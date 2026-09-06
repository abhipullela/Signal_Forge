"""Temporal signal detection pipeline.

This module orchestrates reusable feature functions instead of containing
the entire temporal implementation in one monolithic script.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.features.growth import calculate_volume_dynamics
from ml.features.persistence import calculate_persistence
from ml.features.temporal import (
    aggregate_cluster_time,
    calculate_anomaly,
    calculate_baseline,
    calculate_community_dynamics,
    calculate_engagement_dynamics,
    complete_time_series,
    create_time_windows,
    get_eligible_clusters,
    select_analysis_window,
    validate_clustered_posts,
)
from ml.scoring.signal_score import score_temporal_signals

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "outputs" / "clustered_posts.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "temporal_features.csv"


def run_temporal_analysis(
    df: pd.DataFrame,
    *,
    analysis_days: int = 180,
    time_window: str = "7D",
    baseline_windows: int = 8,
) -> pd.DataFrame:
    """Return the latest scored temporal state for each eligible cluster."""
    working = validate_clustered_posts(df)
    working = select_analysis_window(working, analysis_days=analysis_days)
    if working.empty:
        return pd.DataFrame()

    working = create_time_windows(working, frequency=time_window)
    temporal = aggregate_cluster_time(working)
    temporal = complete_time_series(temporal, frequency=time_window)
    temporal = calculate_volume_dynamics(temporal)
    temporal = calculate_engagement_dynamics(temporal)
    temporal = calculate_community_dynamics(temporal)
    temporal = calculate_baseline(temporal, baseline_windows=baseline_windows)
    temporal = calculate_anomaly(temporal)
    temporal = calculate_persistence(temporal)

    stats, eligible = get_eligible_clusters(temporal)
    scored = score_temporal_signals(temporal, eligible)

    if scored.empty:
        return scored

    output = scored.merge(stats, on="cluster_id", how="left")
    output = output.sort_values("signal_score", ascending=False).reset_index(drop=True)

    # Stable aliases retained for downstream risk/alert code and API consumers.
    output["temporal_signal_score"] = output["signal_score"]
    output["anomaly"] = output["anomaly_score"]
    output["persistence"] = output["persistence_windows"]
    output["communities"] = output["community_count"]

    return output


def run_temporal_analysis_from_csv(
    input_path: str | Path = DEFAULT_INPUT,
    output_path: str | Path = DEFAULT_OUTPUT,
) -> pd.DataFrame:
    """CSV wrapper for CLI/script usage."""
    df = pd.read_csv(input_path)
    result = run_temporal_analysis(df)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


if __name__ == "__main__":
    result = run_temporal_analysis_from_csv()
    print(f"Saved {len(result):,} temporal signal rows.")
