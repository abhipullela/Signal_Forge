import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv


# ============================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    sslmode="require"
)

print("Connected to PostgreSQL")


# ============================================
# 2. READ ML OUTPUT CSV
# ============================================

import os
csv_file = os.path.join(os.path.dirname(__file__), "../../outputs/ml_output.csv")

df = pd.read_csv(csv_file)

print(f"Loaded {len(df)} rows from CSV")


# ============================================
# 3. CHECK CSV COLUMNS
# ============================================

print("Checking CSV columns...")

required_columns = [
    "post_id",
    "source_id",
    "community_id",
    "external_id",
    "title",
    "content",
    "published_at",
    "permalink",
    "url",
    "domain",
    "score",
    "cluster_id",
    "cluster_size",
    "metric_num_posts",
    "metric_num_clusters",
    "metric_num_clustered_points",
    "metric_num_noise_points",
    "metric_noise_percentage",
    "metric_smallest_cluster",
    "metric_largest_cluster",
    "metric_silhouette",
    "metric_davies_bouldin",
    "metric_calinski_harabasz",
    "cluster_rank",
    "signal_score",
    "signal_status"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("ERROR: These columns are missing from the CSV:")
    print(missing_columns)

    connection.close()
    exit()


print("CSV columns verified successfully")


# ============================================
# 4. CLEAN DATA
# ============================================

# Convert NaN values to None
df = df.where(pd.notnull(df), None)

# Convert published_at to proper datetime
df["published_at"] = pd.to_datetime(
    df["published_at"],
    errors="coerce",
    utc=True
)

# Convert NaT back to None
df["published_at"] = df["published_at"].where(
    df["published_at"].notna(),
    None
)

print("Data cleaned successfully")


# ============================================
# 5. CREATE CURSOR
# ============================================

cursor = connection.cursor()


# ============================================
# 6. DELETE OLD ML RESULTS TABLE
# ============================================

print("Removing old ml_results table if it exists...")

cursor.execute("""
DROP TABLE IF EXISTS ml_results
""")

connection.commit()

print("Old ml_results table removed")


# ============================================
# 7. CREATE NEW ML RESULTS TABLE
# ============================================

print("Creating ml_results table...")

cursor.execute("""
CREATE TABLE ml_results (

    id SERIAL PRIMARY KEY,

    post_id INTEGER,
    source_id INTEGER,
    community_id INTEGER,

    external_id TEXT,

    title TEXT,
    content TEXT,

    published_at TIMESTAMPTZ,

    permalink TEXT,
    url TEXT,
    domain TEXT,

    score INTEGER,

    cluster_id INTEGER,
    cluster_size INTEGER,

    metric_num_posts DOUBLE PRECISION,
    metric_num_clusters DOUBLE PRECISION,
    metric_num_clustered_points DOUBLE PRECISION,
    metric_num_noise_points DOUBLE PRECISION,
    metric_noise_percentage DOUBLE PRECISION,
    metric_smallest_cluster DOUBLE PRECISION,
    metric_largest_cluster DOUBLE PRECISION,
    metric_silhouette DOUBLE PRECISION,
    metric_davies_bouldin DOUBLE PRECISION,
    metric_calinski_harabasz DOUBLE PRECISION,

    cluster_rank INTEGER,

    signal_score DOUBLE PRECISION,
    signal_status TEXT,

    UNIQUE(post_id)
)
""")

connection.commit()

print("ml_results table created successfully")


# ============================================
# 8. PREPARE DATA
# ============================================

columns = [
    "post_id",
    "source_id",
    "community_id",
    "external_id",
    "title",
    "content",
    "published_at",
    "permalink",
    "url",
    "domain",
    "score",
    "cluster_id",
    "cluster_size",
    "metric_num_posts",
    "metric_num_clusters",
    "metric_num_clustered_points",
    "metric_num_noise_points",
    "metric_noise_percentage",
    "metric_smallest_cluster",
    "metric_largest_cluster",
    "metric_silhouette",
    "metric_davies_bouldin",
    "metric_calinski_harabasz",
    "cluster_rank",
    "signal_score",
    "signal_status"
]


data = [
    tuple(row[column] for column in columns)
    for _, row in df.iterrows()
]

print(f"Prepared {len(data)} rows for insertion")


# ============================================
# 9. INSERT QUERY
# ============================================

insert_query = """
INSERT INTO ml_results (
    post_id,
    source_id,
    community_id,
    external_id,
    title,
    content,
    published_at,
    permalink,
    url,
    domain,
    score,
    cluster_id,
    cluster_size,
    metric_num_posts,
    metric_num_clusters,
    metric_num_clustered_points,
    metric_num_noise_points,
    metric_noise_percentage,
    metric_smallest_cluster,
    metric_largest_cluster,
    metric_silhouette,
    metric_davies_bouldin,
    metric_calinski_harabasz,
    cluster_rank,
    signal_score,
    signal_status
)

VALUES %s
"""


# ============================================
# 10. INSERT DATA IN BATCHES
# ============================================

batch_size = 1000

print("Starting database insertion...")

for i in range(0, len(data), batch_size):

    batch = data[i:i + batch_size]

    execute_values(
        cursor,
        insert_query,
        batch
    )

    connection.commit()

    processed = min(i + batch_size, len(data))

    print(
        f"Inserted {processed} / {len(data)} rows"
    )


# ============================================
# 11. VERIFY DATABASE
# ============================================

cursor.execute("""
SELECT COUNT(*)
FROM ml_results
""")

count = cursor.fetchone()[0]

print()
print("============================================")
print("DATABASE VERIFICATION")
print("============================================")
print(f"Rows in ml_results: {count}")
print("============================================")


# ============================================
# 12. VERIFY COMMUNITIES
# ============================================

cursor.execute("""
SELECT community_id, COUNT(*)
FROM ml_results
GROUP BY community_id
ORDER BY community_id
""")

community_results = cursor.fetchall()

print()
print("Rows by community:")

for community_id, row_count in community_results:
    print(
        f"Community {community_id}: {row_count} rows"
    )


# ============================================
# 13. CLOSE CONNECTION
# ============================================

cursor.close()
connection.close()

print()
print("============================================")
print("ML OUTPUT IMPORT COMPLETED SUCCESSFULLY!")
print("============================================")