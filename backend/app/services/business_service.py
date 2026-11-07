import json
import uuid
from datetime import datetime, timezone

from app.core.database import get_connection
from app.schemas.business import BusinessCreate


def create_business(data: BusinessCreate):
    business_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO businesses (
                id,
                business_name,
                category,
                location,
                phone,
                email,
                website,
                google_maps_url,
                description,
                services,
                opening_hours,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                business_id,
                data.business_name,
                data.category,
                data.location,
                data.phone,
                data.email,
                data.website,
                data.google_maps_url,
                data.description,
                json.dumps(data.services),
                data.opening_hours,
                created_at,
            ),
        )
        connection.commit()

    return get_business(business_id)


def get_business(business_id: str):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM businesses WHERE id = ?",
            (business_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["services"] = json.loads(result["services"])
    return result


def get_all_businesses():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM businesses
            ORDER BY created_at DESC
            """
        ).fetchall()

    results = []

    for row in rows:
        result = dict(row)
        result["services"] = json.loads(result["services"])
        results.append(result)

    return results


def delete_business(business_id: str) -> bool:
    """Delete one business row. Returns False when it does not exist."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM businesses WHERE id = ?",
            (business_id,),
        )
        connection.commit()
        return cursor.rowcount > 0