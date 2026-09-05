from fastapi import FastAPI, HTTPException
import psycopg2
import os
from dotenv import load_dotenv


# ============================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()


# ============================================
# 2. CREATE FASTAPI APP
# ============================================

app = FastAPI(
    title="Signal Forge API",
    description="Backend API for Signal Forge",
    version="1.0.0"
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
                COUNT(*) AS total_posts
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
                "total_posts": row[1]
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
def community_overview(community_id: int):

    try:

        connection = get_connection()
        cursor = connection.cursor()


        # ----------------------------------------
        # TOTAL POSTS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM ml_results
            WHERE community_id = %s
        """, (community_id,))

        total_posts = cursor.fetchone()[0]


        # ----------------------------------------
        # ACTIVE SIGNALS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM ml_results
            WHERE community_id = %s
            AND signal_status IN ('HIGH','MEDIUM')
        """, (community_id,))

        active_signals = cursor.fetchone()[0]


        # ----------------------------------------
        # ACTIVE CLUSTERS
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(DISTINCT cluster_id)
            FROM ml_results
            WHERE community_id = %s
            AND cluster_id IS NOT NULL
        """, (community_id,))

        active_clusters = cursor.fetchone()[0]


        # ----------------------------------------
        # AVERAGE SIGNAL SCORE
        # ----------------------------------------

        cursor.execute("""
            SELECT AVG(signal_score)
            FROM ml_results
            WHERE community_id = %s
            AND signal_score IS NOT NULL
        """, (community_id,))

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

@app.get("/api/community/{community_id}/signals")
def community_signals(community_id: int):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                post_id,
                title,
                cluster_id,
                cluster_size,
                cluster_rank,
                signal_score,
                signal_status,
                published_at
            FROM ml_results

            WHERE community_id = %s

            AND signal_score IS NOT NULL

            ORDER BY signal_score DESC

            LIMIT 20
        """, (community_id,))

        rows = cursor.fetchall()

        cursor.close()
        connection.close()


        signals = []

        for row in rows:

            signals.append({
                "post_id": row[0],
                "title": row[1],
                "cluster_id": row[2],
                "cluster_size": row[3],
                "cluster_rank": row[4],
                "signal_score": row[5],
                "signal_status": row[6],
                "published_at": row[7]
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
def community_clusters(community_id: int):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                cluster_id,
                MAX(cluster_size) AS cluster_size,
                MAX(cluster_rank) AS cluster_rank,
                COUNT(*) AS post_count,
                AVG(signal_score) AS average_signal_score
            FROM ml_results

            WHERE community_id = %s
            AND cluster_id IS NOT NULL

            GROUP BY cluster_id

            ORDER BY average_signal_score DESC
        """, (community_id,))

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
            "published_at": row[9],
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
def community_trend(community_id: int):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                DATE(published_at) AS date,
                COUNT(*) AS post_count,
                AVG(signal_score) AS average_signal_score
            FROM ml_results

            WHERE community_id = %s
            AND published_at IS NOT NULL

            GROUP BY DATE(published_at)

            ORDER BY DATE(published_at)
        """, (community_id,))

        rows = cursor.fetchall()

        cursor.close()
        connection.close()


        trend = []

        for row in rows:

            trend.append({
                "date": row[0],
                "post_count": row[1],
                "average_signal_score": row[2]
            })


        return {
            "community_id": community_id,
            "trend": trend
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )