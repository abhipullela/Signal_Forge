"""Database loaders for SignalForge."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_PSSWRD = os.getenv("DB_PSSWRD")


def connect_to_database():
    """Connect to the SignalForge PostgreSQL database."""

    if not DATABASE_URL:
        raise RuntimeError(
            f"DATABASE_URL was not found.\n"
            f"Make sure {ENV_FILE} exists and contains:\n"
            f"DATABASE_URL=..."
        )

    conn = psycopg.connect(
        DATABASE_URL,
        password=DATABASE_PSSWRD,
    )

    print("Connected to Neon PostgreSQL!")

    return conn


def load_posts(conn):
    """Load posts and metadata from PostgreSQL."""

    query = """
        SELECT
            post_id,
            platform,
            text,
            author_id,
            community,
            created_at,
            url,
            domain,
            true_topic
        FROM posts
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    print(f"Loaded {len(rows)} posts from PostgreSQL")

    posts = [
        {
            "post_id": row[0],
            "platform": row[1],
            "text": row[2],
            "author_id": row[3],
            "community": row[4],
            "created_at": row[5],
            "url": row[6],
            "domain": row[7],
            "true_topic": row[8],
        }
        for row in rows
    ]

    return posts, rows