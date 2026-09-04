import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. READ CSV
# ============================================

df = pd.read_csv("technology.csv")

print(f"Loaded {len(df)} rows from CSV")


# ============================================
# 2. CONNECT TO NEON POSTGRESQL
# ============================================

connection = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    sslmode="require"
)

cursor = connection.cursor()

print("Connected to PostgreSQL")


try:

    # ========================================
    # 3. INSERT / GET REDDIT SOURCE
    # ========================================

    cursor.execute("""
        INSERT INTO sources (source_name)
        VALUES ('Reddit')
        ON CONFLICT (source_name) DO NOTHING;
    """)

    cursor.execute("""
        SELECT id
        FROM sources
        WHERE source_name = 'Reddit';
    """)

    source_id = cursor.fetchone()[0]

    print(f"Reddit source_id = {source_id}")


    # ========================================
    # 4. PREPARE TECHNOLOGY COMMUNITY
    # ========================================

    # This CSV contains only r/technology posts,
    # so the subreddit name is assigned directly.

    subreddit_id = "technology"
    subreddit_name = "technology"

    community_data = [
        (
            source_id,
            subreddit_id,
            subreddit_name
        )
    ]

    print("Found 1 unique community: technology")


    # ========================================
    # 5. INSERT COMMUNITY
    # ========================================

    execute_values(
        cursor,
        """
        INSERT INTO communities
            (source_id, external_id, name)
        VALUES %s
        ON CONFLICT (source_id, external_id)
        DO UPDATE SET name = EXCLUDED.name
        """,
        community_data
    )

    connection.commit()

    print("Community inserted successfully")


    # ========================================
    # 6. GET COMMUNITY ID
    # ========================================

    cursor.execute("""
        SELECT id
        FROM communities
        WHERE source_id = %s
        AND external_id = %s;
    """, (source_id, subreddit_id))

    result = cursor.fetchone()

    if result is None:
        raise Exception("Technology community was not found in database.")

    community_id = result[0]

    print(f"Technology community_id = {community_id}")


    # ========================================
    # 7. PREPARE POSTS
    # ========================================

    post_data = []

    for _, row in df.iterrows():

        # ------------------------------------
        # Title
        # ------------------------------------

        title = (
            None
            if pd.isna(row["title"])
            else str(row["title"])
        )


        # ------------------------------------
        # Body
        # ------------------------------------

        content = (
            None
            if pd.isna(row["body"])
            else str(row["body"])
        )


        # ------------------------------------
        # URL
        # ------------------------------------

        url = (
            None
            if pd.isna(row["url"])
            else str(row["url"])
        )


        # ------------------------------------
        # Score
        # ------------------------------------

        score = (
            None
            if pd.isna(row["score"])
            else int(row["score"])
        )


        # ------------------------------------
        # Timestamp
        # ------------------------------------

        if pd.isna(row["created"]):

            published_at = None

        else:

            published_at = pd.to_datetime(
                row["created"],
                unit="s",
                utc=True
            )


        # ------------------------------------
        # Prepare post
        # ------------------------------------

        post_data.append(
            (
                source_id,
                community_id,
                str(row["id"]),
                title,
                content,
                published_at,
                None,       # permalink
                url,
                None,       # domain
                score
            )
        )


    print(f"Prepared {len(post_data)} posts")


    # ========================================
    # 8. INSERT POSTS IN BATCHES
    # ========================================

    batch_size = 1000

    for i in range(0, len(post_data), batch_size):

        batch = post_data[i:i + batch_size]

        execute_values(
            cursor,
            """
            INSERT INTO posts (
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
            )
            VALUES %s
            ON CONFLICT (source_id, external_id)
            DO NOTHING
            """,
            batch
        )

        connection.commit()

        print(
            f"Inserted {min(i + batch_size, len(post_data))}"
            f" / {len(post_data)} posts"
        )


    # ========================================
    # 9. FINISHED
    # ========================================

    print("\n===================================")
    print("TECHNOLOGY IMPORT COMPLETED!")
    print("===================================")


except Exception as e:

    connection.rollback()

    print("\nIMPORT FAILED")
    print("Error:", e)


finally:

    cursor.close()
    connection.close()

    print("Database connection closed")