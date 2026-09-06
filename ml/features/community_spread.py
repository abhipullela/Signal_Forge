"""Cross-community and cross-source propagation features."""

from __future__ import annotations

import numpy as np
import pandas as pd

TIME_WINDOW = "7D"
ANALYSIS_DAYS = 180
RECENT_DAYS = 28
NOISE_CLUSTER = -1
MIN_CLUSTER_POSTS = 5


def minmax_normalize(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float)
    if values.empty:
        return pd.Series(0.0, index=values.index)
    low, high = values.min(), values.max()
    if pd.isna(low) or pd.isna(high) or abs(high - low) < 1e-12:
        return pd.Series(0.0, index=values.index)
    return (values - low) / (high - low)


def prepare_propagation_data(df: pd.DataFrame) -> pd.DataFrame:
    required = {"cluster_id", "community_id", "source_id", "published_at"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Missing propagation columns: {missing}")

    out = df.copy()
    out["cluster_id"] = pd.to_numeric(out["cluster_id"], errors="coerce")
    out["community_id"] = pd.to_numeric(out["community_id"], errors="coerce")
    out["source_id"] = pd.to_numeric(out["source_id"], errors="coerce")
    out["published_at"] = pd.to_datetime(out["published_at"], errors="coerce", utc=True)
    out = out.dropna(subset=["cluster_id", "community_id", "source_id", "published_at"])
    out["cluster_id"] = out["cluster_id"].astype(int)
    return out[out["cluster_id"] != NOISE_CLUSTER].copy()


def create_propagation_windows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["time_window"] = out["published_at"].dt.floor(TIME_WINDOW)
    return out


def calculate_community_propagation(df: pd.DataFrame):
    community_activity = (
        df.groupby(["cluster_id", "time_window", "community_id"])
        .agg(posts=("cluster_id", "size"))
        .reset_index()
    )
    window_spread = (
        community_activity.groupby(["cluster_id", "time_window"])
        .agg(
            active_communities=("community_id", "nunique"),
            window_posts=("posts", "sum"),
        )
        .reset_index()
        .sort_values(["cluster_id", "time_window"])
    )
    window_spread["previous_communities"] = (
        window_spread.groupby("cluster_id")["active_communities"].shift(1).fillna(0)
    )
    window_spread["community_spread_velocity"] = (
        window_spread["active_communities"] - window_spread["previous_communities"]
    )
    return community_activity, window_spread


def calculate_cross_community_features(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("cluster_id")
        .agg(
            total_posts=("cluster_id", "size"),
            communities=("community_id", "nunique"),
            sources=("source_id", "nunique"),
            first_seen=("published_at", "min"),
            last_seen=("published_at", "max"),
        )
        .reset_index()
    )
    grouped["cross_community"] = (grouped["communities"] > 1).astype(int)
    grouped["cross_source"] = (grouped["sources"] > 1).astype(int)
    grouped["duration_hours"] = (
        (grouped["last_seen"] - grouped["first_seen"]).dt.total_seconds() / 3600
    ).clip(lower=1)
    grouped["community_spread_rate"] = (
        grouped["communities"] / grouped["duration_hours"]
    )
    return grouped


def calculate_adoption_features(df: pd.DataFrame) -> pd.DataFrame:
    adoption = (
        df.groupby(["cluster_id", "community_id"])
        .agg(
            first_seen=("published_at", "min"),
            community_posts=("cluster_id", "size"),
        )
        .reset_index()
        .sort_values(["cluster_id", "first_seen"])
    )
    adoption["adoption_order"] = adoption.groupby("cluster_id").cumcount() + 1

    summary = (
        adoption.groupby("cluster_id")
        .agg(
            first_community_time=("first_seen", "min"),
            last_community_time=("first_seen", "max"),
            communities_adopted=("community_id", "nunique"),
        )
        .reset_index()
    )
    summary["adoption_duration_hours"] = (
        (summary["last_community_time"] - summary["first_community_time"])
        .dt.total_seconds() / 3600
    ).fillna(0).clip(lower=0)
    summary["propagation_velocity"] = np.where(
        summary["adoption_duration_hours"] > 0,
        (summary["communities_adopted"] - 1)
        / (summary["adoption_duration_hours"] / 24),
        0.0,
    )
    return summary


def calculate_source_propagation(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("cluster_id").agg(source_count=("source_id", "nunique")).reset_index()
    out["cross_source_spread"] = (out["source_count"] > 1).astype(int)
    return out


def calculate_recent_propagation(df: pd.DataFrame, window_spread: pd.DataFrame) -> pd.DataFrame:
    if window_spread.empty:
        return pd.DataFrame(columns=[
            "cluster_id", "recent_community_max",
            "recent_community_growth", "recent_windows_active"
        ])

    latest_window = df["time_window"].max()
    recent = window_spread[
        window_spread["time_window"] >= latest_window - pd.Timedelta(days=RECENT_DAYS)
    ]
    return (
        recent.groupby("cluster_id")
        .agg(
            recent_community_max=("active_communities", "max"),
            recent_community_growth=("community_spread_velocity", "sum"),
            recent_windows_active=("time_window", "nunique"),
        )
        .reset_index()
    )


def _saturating_coverage(communities: pd.Series) -> pd.Series:
    """Bound community coverage so 2 communities cannot look widespread."""
    values = pd.to_numeric(communities, errors="coerce").fillna(0).clip(lower=1)
    return (1.0 - np.exp(-(values - 1.0) / 2.0)).clip(0.0, 1.0)


def _saturating_positive(series: pd.Series, scale: float = 1.0) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0).clip(lower=0.0)
    scale = max(float(scale), 1e-9)
    return (1.0 - np.exp(-values / scale)).clip(0.0, 1.0)


def calculate_propagation_score(features: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()

    # Propagation is evidence of spread, not risk. Coverage is strongest,
    # while adoption speed, recent spread and source diversity provide support.
    coverage = _saturating_coverage(out["communities"])
    velocity_scale = max(float(out["propagation_velocity"].median()), 1.0)
    growth_scale = max(float(out["recent_community_growth"].abs().median()), 1.0)
    source_scale = max(float(out["source_count"].median()), 1.0)

    velocity = _saturating_positive(out["propagation_velocity"], velocity_scale)
    recent_growth = _saturating_positive(out["recent_community_growth"], growth_scale)
    sources = _saturating_positive(out["source_count"].clip(lower=1) - 1, source_scale)

    out["propagation_score"] = (
        0.45 * coverage
        + 0.25 * velocity
        + 0.20 * recent_growth
        + 0.10 * sources
    ) * 100.0
    out["propagation_score"] = out["propagation_score"].clip(0, 100).round(2)
    out["propagation_status"] = np.select(
        [out["propagation_score"] >= 70, out["propagation_score"] >= 40],
        ["HIGH", "MEDIUM"],
        default="LOW",
    )
    return out


def build_propagation_features(
    df: pd.DataFrame,
    *,
    analysis_days: int = ANALYSIS_DAYS,
) -> pd.DataFrame:
    """Run propagation analysis on the same recent horizon as temporal analysis.

    Using the full historical dataset for propagation made a cluster first
    seen years ago look like it had just propagated today.  Propagation is
    therefore measured inside the configured analysis horizon.
    """
    prepared = prepare_propagation_data(df)
    if prepared.empty:
        return pd.DataFrame(
            columns=["cluster_id", "propagation_score", "propagation_status"]
        )

    end = prepared["published_at"].max()
    start = end - pd.Timedelta(days=analysis_days)
    prepared = prepared[
        (prepared["published_at"] >= start)
        & (prepared["published_at"] <= end)
    ].copy()

    if prepared.empty:
        return pd.DataFrame(
            columns=["cluster_id", "propagation_score", "propagation_status"]
        )

    sizes = prepared.groupby("cluster_id").size()
    prepared = prepared[prepared["cluster_id"].isin(
        sizes[sizes >= MIN_CLUSTER_POSTS].index
    )].copy()

    if prepared.empty:
        return pd.DataFrame(columns=["cluster_id", "propagation_score", "propagation_status"])

    prepared = create_propagation_windows(prepared)
    _, window_spread = calculate_community_propagation(prepared)
    community = calculate_cross_community_features(prepared)
    adoption = calculate_adoption_features(prepared)
    source = calculate_source_propagation(prepared)
    recent = calculate_recent_propagation(prepared, window_spread)

    features = community.merge(adoption, on="cluster_id", how="left")
    features = features.merge(source, on="cluster_id", how="left")
    features = features.merge(recent, on="cluster_id", how="left")
    return calculate_propagation_score(features).fillna(0)
