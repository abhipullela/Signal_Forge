"""Transparent and robust composite signal scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml.features.persistence import persistence_multiplier
from ml.scoring.normalizer import min_max, robust_min_max, signed_log1p

SIGNAL_WEIGHTS = {
    "growth_score": 0.20,
    "velocity_score": 0.15,
    "acceleration_score": 0.15,
    "engagement_score": 0.15,
    "anomaly_score_normalized": 0.20,
    "persistence_score": 0.14,
    "community_spread_score": 0.01,
}

HIGH_THRESHOLD = 70.0
MEDIUM_THRESHOLD = 40.0


def _score_positive(series: pd.Series, *, log_compress: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0).clip(lower=0.0)
    if log_compress:
        values = np.log1p(values)
    return robust_min_max(values)


def create_scoring_features(temporal: pd.DataFrame, eligible: pd.DataFrame) -> pd.DataFrame:
    if eligible.empty:
        return pd.DataFrame()

    ids = set(eligible["cluster_id"].astype(int))
    working = temporal[temporal["cluster_id"].isin(ids)].copy()
    if working.empty:
        return pd.DataFrame()

    latest = (
        working.sort_values(["cluster_id", "time_window"])
        .groupby("cluster_id", as_index=False)
        .tail(1)
        .copy()
    )

    # Derivatives are compressed before normalization. This prevents a single
    # sparse window with acceleration in the thousands from dominating every score.
    latest["positive_growth"] = latest["growth_rate"].clip(lower=0)
    latest["growth_score"] = _score_positive(latest["positive_growth"], log_compress=True)

    velocity = latest.get("velocity_log", signed_log1p(latest["velocity"]))
    latest["positive_velocity"] = pd.to_numeric(velocity, errors="coerce").fillna(0.0).clip(lower=0)
    latest["velocity_score"] = _score_positive(latest["positive_velocity"])

    acceleration = latest.get("acceleration_log", signed_log1p(latest["acceleration"]))
    latest["positive_acceleration"] = pd.to_numeric(acceleration, errors="coerce").fillna(0.0).clip(lower=0)
    latest["acceleration_score"] = _score_positive(latest["positive_acceleration"])

    latest["log_engagement"] = np.log1p(latest["engagement"].clip(lower=0))
    latest["engagement_score"] = robust_min_max(latest["log_engagement"])

    # No baseline means there is no anomaly evidence. Keep anomaly at zero.
    latest["anomaly_score_normalized"] = _score_positive(
        np.log1p(latest["positive_anomaly_score"].clip(lower=0))
    )
    latest.loc[~latest["baseline_available"], "anomaly_score_normalized"] = 0.0

    latest["persistence_score"] = _score_positive(latest["persistence_windows"])
    latest["community_spread_score"] = _score_positive(
        latest["community_velocity"].clip(lower=0)
    )
    return latest


def calculate_signal_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["raw_signal_score"] = 0.0

    # Redistribute unavailable anomaly weight across available evidence rather
    # than silently penalising clusters merely because they lack history.
    available_weights = out.apply(
        lambda row: {
            key: weight
            for key, weight in SIGNAL_WEIGHTS.items()
            if key != "anomaly_score_normalized" or bool(row.get("baseline_available", False))
        },
        axis=1,
    )

    scores = []
    for idx, row in out.iterrows():
        weights = available_weights.loc[idx]
        total_weight = sum(weights.values()) or 1.0
        weighted = sum(float(row.get(feature, 0.0) or 0.0) * weight for feature, weight in weights.items())
        scores.append((weighted / total_weight) * 100.0)
    out["raw_signal_score"] = pd.Series(scores, index=out.index).clip(0, 100).round(2)

    out["persistence_multiplier"] = persistence_multiplier(out["persistence_windows"])
    out["signal_score"] = (out["raw_signal_score"] * out["persistence_multiplier"]).clip(0, 100).round(2)

    out["signal_status"] = "LOW"
    out.loc[out["signal_score"] >= MEDIUM_THRESHOLD, "signal_status"] = "MEDIUM"
    out.loc[out["signal_score"] >= HIGH_THRESHOLD, "signal_status"] = "HIGH"
    return out


def score_temporal_signals(temporal: pd.DataFrame, eligible: pd.DataFrame) -> pd.DataFrame:
    return calculate_signal_score(create_scoring_features(temporal, eligible))
