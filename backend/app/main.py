from fastapi import FastAPI, HTTPException
from typing import Optional
import psycopg2
import os
from dotenv import load_dotenv
from app.schemas.post import CommunitySignalsResponse


# ============================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()


# ============================================
# 2. CREATE FASTAPI APP
# ============================================

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Signal Forge API",
    description="Backend API for Signal Forge",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 3. DATABASE CONNECTION
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


def get_db_community_id(community_id: str) -> int:
    cid = str(community_id).lower()
    if cid in ["1", "datasets", "423"]: return 423
    if cid in ["2", "technology", "424"]: return 424
    if cid in ["3", "gaming", "425"]: return 425
    return int(cid) if cid.isdigit() else 423


# ============================================
# 4. HOME / API TEST
# ============================================

@app.get("/")
def home():

    return {
        "message": "Signal Forge API is running"
    }


# ============================================
# 5. DATABASE HEALTH CHECK
# ============================================

@app.get("/api/health")
def health_check():

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM ml_results
        """)

        count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return {
            "status": "connected",
            "ml_results_rows": count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 5b. GET GLOBAL STATS
# ============================================

@app.get("/api/stats")
def get_stats():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM ml_results")
        total_monitored = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ml_results WHERE signal_status IN ('HIGH', 'MEDIUM')")
        active_signals = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        if total_monitored > 1000000:
            formatted_total = f"{total_monitored / 1000000:.1f}M"
        elif total_monitored > 1000:
            formatted_total = f"{total_monitored / 1000:.1f}K"
        else:
            formatted_total = str(total_monitored)

        return {
            "total_monitored": formatted_total,
            "active_signals": active_signals
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 6. GET COMMUNITIES
# ============================================

@app.get("/api/communities")
def get_communities():

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                community_id,
                COUNT(*) AS total_posts,
                COUNT(*) FILTER (WHERE signal_status IN ('HIGH', 'MEDIUM')) AS active_signals,
                ROUND(AVG(signal_score)::numeric, 1) AS average_novelty
            FROM ml_results
            GROUP BY community_id
            ORDER BY community_id
        """)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        communities = []

        for row in rows:

            communities.append({
                "community_id": row[0],
                "total_posts": row[1],
                "active_signals": row[2] or 0,
                "average_novelty": float(row[3]) if row[3] else 0.0
            })

        return {
            "communities": communities
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 7. COMMUNITY OVERVIEW
# ============================================

@app.get("/api/community/{community_id}/overview")
def community_overview(community_id: str):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        db_community_id = get_db_community_id(community_id)

        # ----------------------------------------
        # TOTAL POSTS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM ml_results
            WHERE community_id = %s
        """, (db_community_id,))

        total_posts = cursor.fetchone()[0]


        # ----------------------------------------
        # ACTIVE SIGNALS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM ml_results
            WHERE community_id = %s
            AND signal_status IN ('HIGH','MEDIUM')
        """, (db_community_id,))

        active_signals = cursor.fetchone()[0]


        # ----------------------------------------
        # ACTIVE CLUSTERS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(DISTINCT cluster_id)
            FROM ml_results
            WHERE community_id = %s
            AND cluster_id IS NOT NULL
        """, (db_community_id,))

        active_clusters = cursor.fetchone()[0]


        # ----------------------------------------
        # AVERAGE SIGNAL SCORE
        # ----------------------------------------

        cursor.execute("""
            SELECT ROUND(AVG(signal_score)::numeric, 1)
            FROM ml_results
            WHERE community_id = %s
            AND signal_score IS NOT NULL
        """, (db_community_id,))

        average_signal_score = cursor.fetchone()[0]


        cursor.close()
        connection.close()


        return {
            "community_id": community_id,
            "total_posts_analyzed": total_posts,
            "active_signals": active_signals,
            "active_clusters": active_clusters,
            "average_signal_score": average_signal_score
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 8. GET RECENT SIGNALS
# ============================================

@app.get("/api/community/{community_id}/signals", response_model=CommunitySignalsResponse)
def community_signals(community_id: str):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Map frontend pseudo-IDs to actual DB community IDs
        db_community_id = get_db_community_id(community_id)

        cursor.execute("""
            SELECT
                post_id,
                title,
                cluster_id,
                domain,
                cluster_size,
                cluster_rank,
                ROUND((score::numeric / NULLIF(MAX(score) OVER(), 0)::numeric) * 1000.0) AS signal_score,
                signal_status,
                published_at
            FROM ml_results

            WHERE community_id = %s

            AND score IS NOT NULL

            ORDER BY 
                (CASE 
                    WHEN signal_status = 'HIGH' THEN score * 10.0 
                    WHEN signal_status = 'MEDIUM' THEN score * 2.0 
                    ELSE score 
                END) DESC,
                published_at DESC

            LIMIT 20
        """, (db_community_id,))

        rows = cursor.fetchall()

        # Fallback logic: If no exact match, return top global signals so table is never blank
        if not rows:
            cursor.execute("""
                SELECT
                    post_id,
                    title,
                    cluster_id,
                    domain,
                    cluster_size,
                    cluster_rank,
                    ROUND((score::numeric / NULLIF(MAX(score) OVER(), 0)::numeric) * 1000.0) AS signal_score,
                    signal_status,
                    published_at
                FROM ml_results
                WHERE score IS NOT NULL
                ORDER BY 
                    (CASE 
                        WHEN signal_status = 'HIGH' THEN score * 10.0 
                        WHEN signal_status = 'MEDIUM' THEN score * 2.0 
                        ELSE score 
                    END) DESC,
                    published_at DESC
                LIMIT 20
            """)
            rows = cursor.fetchall()

        cursor.close()
        connection.close()


        signals = []

        for row in rows:

            signals.append({
                "post_id": row[0],
                "title": row[1],
                "cluster_id": row[2],
                "domain": row[3],
                "cluster_size": row[4],
                "cluster_rank": row[5],
                "signal_score": row[6],
                "signal_status": row[7],
                "published_at": row[8].isoformat() if hasattr(row[8], 'isoformat') else str(row[8]) if row[8] else None
            })


        return {
            "community_id": community_id,
            "signals": signals
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 9. GET CLUSTER INFORMATION
# ============================================

@app.get("/api/community/{community_id}/clusters")
def community_clusters(community_id: str):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        db_community_id = get_db_community_id(community_id)

        cursor.execute("""
            SELECT
                cluster_id,
                MAX(cluster_size) AS cluster_size,
                MAX(cluster_rank) AS cluster_rank,
                COUNT(*) AS post_count,
                ROUND(AVG(signal_score)::numeric, 1) AS average_signal_score
            FROM ml_results

            WHERE community_id = %s
            AND cluster_id IS NOT NULL

            GROUP BY cluster_id

            ORDER BY average_signal_score DESC
        """, (db_community_id,))

        rows = cursor.fetchall()

        cursor.close()
        connection.close()


        clusters = []

        for row in rows:

            clusters.append({
                "cluster_id": row[0],
                "cluster_size": row[1],
                "cluster_rank": row[2],
                "post_count": row[3],
                "average_signal_score": row[4]
            })


        return {
            "community_id": community_id,
            "clusters": clusters
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 10. GET SIGNAL DETAILS
# ============================================

@app.get("/api/signal/{post_id}")
def signal_details(post_id: int):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                post_id,
                community_id,
                title,
                content,
                cluster_id,
                cluster_size,
                cluster_rank,
                signal_score,
                signal_status,
                published_at,
                url
            FROM ml_results

            WHERE post_id = %s
        """, (post_id,))

        row = cursor.fetchone()

        cursor.close()
        connection.close()


        if row is None:

            raise HTTPException(
                status_code=404,
                detail="Signal not found"
            )


        return {
            "post_id": row[0],
            "community_id": row[1],
            "title": row[2],
            "content": row[3],
            "cluster_id": row[4],
            "cluster_size": row[5],
            "cluster_rank": row[6],
            "signal_score": row[7],
            "signal_status": row[8],
            "published_at": row[9].isoformat() if hasattr(row[9], 'isoformat') else str(row[9]) if row[9] else None,
            "url": row[10]
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 11. TREND DATA
# ============================================

@app.get("/api/community/{community_id}/trend")
def community_trend(community_id: str, days: Optional[int] = None):

    try:
        from datetime import date, timedelta

        connection = get_connection()
        cursor = connection.cursor()

        db_community_id = get_db_community_id(community_id)

        # Determine full historical date range first
        cursor.execute("""
            SELECT
                MIN(DATE(published_at)),
                MAX(DATE(published_at)),
                COUNT(DISTINCT DATE(published_at))
            FROM ml_results
            WHERE community_id = %s
            AND published_at IS NOT NULL
            AND signal_status IN ('HIGH', 'MEDIUM')
        """, (db_community_id,))

        range_row = cursor.fetchone()
        abs_min_date = range_row[0]
        abs_max_date = range_row[1]
        distinct_days = range_row[2] if range_row and range_row[2] else 1

        if not abs_min_date or not abs_max_date:
            cursor.close()
            connection.close()
            return {"community_id": community_id, "bucket": "day", "trend": []}

        # Apply optional days filter — if provided, clamp window; otherwise use full range
        if days and days > 0:
            from datetime import timedelta
            min_date = max(abs_min_date, abs_max_date - timedelta(days=days - 1))
            max_date = abs_max_date
        else:
            min_date = abs_min_date
            max_date = abs_max_date

        total_span_days = (max_date - min_date).days + 1

        # Adaptive bucket based on the ACTUAL window being displayed
        if total_span_days > 365:
            date_trunc = "month"
        elif total_span_days > 60:
            date_trunc = "week"
        else:
            date_trunc = "day"

        cursor.execute("""
            SELECT
                DATE_TRUNC(%s, published_at)::date AS bucket,
                COUNT(*) AS post_count,
                ROUND(AVG(score)::numeric, 2) AS average_signal_score
            FROM ml_results
            WHERE community_id = %s
            AND published_at IS NOT NULL
            AND signal_status IN ('HIGH', 'MEDIUM')
            AND DATE(published_at) >= %s
            AND DATE(published_at) <= %s
            GROUP BY DATE_TRUNC(%s, published_at)
            ORDER BY bucket ASC
        """, (date_trunc, db_community_id, min_date, max_date, date_trunc))

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        # Build a lookup from actual data
        data_map = {}
        for row in rows:
            bucket_date = row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0])
            data_map[bucket_date] = {
                "post_count": int(row[1]),
                "average_signal_score": float(row[2]) if row[2] is not None else 0.0
            }

        # Fill every bucket in the range with zeros where no data exists
        # so the chart renders as a continuous filled area, not isolated dots
        trend = []
        if date_trunc == "day":
            current = min_date
            while current <= max_date:
                key = current.isoformat()
                trend.append({
                    "date": key,
                    "post_count": data_map.get(key, {}).get("post_count", 0),
                    "average_signal_score": data_map.get(key, {}).get("average_signal_score", 0.0)
                })
                current += timedelta(days=1)

        elif date_trunc == "week":
            # Align to Monday of min_date's week
            current = min_date - timedelta(days=min_date.weekday())
            while current <= max_date:
                key = current.isoformat()
                trend.append({
                    "date": key,
                    "post_count": data_map.get(key, {}).get("post_count", 0),
                    "average_signal_score": data_map.get(key, {}).get("average_signal_score", 0.0)
                })
                current += timedelta(weeks=1)

        else:
            # Monthly — zero-fill every calendar month so index-based tick sampling is clean
            # Without this, gaps cause ticks to land on different months each year
            cur_year = min_date.year
            cur_month = min_date.month
            end_year = max_date.year
            end_month = max_date.month

            while (cur_year, cur_month) <= (end_year, end_month):
                key = f"{cur_year:04d}-{cur_month:02d}-01"
                trend.append({
                    "date": key,
                    "post_count": data_map.get(key, {}).get("post_count", 0),
                    "average_signal_score": data_map.get(key, {}).get("average_signal_score", 0.0)
                })
                # Advance one month cleanly — no timedelta tricks needed
                cur_month += 1
                if cur_month > 12:
                    cur_month = 1
                    cur_year += 1

        return {
            "community_id": community_id,
            "bucket": date_trunc,
            "trend": trend
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
