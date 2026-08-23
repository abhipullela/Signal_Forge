"""Database loaders for SignalForge."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    ENV_FILE,
    override=True,
)

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_PSSWRD = os.getenv("DB_PSSWRD")


# ============================================================
# DATABASE CONNECTION
# ============================================================

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


# ============================================================
# LOAD POSTS
# ============================================================

def load_posts(conn):
    """
    Load posts and metadata from PostgreSQL.

    Current posts table schema:

        id
        source_id
        community_id
        external_id
        title
        content
        published_at
        permalink
        url
        domain
        score
    """

    query = """
        SELECT
            id,
            source_id,
            community_id,
            external_id,
            title,
            content,
            published_at,
            permalink,
            url,
            domain,
            score
        FROM posts
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    print(
        f"Loaded {len(rows)} posts from PostgreSQL"
    )

    posts = [
        {
            "post_id": row[0],
            "source_id": row[1],
            "community_id": row[2],
            "external_id": row[3],
            "title": row[4],
            "content": row[5],
            "published_at": row[6],
            "permalink": row[7],
            "url": row[8],
            "domain": row[9],
            "score": row[10],
        }
        for row in rows
    ]

    if posts:
        print("\nFirst post:")
        print(posts[0])

    return posts