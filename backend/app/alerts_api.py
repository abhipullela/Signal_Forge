from fastapi import FastAPI, HTTPException
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Signal Forge Alerts API",
    description="API for Signal Forge generated alerts",
    version="1.0.0"
)


# ============================================
# DATABASE CONNECTION
# ============================================

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )


# ============================================
# HOME
# ============================================

@app.get("/")
def home():
    return {
        "message": "Signal Forge Alerts API is running"
    }


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/api/alerts/health")
def alerts_health():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM alerts
        """)

        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return {
            "status": "connected",
            "alerts_rows": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# GET ALL ALERTS
# ============================================

@app.get("/api/alerts")
def get_alerts():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM alerts
            ORDER BY signal_score DESC
        """)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        connection.close()

        alerts = []

        for row in rows:
            alert = dict(zip(columns, row))
            alerts.append(alert)

        return {
            "count": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# GET ALERT BY ALERT ID
# ============================================

@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: str):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM alerts
            WHERE alert_id = %s
        """, (alert_id,))

        row = cursor.fetchone()

        if row is None:
            cursor.close()
            connection.close()

            raise HTTPException(
                status_code=404,
                detail="Alert not found"
            )

        columns = [desc[0] for desc in cursor.description]

        alert = dict(zip(columns, row))

        cursor.close()
        connection.close()

        return alert

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# GET HIGH PRIORITY ALERTS
# ============================================

@app.get("/api/alerts/high")
def get_high_alerts():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM alerts
            WHERE signal_status = 'HIGH'
            ORDER BY signal_score DESC
        """)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        connection.close()

        alerts = []

        for row in rows:
            alerts.append(dict(zip(columns, row)))

        return {
            "count": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# GET ALERT SUMMARY
# ============================================

@app.get("/api/alerts/summary")
def alerts_summary():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_alerts,
                COUNT(*) FILTER (
                    WHERE signal_status = 'HIGH'
                ) AS high_alerts,
                COUNT(*) FILTER (
                    WHERE signal_status = 'MEDIUM'
                ) AS medium_alerts,
                COUNT(*) FILTER (
                    WHERE signal_status = 'LOW'
                ) AS low_alerts,
                AVG(signal_score) AS average_signal_score,
                AVG(propagation_score) AS average_propagation_score,
                AVG(risk_score) AS average_risk_score
            FROM alerts
        """)

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        return {
            "total_alerts": row[0],
            "high_alerts": row[1],
            "medium_alerts": row[2],
            "low_alerts": row[3],
            "average_signal_score": row[4],
            "average_propagation_score": row[5],
            "average_risk_score": row[6]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )