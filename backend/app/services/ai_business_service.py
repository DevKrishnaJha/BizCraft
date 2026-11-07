import json
import os
import re
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx
from groq import AsyncGroq


class GroqNotConfigured(Exception):
    pass


class GroqInvalidMapsUrl(Exception):
    pass


class GroqServiceError(Exception):
    pass


GOOGLE_DOMAINS = {"google.com", "google.co.in"}
SHORT_GOOGLE_HOSTS = {"maps.app.goo.gl", "goo.gl", "share.google"}
ALLOWED_REDIRECT_STATUSES = {301, 302, 303, 307, 308}
MAX_REDIRECTS = 5
MAX_URL_LENGTH = 2000

HTTP_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=5.0,
    pool=5.0,
)


def _validate_google_maps_url(url: str):
    if not isinstance(url, str):
        raise GroqInvalidMapsUrl("Google Maps URL must be a string.")

    url = url.strip()

    if not url or len(url) > MAX_URL_LENGTH:
        raise GroqInvalidMapsUrl("Invalid Google Maps URL.")

    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        port = parsed.port
    except ValueError as error:
        raise GroqInvalidMapsUrl("Malformed Google Maps URL.") from error

    is_google_host = (
        hostname in SHORT_GOOGLE_HOSTS
        or hostname in GOOGLE_DOMAINS
        or any(
            hostname.endswith("." + domain)
            for domain in GOOGLE_DOMAINS
        )
    )

    if parsed.scheme.lower() != "https" or not is_google_host:
        raise GroqInvalidMapsUrl(
            "Please provide a valid HTTPS Google Maps link."
        )

    if parsed.username or parsed.password:
        raise GroqInvalidMapsUrl(
            "Google Maps links containing credentials are not accepted."
        )

    if port not in (None, 443):
        raise GroqInvalidMapsUrl("Unexpected URL port.")

    return parsed


async def _resolve_short_google_url(url: str) -> str:
    """
    Resolve Google-owned short links only.
    Every redirect destination is validated before it is requested.
    If resolution fails, keep the original URL so browser search can
    still attempt to identify the listing from the supplied link.
    """
    parsed = _validate_google_maps_url(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")

    if hostname not in SHORT_GOOGLE_HOSTS:
        return url

    current_url = url

    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            follow_redirects=False,
            headers={"User-Agent": "BizCraft/1.0"},
        ) as client:
            for _ in range(MAX_REDIRECTS):
                response = await client.get(current_url)

                if response.status_code not in ALLOWED_REDIRECT_STATUSES:
                    response.raise_for_status()
                    return str(response.url)

                location = response.headers.get("location")

                if not location:
                    return current_url

                next_url = urljoin(current_url, location)
                _validate_google_maps_url(next_url)
                current_url = next_url

    except (httpx.HTTPError, GroqInvalidMapsUrl):
        return url

    return current_url


def _extract_maps_context(url: str) -> dict:
    parsed = _validate_google_maps_url(url)
    query_parameters = parse_qs(parsed.query)

    business_name = ""

    for key in ("query", "q"):
        values = query_parameters.get(key, [])
        if values and values[0].strip():
            business_name = values[0].strip()
            break

    if not business_name:
        for marker in ("/maps/place/", "/maps/search/"):
            if marker in parsed.path:
                raw_name = (
                    parsed.path.split(marker, 1)[1]
                    .split("/", 1)[0]
                )
                business_name = unquote(
                    raw_name.replace("+", " ")
                ).strip()
                if business_name:
                    break

    # Prefer the place pin coordinates (!3dLAT!4dLON) over the
    # map viewport coordinates (@LAT,LON).
    coordinates = None
    coordinate_patterns = [
        r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)",
        r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
    ]

    for pattern in coordinate_patterns:
        match = re.search(pattern, url)
        if not match:
            continue

        latitude = float(match.group(1))
        longitude = float(match.group(2))

        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            coordinates = {
                "latitude": latitude,
                "longitude": longitude,
            }
            break

    place_id_match = re.search(r"!1s([^!/?]+)", url)
    place_id = (
        unquote(place_id_match.group(1))
        if place_id_match
        else None
    )

    return {
        "business_name_hint": business_name[:200] or None,
        "coordinates": coordinates,
        "google_maps_place_id": place_id,
    }


def _extract_json_object(content: str) -> dict:
    """
    Extract the first complete JSON object from model output.
    This tolerates surrounding whitespace or accidental Markdown fences,
    without attempting to repair malformed JSON.
    """
    if not isinstance(content, str) or not content.strip():
        raise GroqServiceError("Groq returned an empty response.")

    start = content.find("{")
    if start < 0:
        raise GroqServiceError(
            "Groq did not return the required JSON business record."
        )

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(content)):
        character = content[index]

        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue

        if character == '"':
            in_string = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1

            if depth == 0:
                try:
                    result = json.loads(content[start:index + 1])
                except json.JSONDecodeError as error:
                    raise GroqServiceError(
                        "Groq returned malformed JSON."
                    ) from error

                if not isinstance(result, dict):
                    raise GroqServiceError(
                        "Groq returned an invalid business object."
                    )

                return result

    raise GroqServiceError(
        "Groq returned incomplete JSON."
    )


def _clean_string(value):
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return None


def _clean_sources(value) -> list[dict]:
    if not isinstance(value, list):
        return []

    sources = []
    seen_urls = set()

    for source in value:
        if not isinstance(source, dict):
            continue

        title = _clean_string(source.get("title")) or "Business information source"
        url = _clean_string(source.get("url"))

        if not url:
            continue

        try:
            parsed = urlparse(url)
        except ValueError:
            continue

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue

        normalized_url = parsed.geturl()

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)

        fields = source.get("fields", [])
        if not isinstance(fields, list):
            fields = []

        sources.append({
            "title": title,
            "url": normalized_url,
            "fields": [
                field.strip()
                for field in fields
                if isinstance(field, str) and field.strip()
            ],
        })

    return sources[:8]


