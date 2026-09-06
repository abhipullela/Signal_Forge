"""Shared score normalization utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def min_max(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float)
    if values.empty:
        return pd.Series(0.0, index=values.index)
    low, high = values.min(), values.max()
    if pd.isna(low) or pd.isna(high) or abs(high - low) < 1e-12:
        return pd.Series(0.0, index=values.index)
    return ((values - low) / (high - low)).clip(0.0, 1.0)


def robust_min_max(series: pd.Series, lower_q: float = 0.05, upper_q: float = 0.95) -> pd.Series:
    """Normalize using quantiles so one extreme cluster cannot dominate the score."""
    values = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    if values.empty:
        return pd.Series(0.0, index=values.index)
    low = float(values.quantile(lower_q))
    high = float(values.quantile(upper_q))
    if not np.isfinite(low) or not np.isfinite(high) or high - low < 1e-12:
        return pd.Series(0.0, index=values.index)
    return ((values - low) / (high - low)).clip(0.0, 1.0)


def signed_log1p(series: pd.Series) -> pd.Series:
    """Compress large positive/negative derivatives without destroying direction."""
    values = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    return np.sign(values) * np.log1p(np.abs(values))


def clamp(value, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return float(np.clip(value, minimum, maximum))


def normalize_feature(value, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return clamp((float(value) / maximum) * 100.0)


def log_normalize(series: pd.Series) -> pd.Series:
    return min_max(np.log1p(pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)))
