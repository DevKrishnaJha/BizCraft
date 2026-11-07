import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "bizcraft.db"


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_india_date() -> str:
    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).date().isoformat()


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                website TEXT,
                google_maps_url TEXT,
                description TEXT,
                services TEXT NOT NULL DEFAULT '[]',
                opening_hours TEXT,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS lookup_usage (
                ip_address TEXT NOT NULL,
                usage_date TEXT NOT NULL,
                request_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (ip_address, usage_date)
            )
        """)

        connection.commit()


def reserve_lookup(
    ip_address: str,
    daily_limit: int = 10,
) -> str | None:
    """
    Atomically reserve one lookup for this IP and India date.

    Returns the usage date when reserved.
    Returns None when the daily limit has been reached.
    """

    usage_date = get_india_date()
    connection = get_connection()

    try:
        # Prevent two simultaneous requests from both passing
        # the limit check.
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute(
            """
            SELECT request_count
            FROM lookup_usage
            WHERE ip_address = ? AND usage_date = ?
            """,
            (ip_address, usage_date),
        ).fetchone()

        current_count = (
            row["request_count"]
            if row is not None
            else 0
        )

        if current_count >= daily_limit:
            connection.rollback()
            return None

        if row is None:
            connection.execute(
                """
                INSERT INTO lookup_usage (
                    ip_address,
                    usage_date,
                    request_count
                )
                VALUES (?, ?, 1)
                """,
                (ip_address, usage_date),
            )
        else:
            connection.execute(
                """
                UPDATE lookup_usage
                SET request_count = request_count + 1
                WHERE ip_address = ? AND usage_date = ?
                """,
                (ip_address, usage_date),
            )

        connection.commit()
        return usage_date

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def release_lookup(
    ip_address: str,
    usage_date: str,
) -> None:
    """Release a reserved lookup after a failed provider request."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE lookup_usage
            SET request_count = MAX(request_count - 1, 0)
            WHERE ip_address = ? AND usage_date = ?
            """,
            (ip_address, usage_date),
        )
        connection.commit()

    finally:
        connection.close()