import pandas as pd
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

def ingest_data():
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Check for required variables
    if not os.getenv("POSTGRES_HOST"):
        print("Error: Missing POSTGRES_HOST in .env")
        return

    csv_path = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'ml_output.csv')
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    print("Loading CSV data...")
    df = pd.read_csv(csv_path)
    
    # Rename columns to match the expected database schema
    if 'semantic_cluster_status' in df.columns:
        df.rename(columns={'semantic_cluster_status': 'signal_status'}, inplace=True)
    if 'semantic_cluster_score' in df.columns and 'signal_score' not in df.columns:
        df.rename(columns={'semantic_cluster_score': 'signal_score'}, inplace=True)
        
    # Replace NaN with None for database insertion
    df = df.where(pd.notnull(df), None)

    print("Connecting to Neon Postgres...")
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )
    
    cur = conn.cursor()

    print("Creating ml_results table if it doesn't exist...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ml_results (
        post_id INTEGER PRIMARY KEY,
        source_id INTEGER,
        community_id INTEGER,
        external_id TEXT,
        title TEXT,
        content TEXT,
        published_at TIMESTAMP,
        permalink TEXT,
        url TEXT,
        domain TEXT,
        score NUMERIC,
        cluster_id INTEGER,
        cluster_size INTEGER,
        cluster_rank INTEGER,
        signal_score NUMERIC,
        signal_status TEXT
    );
    """
    cur.execute(create_table_query)
    conn.commit()

    print("Clearing existing data from ml_results...")
    cur.execute("TRUNCATE TABLE ml_results;")
    conn.commit()

    print(f"Inserting {len(df)} rows into ml_results...")
    
    insert_query = """
    INSERT INTO ml_results (
        post_id, source_id, community_id, external_id, title, content, 
        published_at, permalink, url, domain, score, cluster_id, 
        cluster_size, cluster_rank, signal_score, signal_status
    ) VALUES (
        %(post_id)s, %(source_id)s, %(community_id)s, %(external_id)s, %(title)s, %(content)s,
        %(published_at)s, %(permalink)s, %(url)s, %(domain)s, %(score)s, %(cluster_id)s,
        %(cluster_size)s, %(cluster_rank)s, %(signal_score)s, %(signal_status)s
    )
    """
    
    records = df.to_dict('records')
    psycopg2.extras.execute_batch(cur, insert_query, records)
    conn.commit()

    print("Data ingestion complete!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    ingest_data()
