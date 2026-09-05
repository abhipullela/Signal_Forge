"""Export SignalForge ML inference results to CSV."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "ml_output.csv"


def export_ml_output(results):
    """Export complete semantic clustering output to CSV."""

    if results is None:
        print("No results to export.")
        return None

    posts = results.get("posts", [])
    labels = results.get("labels", [])
    metrics = results.get("metrics", {})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for index, post in enumerate(posts):

        label = (
            labels[index]
            if index < len(labels)
            else -1
        )

        # Handle dictionary posts
        if isinstance(post, dict):

            row = post.copy()

        # Handle tuple/list posts
        elif isinstance(post, (tuple, list)):

            row = {
                "post_data": str(post)
            }

        # Handle plain text posts
        else:

            row = {
                "text": str(post)
            }

        row["cluster_id"] = int(label)

        rows.append(row)

    df = pd.DataFrame(rows)

    # ----------------------------------------------------
    # Add cluster-level information
    # ----------------------------------------------------

    if "cluster_id" in df.columns:

        cluster_sizes = (
            df["cluster_id"]
            .value_counts()
            .to_dict()
        )

        df["cluster_size"] = (
            df["cluster_id"]
            .map(cluster_sizes)
        )

    # ----------------------------------------------------
    # Add clustering metrics
    # ----------------------------------------------------

    if metrics:

        for name, value in metrics.items():

            # Metrics apply to the complete clustering
            # result, so repeat them for every row.
            if isinstance(
                value,
                (int, float, np.integer, np.floating)
            ):
                df[f"metric_{name}"] = float(value)

            else:
                df[f"metric_{name}"] = str(value)

    # ----------------------------------------------------
    # Cluster rank
    # ----------------------------------------------------

    if "cluster_size" in df.columns:

        cluster_rank = (
            df.groupby("cluster_id")["cluster_size"]
            .first()
            .rank(
                method="dense",
                ascending=False
            )
        )

        rank_dict = cluster_rank.to_dict()

        df["cluster_rank"] = (
            df["cluster_id"]
            .map(rank_dict)
            .astype(int)
        )

    # ----------------------------------------------------
    # Signal score
    # ----------------------------------------------------

    if "cluster_size" in df.columns:

        maximum = df["cluster_size"].max()

        if maximum > 0:

            df["signal_score"] = (
                df["cluster_size"]
                / maximum
                * 100
            )

        else:

            df["signal_score"] = 0.0

    else:

        df["signal_score"] = 0.0

    # ----------------------------------------------------
    # Signal classification
    # ----------------------------------------------------

    df["signal_status"] = np.select(
        [
            df["signal_score"] >= 75,
            df["signal_score"] >= 50,
            df["signal_score"] >= 25,
        ],
        [
            "HIGH",
            "MEDIUM",
            "LOW",
        ],
        default="BACKGROUND",
    )

    # ----------------------------------------------------
    # Sort strongest signals first
    # ----------------------------------------------------

    df = df.sort_values(
        "signal_score",
        ascending=False
    ).reset_index(drop=True)

    # ----------------------------------------------------
    # Export
    # ----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("ML OUTPUT EXPORTED")
    print("=" * 60)
    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")
    print(f"File    : {OUTPUT_FILE}")
    print("=" * 60)

    return OUTPUT_FILE