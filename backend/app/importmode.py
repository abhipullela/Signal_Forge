import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()



# ============================================
# 1. READ CSV
# ============================================

df = pd.read_csv("reddit_info.csv")

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
    # 4. PREPARE UNIQUE COMMUNITIES
    # ========================================

    communities = (
        df[
            ["subreddit.id", "subreddit.name"]
        ]
        .drop_duplicates(subset=["subreddit.id"])
    )

    community_data = []

    for _, row in communities.iterrows():

        subreddit_id = str(row["subreddit.id"])
        subreddit_name = str(row["subreddit.name"])

        community_data.append(
            (
                source_id,
                subreddit_id,
                subreddit_name
            )
        )

    print(f"Found {len(community_data)} unique communities")


    # ========================================
    # 5. INSERT COMMUNITIES IN BATCH
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

    print("Communities inserted successfully")


    # ========================================
    # 6. GET COMMUNITY IDs
    # ========================================

    cursor.execute("""
        SELECT id, external_id
        FROM communities
        WHERE source_id = %s;
    """, (source_id,))

    community_rows = cursor.fetchall()

    community_map = {
        str(external_id): community_id
        for community_id, external_id in community_rows
    }

    print("Community IDs loaded")


    # ========================================
    # 7. PREPARE POSTS
    # ========================================

    post_data = []

    for _, row in df.iterrows():

        subreddit_id = str(row["subreddit.id"])

        community_id = community_map.get(subreddit_id)

        if community_id is None:
            continue

        # Handle missing values

        title = None if pd.isna(row["title"]) else str(row["title"])

        content = None if pd.isna(row["selftext"]) else str(row["selftext"])

        permalink = None if pd.isna(row["permalink"]) else str(row["permalink"])

        url = None if pd.isna(row["url"]) else str(row["url"])

        domain = None if pd.isna(row["domain"]) else str(row["domain"])

        score = None if pd.isna(row["score"]) else int(row["score"])


        # Convert Unix timestamp to PostgreSQL timestamp

        if pd.isna(row["created_utc"]):
            published_at = None
        else:
            published_at = pd.to_datetime(
                row["created_utc"],
                unit="s",
                utc=True
            )


        post_data.append(
            (
                source_id,
                community_id,
                str(row["id"]),
                title,
                content,
                published_at,
                permalink,
                url,
                domain,
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
    print("IMPORT COMPLETED SUCCESSFULLY!")
    print("===================================")


except Exception as e:

    connection.rollback()

    print("\nIMPORT FAILED")
    print("Error:", e)


finally:

    cursor.close()
    connection.close()

    print("Database connection closed")
