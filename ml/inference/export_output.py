"""Export SignalForge ML inference results to CSV."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "ml_output.csv"
ALERT_FILE = OUTPUT_DIR / "alerts.csv"

# Alert-generation thresholds. The authoritative temporal signal score
# remains in ml.scoring.signal_score; this module only combines already
# computed evidence into an alert priority.
SIGNAL_THRESHOLD = 25.0
MEDIUM_RISK_THRESHOLD = 45.0
HIGH_RISK_THRESHOLD = 70.0
PROPAGATION_THRESHOLD = 40.0
PERSISTENCE_THRESHOLD = 2.0
MIN_ALERT_POSTS = 10


# ============================================================
# HELPERS
# ============================================================


def _safe_float(value, default=0.0):
    """Safely convert a value to float."""

    try:
        value = float(value)

        if np.isnan(value) or np.isinf(value):
            return default

        return value

    except (TypeError, ValueError):
        return default


def _clamp(value, minimum=0.0, maximum=100.0):
    """Clamp a numeric value to a fixed range."""

    return max(
        minimum,
        min(maximum, _safe_float(value)),
    )


def _find_column(df, candidates):
    """Return the first matching column from candidates."""

    for column in candidates:
        if column in df.columns:
            return column

    return None


# ============================================================
# SEMANTIC CLUSTERING OUTPUT
# ============================================================


def export_ml_output(results):
    """Export complete semantic clustering output to CSV."""

    if results is None:
        print("No results to export.")
        return None

    posts = results.get("posts", [])
    labels = results.get("labels", [])
    metrics = results.get("metrics", {})

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    for index, post in enumerate(posts):

        label = (
            labels[index]
            if index < len(labels)
            else -1
        )

        # Dictionary posts
        if isinstance(post, dict):

            row = post.copy()

        # Tuple/list posts
        elif isinstance(post, (tuple, list)):

            row = {
                "post_data": str(post)
            }

        # Plain text posts
        else:

            row = {
                "text": str(post)
            }

        row["cluster_id"] = int(label)

        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        df.to_csv(
            OUTPUT_FILE,
            index=False,
        )

        print("No rows to export.")
        return OUTPUT_FILE

    # --------------------------------------------------------
    # Cluster size
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Clustering metrics
    # --------------------------------------------------------

    if metrics:

        for name, value in metrics.items():

            if isinstance(
                value,
                (
                    int,
                    float,
                    np.integer,
                    np.floating,
                ),
            ):

                df[f"metric_{name}"] = float(value)

            else:

                df[f"metric_{name}"] = str(value)

    # --------------------------------------------------------
    # Cluster rank
    # --------------------------------------------------------

    if "cluster_size" in df.columns:

        cluster_rank = (
            df.groupby("cluster_id")["cluster_size"]
            .first()
            .rank(
                method="dense",
                ascending=False,
            )
        )

        rank_dict = cluster_rank.to_dict()

        df["cluster_rank"] = (
            df["cluster_id"]
            .map(rank_dict)
            .fillna(0)
            .astype(int)
        )

    # --------------------------------------------------------
    # Cluster-size score
    #
    # This is a semantic-clustering diagnostic, not the final
    # emerging-signal score.  The authoritative temporal signal
    # score is produced by ml.scoring.signal_score.
    # --------------------------------------------------------

    if "cluster_size" in df.columns:

        maximum = df["cluster_size"].max()

        if maximum > 0:

            df["semantic_cluster_score"] = (
                df["cluster_size"]
                / maximum
                * 100
            )

        else:

            df["semantic_cluster_score"] = 0.0

    else:

        df["signal_score"] = 0.0

    # --------------------------------------------------------
    # Signal classification
    # --------------------------------------------------------

    df["semantic_cluster_status"] = np.select(
        [
            df["semantic_cluster_score"] >= 75,
            df["semantic_cluster_score"] >= 50,
            df["semantic_cluster_score"] >= 25,
        ],
        [
            "HIGH",
            "MEDIUM",
            "LOW",
        ],
        default="BACKGROUND",
    )

    # --------------------------------------------------------
    # Sort strongest semantic clusters first
    # --------------------------------------------------------

    df = df.sort_values(
        "semantic_cluster_score",
        ascending=False,
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n" + "=" * 60)
    print("ML OUTPUT EXPORTED")
    print("=" * 60)
    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")
    print(f"File    : {OUTPUT_FILE}")
    print("=" * 60)

    return OUTPUT_FILE


# ============================================================
# ALERT GENERATION
# ============================================================


def generate_alerts(
    temporal,
    propagation,
    risk,
    clustered_posts,
):
    """
    Generate explainable alerts from ML analysis results.

    The function operates at cluster level and combines:
        - temporal signal strength
        - propagation
        - risk classification
        - source-post information
    """

    if temporal is None:
        return pd.DataFrame()

    if not isinstance(temporal, pd.DataFrame):
        temporal = pd.DataFrame(temporal)

    if propagation is None:
        propagation = pd.DataFrame()

    if not isinstance(propagation, pd.DataFrame):
        propagation = pd.DataFrame(propagation)

    if risk is None:
        risk = pd.DataFrame()

    if not isinstance(risk, pd.DataFrame):
        risk = pd.DataFrame(risk)

    if clustered_posts is None:
        clustered_posts = pd.DataFrame()

    if not isinstance(
        clustered_posts,
        pd.DataFrame,
    ):
        clustered_posts = pd.DataFrame(
            clustered_posts
        )

    if temporal.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Determine cluster column
    # --------------------------------------------------------

    cluster_column = _find_column(
        temporal,
        [
            "cluster_id",
            "cluster",
            "community_id",
        ],
    )

    if cluster_column is None:
        return pd.DataFrame()

    alerts = temporal.copy()

    # --------------------------------------------------------
    # Merge propagation features
    # --------------------------------------------------------

    propagation_cluster = _find_column(
        propagation,
        [
            "cluster_id",
            "cluster",
            "community_id",
        ],
    )

    if (
        propagation_cluster is not None
        and propagation_cluster != cluster_column
    ):

        propagation = propagation.rename(
            columns={
                propagation_cluster: cluster_column
            }
        )

    if (
        not propagation.empty
        and cluster_column in propagation.columns
    ):

        propagation_columns = [
            column
            for column in propagation.columns
            if column != cluster_column
            and column not in alerts.columns
        ]

        if propagation_columns:

            alerts = alerts.merge(
                propagation[
                    [cluster_column]
                    + propagation_columns
                ],
                on=cluster_column,
                how="left",
            )

    # --------------------------------------------------------
    # Merge risk features
    # --------------------------------------------------------

    risk_cluster = _find_column(
        risk,
        [
            "cluster_id",
            "cluster",
            "community_id",
        ],
    )

    if (
        risk_cluster is not None
        and risk_cluster != cluster_column
    ):

        risk = risk.rename(
            columns={
                risk_cluster: cluster_column
            }
        )

    if (
        not risk.empty
        and cluster_column in risk.columns
    ):

        risk_columns = [
            column
            for column in risk.columns
            if column != cluster_column
            and column not in alerts.columns
        ]

        if risk_columns:

            alerts = alerts.merge(
                risk[
                    [cluster_column]
                    + risk_columns
                ],
                on=cluster_column,
                how="left",
            )

    # --------------------------------------------------------
    # Identify useful scoring columns
    # --------------------------------------------------------

    signal_column = _find_column(
        alerts,
        [
            "signal_score",
            "composite_score",
            "score",
            "temporal_score",
        ],
    )

    if signal_column is None:
        alerts["signal_score"] = 0.0
        signal_column = "signal_score"

    alerts["signal_score"] = alerts[
        signal_column
    ].apply(_safe_float).apply(_clamp)

    # --------------------------------------------------------
    # Propagation score
    # --------------------------------------------------------

    propagation_column = _find_column(
        alerts,
        [
            "propagation_score",
            "spread_score",
            "community_spread_score",
            "propagation_strength",
        ],
    )

    if propagation_column is None:

        propagation_column = "propagation_score"

        alerts[propagation_column] = 0.0

    alerts[propagation_column] = alerts[
        propagation_column
    ].apply(_safe_float).apply(_clamp)

    # --------------------------------------------------------
    # Risk score
    # --------------------------------------------------------

    risk_column = _find_column(
        alerts,
        [
            "risk_score",
            "risk",
            "risk_level_score",
        ],
    )

    if risk_column is None:

        risk_column = "risk_score"

        alerts[risk_column] = 0.0

    alerts[risk_column] = alerts[
        risk_column
    ].apply(_safe_float).apply(_clamp)

    # --------------------------------------------------------
    # Composite alert priority
    #
    # Ported from src/alert_generation.py.  This is intentionally
    # separate from the temporal signal score.
    # --------------------------------------------------------

    persistence_column = _find_column(
        alerts,
        ["persistence", "persistence_windows"],
    )

    if persistence_column is None:
        alerts["persistence"] = 0.0
        persistence_column = "persistence"

    alerts[persistence_column] = (
        alerts[persistence_column]
        .apply(_safe_float)
        .clip(lower=0)
    )

    persistence_score = (
        alerts[persistence_column] / 5.0 * 100.0
    ).clip(0, 100)

    alerts["alert_priority"] = (
        0.35 * alerts["signal_score"]
        + 0.35 * alerts[risk_column]
        + 0.20 * alerts[propagation_column]
        + 0.10 * persistence_score
    ).clip(0, 100).round(2)

    # --------------------------------------------------------
    # Alert level
    # --------------------------------------------------------

    alerts["alert_level"] = np.select(
        [
            (
                (alerts["alert_priority"] >= 80)
                & (alerts[risk_column] >= HIGH_RISK_THRESHOLD)
                & (
                    (alerts[propagation_column] >= 60)
                    | (alerts.get("severity", pd.Series("", index=alerts.index))
                       .astype(str).str.upper() == "HIGH")
                )
            ),
            (
                (alerts["alert_priority"] >= 65)
                | (alerts[risk_column] >= HIGH_RISK_THRESHOLD)
                | (
                    alerts.get("severity", pd.Series("", index=alerts.index))
                    .astype(str).str.upper() == "HIGH"
                )
            ),
            (
                (alerts["alert_priority"] >= 40)
                | (alerts[risk_column] >= MEDIUM_RISK_THRESHOLD)
                | (
                    alerts.get("severity", pd.Series("", index=alerts.index))
                    .astype(str).str.upper() == "MEDIUM"
                )
            ),
        ],
        ["CRITICAL", "HIGH", "MEDIUM"],
        default="LOW",
    )

    # --------------------------------------------------------
    # Alert candidate filter
    #
    # Preserve the source implementation's evidence-based
    # eligibility rather than filtering only by priority.
    # --------------------------------------------------------

    candidate_mask = (
        (alerts["signal_score"] >= SIGNAL_THRESHOLD)
        | (alerts[risk_column] >= HIGH_RISK_THRESHOLD)
        | (
            (alerts[risk_column] >= MEDIUM_RISK_THRESHOLD)
            & (alerts[propagation_column] >= PROPAGATION_THRESHOLD)
        )
        | (
            (alerts["signal_score"] >= 15.0)
            & (alerts[persistence_column] >= PERSISTENCE_THRESHOLD)
        )
    )

    # Candidate filtering is delayed until source_post_count is known.
    # This prevents tiny clusters from becoming alerts solely because
    # they happen to span multiple communities.

    # --------------------------------------------------------
    # Risk type
    # --------------------------------------------------------

    risk_type_column = _find_column(
        alerts,
        [
            "risk_type",
            "risk_category",
            "category",
        ],
    )

    if risk_type_column is None:

        alerts["risk_type"] = "general"
        risk_type_column = "risk_type"

    alerts["risk_type"] = (
        alerts[risk_type_column]
        .fillna("general")
        .astype(str)
    )

    # --------------------------------------------------------
    # Source post count
    # --------------------------------------------------------

    if (
        not clustered_posts.empty
        and cluster_column in clustered_posts.columns
    ):

        source_counts = (
            clustered_posts
            .groupby(cluster_column)
            .size()
            .to_dict()
        )

        alerts["source_post_count"] = (
            alerts[cluster_column]
            .map(source_counts)
            .fillna(0)
            .astype(int)
        )

    elif "cluster_size" in alerts.columns:

        alerts["source_post_count"] = (
            pd.to_numeric(
                alerts["cluster_size"],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

    else:

        alerts["source_post_count"] = 0

    candidate_mask = candidate_mask & (alerts["source_post_count"] >= MIN_ALERT_POSTS)
    alerts = alerts[candidate_mask].copy()

    if alerts.empty:
        return alerts

    # --------------------------------------------------------
    # Generate explanations
    # --------------------------------------------------------

    explanations = []

    for _, row in alerts.iterrows():

        reasons = []

        signal_score = _safe_float(
            row.get("signal_score", 0)
        )

        propagation_score = _safe_float(
            row.get(
                propagation_column,
                0,
            )
        )

        risk_score = _safe_float(
            row.get(
                risk_column,
                0,
            )
        )

        if signal_score >= 75:
            reasons.append(
                "strong signal activity"
            )

        elif signal_score >= 50:
            reasons.append(
                "elevated signal activity"
            )

        if propagation_score >= 75:
            reasons.append(
                "strong cross-community propagation"
            )

        elif propagation_score >= 50:
            reasons.append(
                "significant propagation"
            )

        if risk_score >= 75:
            reasons.append(
                "high risk indicators"
            )

        elif risk_score >= 50:
            reasons.append(
                "elevated risk indicators"
            )

        # Temporal indicators
        growth = _find_column(
            alerts,
            [
                "growth",
                "growth_rate",
                "growth_score",
            ],
        )

        if growth is not None:

            growth_value = _safe_float(
                row.get(growth, 0)
            )

            if growth_value > 0:
                reasons.append(
                    "positive temporal growth"
                )

        persistence = _find_column(
            alerts,
            [
                "persistence",
                "persistence_score",
                "persistence_windows",
            ],
        )

        if persistence is not None:

            persistence_value = _safe_float(
                row.get(persistence, 0)
            )

            if persistence_value > 0:
                reasons.append(
                    "persistent activity"
                )

        if not reasons:
            reasons.append(
                "multiple signal indicators exceeded threshold"
            )

        explanation = (
            "Alert triggered by "
            + ", ".join(reasons)
            + "."
        )

        explanations.append(explanation)

    alerts["explanation"] = explanations

    # --------------------------------------------------------
    # Alert IDs
    # --------------------------------------------------------

    alerts = alerts.reset_index(drop=True)

    alerts.insert(
        0,
        "alert_id",
        [
            f"SF-{index + 1:05d}"
            for index in range(len(alerts))
        ],
    )

    # --------------------------------------------------------
    # Sort by priority
    # --------------------------------------------------------

    alerts = alerts.sort_values(
        "alert_priority",
        ascending=False,
    ).reset_index(drop=True)

    return alerts


# ============================================================
# ALERT EXPORT
# ============================================================


def export_alerts(
    alerts,
    output_path=ALERT_FILE,
):
    """Export generated alerts to CSV."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if alerts is None:
        alerts = pd.DataFrame()

    if not isinstance(
        alerts,
        pd.DataFrame,
    ):
        alerts = pd.DataFrame(alerts)

    alerts.to_csv(
        output_path,
        index=False,
    )

    print("\n" + "=" * 60)
    print("ALERTS EXPORTED")
    print("=" * 60)
    print(f"Rows : {len(alerts):,}")
    print(f"File : {output_path}")
    print("=" * 60)

    return output_path