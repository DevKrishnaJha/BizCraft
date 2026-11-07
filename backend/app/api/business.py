import io
import json
import re
import zipfile
import shutil
import uuid

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas.business import BusinessCreate, BusinessResponse
from app.schemas.maps_lookup import MapsLookupRequest

from app.services.business_service import (
    create_business,
    get_business,
    get_all_businesses,
    delete_business,
)

from app.core.database import reserve_lookup, release_lookup

from app.services.ai_business_service import (
    search_and_structure_business,
    GroqNotConfigured,
    GroqInvalidMapsUrl,
    GroqServiceError,
)

from app.services.analysis_service import analyze_business
from app.services.blueprint_service import (
    build_website_blueprint,
    DESIGN_SYSTEMS,
)

from app.generators.static_generator import (
    generate_static_website,
    PROJECTS_DIR,
)


router = APIRouter(
    prefix="/api/businesses",
    tags=["Businesses"],
)


# --------------------------------------------------
# Business CRUD
# --------------------------------------------------

@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_business(data: BusinessCreate):
    return create_business(data)


@router.get("", response_model=list[BusinessResponse])
def list_businesses():
    return get_all_businesses()


@router.get("/{business_id}", response_model=BusinessResponse)
def retrieve_business(business_id: str):
    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business

@router.delete("/{business_id}")
def delete_business_profile(business_id: str):
    """Delete the business record and its generated website directory."""

    if not _safe_business_id(business_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID.",
        )

    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found.",
        )

    projects_root = PROJECTS_DIR.resolve()
    project_path = projects_root / business_id
    resolved_project = project_path.resolve()

    if not resolved_project.is_relative_to(projects_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project path.",
        )

    # Temporarily move the generated website folder.
    # If database deletion fails, we can restore it.

    tombstone = projects_root / (
        f".bizcraft-delete-{uuid.uuid4().hex}"
    )

    moved_project = False

    try:
        if project_path.exists() or project_path.is_symlink():
            project_path.rename(tombstone)
            moved_project = True

        deleted = delete_business(business_id)

        if not deleted:
            if moved_project and tombstone.exists():
                tombstone.rename(project_path)

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found.",
            )

    except HTTPException:
        raise

    except Exception as error:
        if moved_project and tombstone.exists():
            try:
                tombstone.rename(project_path)
            except OSError:
                pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Could not delete the business. "
                "Its website files were preserved where possible."
            ),
        ) from error

    cleanup_warning = False

    if moved_project:
        try:
            if tombstone.is_symlink() or tombstone.is_file():
                tombstone.unlink()
            else:
                shutil.rmtree(tombstone)

        except OSError:
            cleanup_warning = True

    return {
        "status": "deleted",
        "business_id": business_id,
        "business_name": business.get("business_name"),
        "cleanup_warning": cleanup_warning,
    }

# --------------------------------------------------
# Shared lookup limit
# --------------------------------------------------

def reserve_business_lookup(request: Request):
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    usage_date = reserve_lookup(
        client_ip,
        daily_limit=10,
    )

    if usage_date is None:
        raise HTTPException(
            status_code=429,
            detail=(
                "Daily business lookup limit reached. "
                "You can make up to 10 lookups per IP address per day."
            ),
        )

    return client_ip, usage_date


def _build_missing_fields(business: dict) -> list[str]:
    fields = (
        "business_name",
        "category",
        "location",
        "phone",
        "email",
        "website",
        "description",
        "services",
        "opening_hours",
    )

    missing = []

    for field in fields:
        value = business.get(field)

        if value is None or value == "":
            missing.append(field)
        elif isinstance(value, list) and not value:
            missing.append(field)

    return missing


async def _run_business_autofill(maps_url: str) -> dict:
    result = await search_and_structure_business(maps_url)

    if result["status"] != "success":
        return {
            "status": result["status"],
            "message": result.get("message")
            or "BizCraft couldn't confidently identify this business.",
            "sources": result.get("sources", []),
            "confidence": result.get("confidence"),
        }

    business = result["business"]

    return {
        "status": "success",
        "business": business,
        "missing_fields": _build_missing_fields(business),
        "source": "Groq Browser Search",
        "sources": result.get("sources", []),
        "confidence": result.get("confidence"),
        "message": result.get("message")
        or "Business information researched successfully.",
    }


# --------------------------------------------------
# Business lookup compatibility endpoint
# --------------------------------------------------

@router.post("/lookup")
async def lookup_business(
    data: MapsLookupRequest,
    request: Request,
):
    client_ip, usage_date = reserve_business_lookup(request)

    try:
        return await _run_business_autofill(data.maps_url)

    except GroqInvalidMapsUrl as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    except GroqNotConfigured as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )

    except GroqServiceError as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    except Exception:
        release_lookup(client_ip, usage_date)
        raise


# --------------------------------------------------
# AI business autofill endpoint
# --------------------------------------------------

@router.post("/autofill")
async def autofill_business(
    data: MapsLookupRequest,
    request: Request,
):
    client_ip, usage_date = reserve_business_lookup(request)

    try:
        return await _run_business_autofill(data.maps_url)

    except GroqInvalidMapsUrl as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    except GroqNotConfigured as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )

    except GroqServiceError as error:
        release_lookup(client_ip, usage_date)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    except Exception:
        release_lookup(client_ip, usage_date)
        raise


# --------------------------------------------------
# Business analysis
# --------------------------------------------------

@router.get("/{business_id}/analysis")
def get_business_analysis(business_id: str):
    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return analyze_business(business)


# --------------------------------------------------
# Website blueprint
# --------------------------------------------------

@router.get("/{business_id}/blueprint")
def get_business_blueprint(business_id: str):
    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return build_website_blueprint(business)


# --------------------------------------------------
# Website generation
# --------------------------------------------------

@router.post("/{business_id}/generate")
def generate_business_website(
    business_id: str,
    design_id: str | None = None,
):
    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    blueprint = build_website_blueprint(business)
    metadata_path = PROJECTS_DIR / business_id / "project.json"

    if design_id is not None:
        if design_id not in DESIGN_SYSTEMS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported design system.",
            )

    else:
        try:
            if metadata_path.is_file():
                metadata = json.loads(
                    metadata_path.read_text(encoding="utf-8")
                )

                saved_design = metadata.get("selected_design_id")

                if saved_design in DESIGN_SYSTEMS:
                    design_id = saved_design

        except (OSError, json.JSONDecodeError):
            pass

    if design_id is None:
        design_id = blueprint["design"]["system_id"]

    selected_design = DESIGN_SYSTEMS[design_id]

    blueprint["design"].update({
        "system_id": design_id,
        "name": selected_design["name"],
        "description": selected_design["description"],
    })

    try:
        return generate_static_website(business, blueprint)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# --------------------------------------------------
# Website ZIP export
# --------------------------------------------------

EXPORT_FILES = (
    ("index.html", "index.html"),
    ("css/style.css", "css/style.css"),
    ("js/script.js", "js/script.js"),
)


def _safe_business_id(business_id: str) -> bool:
    return bool(re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}",
        business_id,
    ))


def _download_filename(business_name: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        business_name.lower(),
    ).strip("-")

    return f"{slug or 'business'}-website.zip"


@router.get("/{business_id}/export")
def export_business_website(business_id: str):
    if not _safe_business_id(business_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID.",
        )

    business = get_business(business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found.",
        )

    projects_root = PROJECTS_DIR.resolve()
    project_dir = (projects_root / business_id).resolve()

    if not project_dir.is_relative_to(projects_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project path.",
        )

    if not project_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generate this website before exporting it.",
        )

    files_to_export = []

    for disk_path, archive_path in EXPORT_FILES:
        target = (project_dir / disk_path).resolve()

        if not target.is_relative_to(project_dir):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid generated file path.",
            )

        if not target.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Website files are incomplete. "
                    "Generate the website again before exporting."
                ),
            )

        files_to_export.append((target, archive_path))

    readme = f"""# {business.get("business_name") or "Business"} Website

This is a standalone static website generated with BizCraft.

## Files

- `index.html` - Website page
- `css/style.css` - Website styling and responsive layout
- `js/script.js` - Navigation menu and small interactive features

## How to preview

1. Extract the ZIP file.
2. Open `index.html` in a modern web browser.

The website does not require BizCraft or a backend server to run.

## Customisation

You can edit the HTML, CSS, and JavaScript files with any code editor.

Note: The website may load fonts from Google Fonts when an internet connection
is available. The layout and system fonts remain available offline.
"""

    memory_file = io.BytesIO()

    try:
        with zipfile.ZipFile(
            memory_file,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=8,
        ) as archive:
            for disk_path, archive_path in files_to_export:
                archive.write(disk_path, arcname=archive_path)

            archive.writestr("README.md", readme)

    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not package the generated website.",
        )

    memory_file.seek(0)

    filename = _download_filename(
        str(business.get("business_name") or "business")
    )

    return StreamingResponse(
        memory_file,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(filename)}"
            ),
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store",
        },
    )


# --------------------------------------------------
# Website preview
# --------------------------------------------------

PREVIEW_FILES = {
    "index.html": ("index.html", "text/html"),
    "css/style.css": ("css/style.css", "text/css"),
    "js/script.js": ("js/script.js", "application/javascript"),
}


@router.get("/{business_id}/preview/{file_path:path}")
def preview_business_website(
    business_id: str,
    file_path: str,
):
    if not _safe_business_id(business_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business ID.",
        )

    file_info = PREVIEW_FILES.get(file_path)

    if file_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview file not found.",
        )

    relative_path, media_type = file_info

    projects_root = PROJECTS_DIR.resolve()
    project_dir = (projects_root / business_id).resolve()
    target_file = (project_dir / relative_path).resolve()

    if not project_dir.is_relative_to(projects_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project path.",
        )

    if not target_file.is_relative_to(project_dir):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid preview path.",
        )

    if not target_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website has not been generated yet.",
        )

    return FileResponse(
        path=target_file,
        media_type=media_type,
        headers={
            "X-Content-Type-Options": "nosniff",
        },
    )