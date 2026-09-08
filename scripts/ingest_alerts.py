import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def main():
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    db_url = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ['POSTGRES_DB']}?sslmode=require"
    engine = create_engine(db_url)
    print("Loading alerts.csv...")
    df_alerts = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'alerts.csv'))
    df_alerts.to_sql("alerts", engine, if_exists="replace", index=False)
    print("Uploaded alerts.csv to alerts table.")

if __name__ == '__main__':
    main()
