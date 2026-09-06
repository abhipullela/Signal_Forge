"""SignalForge ML inference orchestration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.detection.cluster_detector import (
    cluster_embeddings,
    evaluate_clustering,
    print_clusters,
)
from ml.detection.temporal_detector import run_temporal_analysis
from ml.explanation.feature_explanations import classify_risk
from ml.features.community_spread import build_propagation_features
from ml.features.embeddings import create_embeddings, load_embedding_model
from ml.inference.export_output import (
    export_alerts,
    export_ml_output,
    generate_alerts,
)
from ml.ingestion.loaders import connect_to_database, load_posts
from ml.scoring.ranking import rank_signals


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs"


def run_semantic_clustering():
    """Run the SignalForge semantic clustering stage."""

    print("SignalForge Semantic Clustering")
    print("=" * 60)

    model = load_embedding_model()

    conn = connect_to_database()

    try:
        # posts = load_posts(conn)

        # if not posts:
        #     print("No posts found. Nothing to cluster.")
        #     return None
        posts = load_posts(conn)

        if not posts:
            print("No posts found. Nothing to cluster.")
            return None

        embeddings = create_embeddings(
            posts,
            model,
        )

        labels, clusterer = cluster_embeddings(
            embeddings
        )

        print_clusters(
            posts,
            labels,
        )

        metrics = evaluate_clustering(
            embeddings,
            labels,
        )

        print("\n--- Metrics ---")

        for name, value in metrics.items():
            if isinstance(value, float):
                print(f"{name}: {value:.4f}")
            else:
                print(f"{name}: {value}")

        results = {
            "posts": posts,
            "embeddings": embeddings,
            "labels": labels,
            "clusterer": clusterer,
            "metrics": metrics,
        }

        export_ml_output(results)

        return results

    finally:
        conn.close()

        print("\nDatabase connection closed.")


def run_signal_analysis(clustered_posts: pd.DataFrame) -> dict:
    """Run temporal, propagation, scoring, risk and alert stages."""

    print("\nSignalForge Signal Analysis")
    print("=" * 60)

    # --------------------------------------------------------
    # Temporal analysis
    # --------------------------------------------------------

    print("\nRunning temporal analysis...")

    temporal = run_temporal_analysis(
        clustered_posts
    )

    # --------------------------------------------------------
    # Propagation analysis
    # --------------------------------------------------------

    print("Running propagation analysis...")

    # Keep temporal and propagation analysis on the same recent horizon.
    propagation = build_propagation_features(
        clustered_posts,
        analysis_days=180,
    )

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    print("Running risk classification...")

    risk = classify_risk(
        temporal,
        propagation,
        clustered_posts,
    )

    # --------------------------------------------------------
    # Alert generation
    # --------------------------------------------------------

    print("Generating alerts...")

    alerts = generate_alerts(
        temporal,
        propagation,
        risk,
        clustered_posts,
    )

    # --------------------------------------------------------
    # Export results
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporal.to_csv(
        OUTPUT_DIR / "temporal_features.csv",
        index=False,
    )

    propagation.to_csv(
        OUTPUT_DIR / "propagation_features.csv",
        index=False,
    )

    risk.to_csv(
        OUTPUT_DIR / "risk_classification.csv",
        index=False,
    )

    export_alerts(
        alerts,
        OUTPUT_DIR / "alerts.csv",
    )

    return {
        "temporal": rank_signals(
            temporal
        ),
        "propagation": propagation,
        "risk": risk,
        "alerts": alerts,
    }


def run_full_pipeline() -> dict | None:
    """Run the complete SignalForge ML pipeline."""

    results = run_semantic_clustering()

    if results is None:
        return None

    posts = results.get("posts", [])
    labels = results.get("labels", [])

    rows = []

    for index, post in enumerate(posts):

        # Database loader returns dictionaries.
        if isinstance(post, dict):
            row = post.copy()

        elif hasattr(post, "_asdict"):
            row = post._asdict()

        elif isinstance(post, (tuple, list)):
            row = {
                "post_data": str(post)
            }

        else:
            row = {
                "text": str(post)
            }

        # ----------------------------------------------------
        # Preserve the real database post ID.
        # temporal.py expects the column to be called "id".
        # ----------------------------------------------------

        if "post_id" in row and "id" not in row:
            row["id"] = row["post_id"]

        # ----------------------------------------------------
        # Add cluster ID
        # ----------------------------------------------------

        row["cluster_id"] = (
            int(labels[index])
            if index < len(labels)
            else -1
        )

        rows.append(row)

    clustered_posts = pd.DataFrame(rows)

    print("\nClustered DataFrame columns:")
    print(list(clustered_posts.columns))

    # --------------------------------------------------------
    # Validate required temporal-analysis column
    # --------------------------------------------------------

    if "id" not in clustered_posts.columns:
        raise ValueError(
            "The clustered posts are missing the required "
            "'id' column."
        )

    return run_signal_analysis(
        clustered_posts
    )

if __name__ == "__main__":
    output = run_full_pipeline()

    if output is not None:
        print(
            f"\nAlerts generated: "
            f"{len(output['alerts']):,}"
        )