async def search_and_structure_business(maps_url: str) -> dict:
    """
    Use Groq's hosted Browser Search tool to identify a Google Maps
    business listing, research public business details, and return
    a validated structure for BizCraft's onboarding form.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        raise GroqNotConfigured(
            "GROQ_API_KEY is missing from backend/.env"
        )

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b",
    ).strip()

    supported_models = {
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    }

    if model not in supported_models:
        raise GroqServiceError(
            "Groq Browser Search requires GROQ_MODEL to be "
            "openai/gpt-oss-20b or openai/gpt-oss-120b."
        )

    original_url = maps_url.strip()
    _validate_google_maps_url(original_url)

    resolved_url = await _resolve_short_google_url(original_url)
    context = _extract_maps_context(resolved_url)

    # Include both the original and resolved URLs. This is useful when
    # Google redirects a short share link to a full Maps listing.
    search_context = {
        **context,
        "original_google_maps_url": original_url,
        "resolved_google_maps_url": resolved_url,
    }

    system_prompt = """
You are BizCraft's business research and information extraction agent.

You MUST use the available browser_search tool to research the exact
business identified by the supplied Google Maps URL.

IDENTITY AND MATCHING RULES:
- Identify the exact business, not merely a similarly named business.
- Use the business name, Google Maps URL, place ID, and coordinates
  together when those details are available.
- Search the exact business name with its location or coordinates.
- If multiple businesses have similar names, compare their addresses
  and locations before choosing.
- Never substitute a nearby or similarly named business.
- If the exact business cannot be identified confidently, return
  status "no_match" or "ambiguous". Do not guess.

FACTUAL RULES:
- Use only information supported by pages you actually found.
- Never invent phone numbers, email addresses, websites, services,
  opening hours, addresses, or descriptions.
- Do not infer that a service is offered merely because it is common
  for that business category.
- Use the business's official website or official public listing
  when available. Other reputable public listings may support details
  when an official source is unavailable.
- If sources disagree, prefer the official source and leave uncertain
  fields null.
- Missing or unverified fields must be null.
- Services must be an array of strings. Use [] if none are verified.
- Do not include personal information about private individuals.
- Return one JSON object only. No Markdown and no text outside JSON.

OUTPUT SCHEMA:
{
  "status": "success | no_match | ambiguous",
  "confidence": "high | medium | low",
  "business_name": null,
  "category": null,
  "location": null,
  "phone": null,
  "email": null,
  "website": null,
  "description": null,
  "services": [],
  "opening_hours": null,
  "sources": [
    {
      "title": "Source page title",
      "url": "https://exact-source-url",
      "fields": ["business_name", "location"]
    }
  ],
  "reason": "Short explanation of how the business was identified"
}

Only set status to "success" when the exact business identity is
supported by the search results and at least one real source URL is
included. Use "ambiguous" when plausible matches cannot be separated.
Use "no_match" when the exact business cannot be found.
"""

    user_prompt = (
        "Research this business using browser search. Identify the exact "
        "Google Maps listing first, then collect only verifiable public "
        "business information.\n\n"
        "Google Maps context:\n"
        + json.dumps(search_context, ensure_ascii=False)
        + "\n\n"
        "Search for the exact business name and location. Use the supplied "
        "coordinates to distinguish nearby businesses. Return the required "
        "JSON object with source URLs."
    )

    client = AsyncGroq(api_key=api_key)

    try:
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            tools=[
                {
                    "type": "browser_search",
                }
            ],
            tool_choice="required",
            temperature=1,
            top_p=1,
            max_completion_tokens=3500,
            stream=False,
            reasoning_effort="low",
        )

        if not completion.choices:
            raise GroqServiceError(
                "Groq returned no completion choices."
            )

        content = completion.choices[0].message.content
        result = _extract_json_object(content)

    except GroqServiceError:
        raise
    except Exception as error:
        raise GroqServiceError(
            "Groq Browser Search failed. Check the API key, model access, "
            "network connection, and Groq rate limits."
        ) from error
    finally:
        await client.close()

    status_value = result.get("status")
    if status_value not in {"success", "no_match", "ambiguous"}:
        status_value = "no_match"

    confidence = result.get("confidence")
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    sources = _clean_sources(result.get("sources"))

    if status_value == "success" and (
        confidence == "low" or not sources
    ):
        status_value = "ambiguous"

    services = result.get("services", [])
    if not isinstance(services, list):
        services = []

    services = [
        service.strip()
        for service in services
        if isinstance(service, str) and service.strip()
    ][:30]

    business = {
        "business_name": _clean_string(result.get("business_name")),
        "category": _clean_string(result.get("category")),
        "location": _clean_string(result.get("location")),
        "phone": _clean_string(result.get("phone")),
        "email": _clean_string(result.get("email")),
        "website": _clean_string(result.get("website")),
        "google_maps_url": original_url,
        "description": _clean_string(result.get("description")),
        "services": services,
        "opening_hours": _clean_string(result.get("opening_hours")),
    }

    if status_value == "success" and not business["business_name"]:
        status_value = "no_match"

    if status_value != "success":
        return {
            "status": status_value,
            "business": None,
            "sources": sources,
            "confidence": confidence,
            "message": (
                _clean_string(result.get("reason"))
                or "BizCraft could not confidently identify this business."
            ),
        }

    return {
        "status": "success",
        "business": business,
        "sources": sources,
        "confidence": confidence,
        "message": "Business information researched successfully.",
    }
