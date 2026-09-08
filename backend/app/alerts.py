import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

# ============================================
# 1. CONNECT TO NEON POSTGRESQL
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

# ============================================
# 2. READ ALERTS CSV
# ============================================

import os
csv_path = os.path.join(os.path.dirname(__file__), "../../outputs/alerts.csv")
df = pd.read_csv(csv_path)

print(f"CSV rows: {len(df)}")
print(f"CSV columns: {len(df.columns)}")

# Replace NaN with None so PostgreSQL gets NULL
df = df.where(pd.notnull(df), None)

# ============================================
# 3. DROP OLD ALERTS TABLE
# ============================================

cursor.execute("""
    DROP TABLE IF EXISTS alerts;
""")

# ============================================
# 4. CREATE ALERTS TABLE
# ============================================

cursor.execute("""
    CREATE TABLE alerts (
        id SERIAL PRIMARY KEY,

        alert_id TEXT,
        cluster_id INTEGER,
        time_window TIMESTAMPTZ,

        volume DOUBLE PRECISION,
        engagement DOUBLE PRECISION,
        average_engagement DOUBLE PRECISION,
        community_count DOUBLE PRECISION,
        velocity DOUBLE PRECISION,
        growth_rate DOUBLE PRECISION,
        acceleration DOUBLE PRECISION,
        velocity_log DOUBLE PRECISION,
        acceleration_log DOUBLE PRECISION,
        engagement_velocity DOUBLE PRECISION,
        engagement_growth DOUBLE PRECISION,
        community_velocity DOUBLE PRECISION,

        baseline_volume DOUBLE PRECISION,
        baseline_std DOUBLE PRECISION,
        baseline_available BOOLEAN,

        anomaly_score DOUBLE PRECISION,
        positive_anomaly_score DOUBLE PRECISION,
        above_baseline BOOLEAN,

        persistence_windows DOUBLE PRECISION,
        persistence_score DOUBLE PRECISION,

        positive_growth DOUBLE PRECISION,
        growth_score DOUBLE PRECISION,

        positive_velocity DOUBLE PRECISION,
        velocity_score DOUBLE PRECISION,

        positive_acceleration DOUBLE PRECISION,
        acceleration_score DOUBLE PRECISION,

        log_engagement DOUBLE PRECISION,
        engagement_score DOUBLE PRECISION,
        anomaly_score_normalized DOUBLE PRECISION,
        community_spread_score DOUBLE PRECISION,

        raw_signal_score DOUBLE PRECISION,
        persistence_multiplier DOUBLE PRECISION,
        signal_score DOUBLE PRECISION,
        signal_status TEXT,

        total_posts DOUBLE PRECISION,
        active_windows INTEGER,
        max_volume DOUBLE PRECISION,
        temporal_signal_score DOUBLE PRECISION,

        anomaly DOUBLE PRECISION,
        persistence DOUBLE PRECISION,
        communities DOUBLE PRECISION,
        sources INTEGER,

        first_seen TIMESTAMPTZ,
        last_seen TIMESTAMPTZ,

        cross_community INTEGER,
        cross_source INTEGER,

        duration_hours DOUBLE PRECISION,
        community_spread_rate DOUBLE PRECISION,

        first_community_time TIMESTAMPTZ,
        last_community_time TIMESTAMPTZ,

        communities_adopted INTEGER,
        adoption_duration_hours DOUBLE PRECISION,
        propagation_velocity DOUBLE PRECISION,

        source_count INTEGER,
        cross_source_spread INTEGER,

        recent_community_max INTEGER,
        recent_community_growth DOUBLE PRECISION,
        recent_windows_active INTEGER,

        propagation_score DOUBLE PRECISION,
        propagation_status TEXT,

        risk_type TEXT,
        severity TEXT,
        risk_score DOUBLE PRECISION,
        risk_confidence DOUBLE PRECISION,
        justification TEXT,

        keyword_risk_type TEXT,
        keyword_hits TEXT,
        keyword_score INTEGER,

        content_risk_score DOUBLE PRECISION,
        behavioral_risk_score DOUBLE PRECISION,

        representative_text TEXT,

        alert_priority DOUBLE PRECISION,
        alert_level TEXT,

        source_post_count INTEGER,

        explanation TEXT
    );
""")

# ============================================
# 5. CONVERT TIMESTAMP COLUMNS
# ============================================

timestamp_columns = [
    "time_window",
    "first_seen",
    "last_seen",
    "first_community_time",
    "last_community_time"
]

for column in timestamp_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
        utc=True
    )

# Convert pandas timestamps to Python datetime / None
for column in timestamp_columns:
    df[column] = df[column].apply(
        lambda x: x.to_pydatetime() if pd.notnull(x) else None
    )

# ============================================
# 6. INSERT DATA
# ============================================

columns = list(df.columns)

column_names = ", ".join(f'"{column}"' for column in columns)

values = [
    tuple(row)
    for row in df[columns].itertuples(index=False, name=None)
]

query = f"""
    INSERT INTO alerts ({column_names})
    VALUES %s
"""

execute_values(
    cursor,
    query,
    values,
    page_size=1000
)

connection.commit()

# ============================================
# 7. VERIFY
# ============================================

cursor.execute("""
    SELECT COUNT(*)
    FROM alerts;
""")

count = cursor.fetchone()[0]

print(f"Inserted rows: {count}")

cursor.close()
connection.close()

print("Alerts table created and CSV uploaded successfully!")
