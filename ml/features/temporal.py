"""Temporal feature engineering for SignalForge.

This file owns reusable time-series features.  Pipeline orchestration
lives in ml/detection/temporal_detector.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

EPSILON = 1e-9
TIME_WINDOW = "7D"
BASELINE_WINDOWS = 8
ANALYSIS_DAYS = 180
MIN_TOTAL_POSTS = 5
MIN_ACTIVE_WINDOWS = 2


def validate_clustered_posts(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the canonical post schema and support legacy ``id`` inputs.

    The database loader uses ``post_id``.  Temporal features historically
    expected ``id``.  Normalize that boundary here so downstream feature
    functions have one stable identifier without forcing the database schema
    to change.
    """
    out = df.copy()

    if "id" not in out.columns and "post_id" in out.columns:
        out["id"] = out["post_id"]

    required = {"id", "community_id", "published_at", "score", "cluster_id"}
    missing = sorted(required.difference(out.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    out["published_at"] = pd.to_datetime(out["published_at"], errors="coerce", utc=True)
    out = out.dropna(subset=["published_at", "cluster_id"]).copy()
    out["cluster_id"] = pd.to_numeric(out["cluster_id"], errors="coerce")
    out = out.dropna(subset=["cluster_id"]).copy()
    out["cluster_id"] = out["cluster_id"].astype(int)
    out["score"] = pd.to_numeric(out["score"], errors="coerce").fillna(0.0)
    out["community_id"] = out["community_id"].fillna("unknown").astype(str)
    return out.sort_values("published_at").reset_index(drop=True)


def select_analysis_window(df: pd.DataFrame, analysis_days: int = ANALYSIS_DAYS) -> pd.DataFrame:
    end = df["published_at"].max()
    start = end - pd.Timedelta(days=analysis_days)
    return df[
        (df["published_at"] >= start)
        & (df["published_at"] <= end)
        & (df["cluster_id"] != -1)
    ].copy()


def create_time_windows(df: pd.DataFrame, frequency: str = TIME_WINDOW) -> pd.DataFrame:
    out = df.copy()
    out["time_window"] = out["published_at"].dt.floor(frequency)
    return out


def aggregate_cluster_time(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["cluster_id", "time_window"], as_index=False)
        .agg(
            volume=("id", "count"),
            engagement=("score", "sum"),
            average_engagement=("score", "mean"),
            community_count=("community_id", "nunique"),
        )
        .sort_values(["cluster_id", "time_window"])
        .reset_index(drop=True)
    )


def complete_time_series(df: pd.DataFrame, frequency: str = TIME_WINDOW) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    times = pd.date_range(df["time_window"].min(), df["time_window"].max(), freq=frequency)
    clusters = sorted(df["cluster_id"].unique())
    index = pd.MultiIndex.from_product(
        [clusters, times], names=["cluster_id", "time_window"]
    )

    out = (
        df.set_index(["cluster_id", "time_window"])
        .reindex(index)
        .reset_index()
    )
    for col in ["volume", "engagement", "average_engagement", "community_count"]:
        out[col] = out[col].fillna(0.0)
    return out


def calculate_engagement_dynamics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    previous = out.groupby("cluster_id")["engagement"].shift(1)
    out["engagement_velocity"] = (out["engagement"] - previous).fillna(0.0)
    out["engagement_growth"] = (
        (out["engagement"] - previous) / (previous + EPSILON)
    ).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


def calculate_community_dynamics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    previous = out.groupby("cluster_id")["community_count"].shift(1)
    out["community_velocity"] = (
        out["community_count"] - previous
    ).fillna(0.0)
    return out


def calculate_baseline(
    df: pd.DataFrame, baseline_windows: int = BASELINE_WINDOWS
) -> pd.DataFrame:
    out = df.copy()
    shifted = out.groupby("cluster_id")["volume"].shift(1)
    grouped = shifted.groupby(out["cluster_id"])
    rolling = grouped.rolling(baseline_windows, min_periods=3)
    out["baseline_volume"] = rolling.mean().reset_index(level=0, drop=True)
    out["baseline_std"] = rolling.std().reset_index(level=0, drop=True)
    out["baseline_available"] = out["baseline_volume"].notna() & out["baseline_std"].notna()
    out["baseline_volume"] = out["baseline_volume"].fillna(0.0)
    out["baseline_std"] = out["baseline_std"].fillna(0.0)
    return out

def calculate_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    usable_std = out["baseline_available"] & (out["baseline_std"] > EPSILON)
    flat_baseline = (
        out["baseline_available"]
        & ~usable_std
        & (out["baseline_volume"] > 0)
    )
    out["anomaly_score"] = 0.0
    out.loc[usable_std, "anomaly_score"] = (
        (out.loc[usable_std, "volume"] - out.loc[usable_std, "baseline_volume"])
        / out.loc[usable_std, "baseline_std"]
    )
    out.loc[flat_baseline, "anomaly_score"] = (
        (out.loc[flat_baseline, "volume"] - out.loc[flat_baseline, "baseline_volume"])
        / out.loc[flat_baseline, "baseline_volume"]
    ).clip(lower=0, upper=10)
    out["anomaly_score"] = out["anomaly_score"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    out["positive_anomaly_score"] = out["anomaly_score"].clip(lower=0.0)
    return out

def get_eligible_clusters(
    df: pd.DataFrame,
    min_total_posts: int = MIN_TOTAL_POSTS,
    min_active_windows: int = MIN_ACTIVE_WINDOWS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    stats = (
        df.groupby("cluster_id")
        .agg(
            total_posts=("volume", "sum"),
            active_windows=("volume", lambda x: int((x > 0).sum())),
            max_volume=("volume", "max"),
        )
        .reset_index()
    )
    eligible = stats[
        (stats["total_posts"] >= min_total_posts)
        & (stats["active_windows"] >= min_active_windows)
    ].copy()
    return stats, eligible
