"""Temporal signal analysis for SignalForge.

Reads:
    outputs/clustered_posts.csv

Produces:
    outputs/temporal_features.csv

Pipeline:
    load/validate
    -> recent analysis window
    -> weekly cluster aggregation
    -> volume dynamics
    -> engagement dynamics
    -> community dynamics
    -> rolling baseline
    -> anomaly score
    -> persistence
    -> activity filtering
    -> normalization
    -> transparent signal score
    -> ranking
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

# Repository root:
#
# Signal_Forge/
# ├── ml/
# │   └── detection/
# │       └── temporal_detector.py
# └── outputs/
#
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "clustered_posts.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "temporal_features.csv"
)


# ============================================================
# ANALYSIS CONFIGURATION
# ============================================================

# Analyze the final 180 days represented in the dataset.
ANALYSIS_DAYS = 180

# Each post is assigned to a weekly bucket.
TIME_WINDOW = "7D"

# Prevent tiny clusters from receiving huge percentage-growth
# scores based on only one or two posts.
MIN_TOTAL_POSTS = 5
MIN_ACTIVE_WINDOWS = 2

# Number of previous weekly windows used for the rolling baseline.
# The current window is excluded from its own baseline.
BASELINE_WINDOWS = 8


# ============================================================
# SIGNAL SCORING WEIGHTS
# ============================================================

# The current dataset contains only one community, so community
# spread receives very little weight for now.

SIGNAL_WEIGHTS = {
    "growth_score": 0.20,
    "velocity_score": 0.15,
    "acceleration_score": 0.15,
    "engagement_score": 0.15,
    "anomaly_score_normalized": 0.20,
    "persistence_score": 0.14,
    "community_spread_score": 0.01,
}

EPSILON = 1e-9


# ============================================================
# SIGNAL STATUS THRESHOLDS
# ============================================================

HIGH_THRESHOLD = 70
MEDIUM_THRESHOLD = 40


# ============================================================
# SECTION HELPER
# ============================================================

def section(title):
    """Print a readable terminal section heading."""

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# 1. LOAD + VALIDATE
# ============================================================

def load_clustered_posts():
    """
    Load the semantic-clustering output.

    The semantic clustering stage already preserves:

        post_id / id
        community_id
        published_at
        score
        cluster_id

    We do NOT recluster here.
    """

    section("1. LOADING CLUSTERED POSTS")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find:\n{INPUT_FILE}\n\n"
            "Run the semantic clustering stage first."
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    required = [
        "id",
        "community_id",
        "published_at",
        "score",
        "cluster_id",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing
            )
        )

    # --------------------------------------------------------
    # Convert timestamps
    # --------------------------------------------------------

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True,
    )

    bad_dates = (
        df["published_at"]
        .isna()
        .sum()
    )

    if bad_dates:
        print(
            f"Removing {bad_dates:,} rows "
            "with invalid timestamps."
        )

        df = df.dropna(
            subset=["published_at"]
        ).copy()

    # --------------------------------------------------------
    # Validate cluster IDs
    # --------------------------------------------------------

    df["cluster_id"] = pd.to_numeric(
        df["cluster_id"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["cluster_id"]
    ).copy()

    df["cluster_id"] = (
        df["cluster_id"]
        .astype(int)
    )

    # --------------------------------------------------------
    # Score / engagement
    # --------------------------------------------------------

    df["score"] = pd.to_numeric(
        df["score"],
        errors="coerce",
    ).fillna(0)

    # --------------------------------------------------------
    # Community IDs
    # --------------------------------------------------------

    df["community_id"] = (
        df["community_id"]
        .fillna("unknown")
        .astype(str)
    )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = (
        df.sort_values(
            "published_at"
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"Rows loaded: {len(df):,}"
    )

    print(
        f"Date range: "
        f"{df['published_at'].min()} "
        f"-> "
        f"{df['published_at'].max()}"
    )

    print(
        f"Clusters: "
        f"{df['cluster_id'].nunique():,}"
    )

    print(
        f"Communities: "
        f"{df['community_id'].nunique():,}"
    )

    return df


# ============================================================
# 2. SELECT RECENT ANALYSIS WINDOW
# ============================================================

def select_analysis_window(df):
    """
    Analyze only the final ANALYSIS_DAYS represented in the data.

    A topic existing for many years should not automatically
    become an emerging signal simply because it has many posts.
    """

    section(
        "2. SELECTING ANALYSIS WINDOW"
    )

    end = df[
        "published_at"
    ].max()

    start = (
        end
        - pd.Timedelta(
            days=ANALYSIS_DAYS
        )
    )

    window = df[
        (
            df["published_at"]
            >= start
        )
        &
        (
            df["published_at"]
            <= end
        )
        &
        (
            df["cluster_id"]
            != -1
        )
    ].copy()

    print(
        f"Window: {start} -> {end}"
    )

    print(
        f"Posts in window: "
        f"{len(window):,}"
    )

    print(
        "Posts after excluding "
        f"semantic noise: {len(window):,}"
    )

    print(
        f"Usable clusters: "
        f"{window['cluster_id'].nunique():,}"
    )

    if window.empty:
        raise ValueError(
            "No usable clustered posts "
            "in the analysis window."
        )

    return window


# ============================================================
# 3. CREATE TIME WINDOWS
# ============================================================

def create_time_windows(df):
    """
    Convert every post timestamp into a fixed time bucket.

    With TIME_WINDOW = '7D', posts are grouped into
    weekly windows.
    """

    section(
        "3. CREATING TIME WINDOWS"
    )

    df = df.copy()

    df["time_window"] = (
        df["published_at"]
        .dt.floor(TIME_WINDOW)
    )

    print(
        f"Window size: {TIME_WINDOW}"
    )

    print(
        f"Unique windows: "
        f"{df['time_window'].nunique():,}"
    )

    return df


# ============================================================
# 4. CLUSTER-TIME AGGREGATION
# ============================================================

def aggregate_cluster_time(df):
    """
    Build the core temporal dataset.

    One row represents:

        one semantic cluster
        during one time window

    Features:

        volume
        engagement
        average engagement
        community count
    """

    section(
        "4. AGGREGATING CLUSTERS OVER TIME"
    )

    result = (
        df.groupby(
            [
                "cluster_id",
                "time_window",
            ],
            as_index=False,
        )
        .agg(
            volume=(
                "id",
                "count",
            ),
            engagement=(
                "score",
                "sum",
            ),
            average_engagement=(
                "score",
                "mean",
            ),
            community_count=(
                "community_id",
                "nunique",
            ),
        )
        .sort_values(
            [
                "cluster_id",
                "time_window",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"Cluster/time rows: "
        f"{len(result):,}"
    )

    return result


# ============================================================
# 5. COMPLETE ZERO-ACTIVITY WINDOWS
# ============================================================

def complete_time_series(df):
    """
    Add explicit zero rows when a cluster had no posts
    during a time window.

    This makes velocity and acceleration meaningful.
    """

    section(
        "5. COMPLETING MISSING TIME WINDOWS"
    )

    times = pd.date_range(
        df["time_window"].min(),
        df["time_window"].max(),
        freq=TIME_WINDOW,
    )

    clusters = sorted(
        df["cluster_id"].unique()
    )

    index = pd.MultiIndex.from_product(
        [
            clusters,
            times,
        ],
        names=[
            "cluster_id",
            "time_window",
        ],
    )

    result = (
        df.set_index(
            [
                "cluster_id",
                "time_window",
            ]
        )
        .reindex(index)
        .reset_index()
    )

    numeric_columns = [
        "volume",
        "engagement",
        "average_engagement",
        "community_count",
    ]

    for column in numeric_columns:
        result[column] = (
            result[column]
            .fillna(0)
        )

    print(
        f"Completed rows: "
        f"{len(result):,}"
    )

    return result


# ============================================================
# 6. VOLUME DYNAMICS
# ============================================================

def calculate_volume_dynamics(df):
    """
    Calculate:

        velocity
        growth_rate
        acceleration

    Logarithmic growth is used instead of ordinary percentage
    growth so that zero-to-positive transitions do not cause
    division-by-zero or enormous percentages.
    """

    section(
        "6. VOLUME DYNAMICS"
    )

    df = df.copy()

    previous_volume = (
        df.groupby(
            "cluster_id"
        )["volume"]
        .shift(1)
        .fillna(0)
    )

    # --------------------------------------------------------
    # Velocity
    # --------------------------------------------------------

    df["velocity"] = (
        df["volume"]
        - previous_volume
    )

    # --------------------------------------------------------
    # Logarithmic growth
    # --------------------------------------------------------

    df["growth_rate"] = (
        np.log1p(
            df["volume"]
        )
        -
        np.log1p(
            previous_volume
        )
    )

    df["growth_rate"] = (
        df["growth_rate"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------

    previous_velocity = (
        df.groupby(
            "cluster_id"
        )["velocity"]
        .shift(1)
        .fillna(0)
    )

    df["acceleration"] = (
        df["velocity"]
        - previous_velocity
    )

    return df


# ============================================================
# 7. ENGAGEMENT DYNAMICS
# ============================================================

def calculate_engagement_dynamics(df):
    """
    Treat PostgreSQL 'score' as the available engagement field.

    Calculates:

        engagement_velocity
        engagement_growth
    """

    section(
        "7. ENGAGEMENT DYNAMICS"
    )

    df = df.copy()

    previous = (
        df.groupby(
            "cluster_id"
        )["engagement"]
        .shift(1)
    )

    df["engagement_velocity"] = (
        df["engagement"]
        - previous
    ).fillna(0)

    df["engagement_growth"] = (
        (
            df["engagement"]
            - previous
        )
        /
        (
            previous
            + EPSILON
        )
    )

    df["engagement_growth"] = (
        df["engagement_growth"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
    )

    return df


# ============================================================
# 8. COMMUNITY DYNAMICS
# ============================================================

def calculate_community_dynamics(df):
    """
    Calculate community velocity.

    The current dataset has one community, so this feature
    will have limited variation. It remains in the pipeline
    for future multi-community data.
    """

    section(
        "8. COMMUNITY DYNAMICS"
    )

    df = df.copy()

    previous = (
        df.groupby(
            "cluster_id"
        )["community_count"]
        .shift(1)
    )

    df["community_velocity"] = (
        df["community_count"]
        - previous
    ).fillna(0)

    return df


# ============================================================
# 9. ROLLING HISTORICAL BASELINE
# ============================================================

def calculate_baseline(df):
    """
    Calculate the recent normal activity level for each cluster.

    The current window is excluded from its own baseline.
    """

    section(
        "9. HISTORICAL BASELINE"
    )

    df = df.copy()

    shifted = (
        df.groupby(
            "cluster_id"
        )["volume"]
        .shift(1)
    )

    df["baseline_volume"] = (
        shifted
        .groupby(
            df["cluster_id"]
        )
        .rolling(
            BASELINE_WINDOWS,
            min_periods=3,
        )
        .mean()
        .reset_index(
            level=0,
            drop=True,
        )
        .fillna(0)
    )

    df["baseline_std"] = (
        shifted
        .groupby(
            df["cluster_id"]
        )
        .rolling(
            BASELINE_WINDOWS,
            min_periods=3,
        )
        .std()
        .reset_index(
            level=0,
            drop=True,
        )
        .fillna(0)
    )

    return df


# ============================================================
# 10. ANOMALY SCORE
# ============================================================

def calculate_anomaly(df):
    """
    Calculate an anomaly score based on deviation from the
    historical cluster baseline.

    If the baseline standard deviation is zero but current
    activity is above the baseline, absolute increase is used.
    """

    section(
        "10. ANOMALY DETECTION"
    )

    df = df.copy()

    normal_std = (
        df["baseline_std"]
        > EPSILON
    )

    df["anomaly_score"] = 0.0

    # --------------------------------------------------------
    # Normal z-score-like anomaly
    # --------------------------------------------------------

    df.loc[
        normal_std,
        "anomaly_score",
    ] = (
        (
            df.loc[
                normal_std,
                "volume",
            ]
            -
            df.loc[
                normal_std,
                "baseline_volume",
            ]
        )
        /
        df.loc[
            normal_std,
            "baseline_std",
        ]
    )

    # --------------------------------------------------------
    # Stable baseline but increased activity
    # --------------------------------------------------------

    zero_std_activity = (
        (~normal_std)
        &
        (
            df["volume"]
            >
            df["baseline_volume"]
        )
    )

    df.loc[
        zero_std_activity,
        "anomaly_score",
    ] = (
        df.loc[
            zero_std_activity,
            "volume",
        ]
        -
        df.loc[
            zero_std_activity,
            "baseline_volume",
        ]
    )

    df["anomaly_score"] = (
        df["anomaly_score"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
    )

    df["positive_anomaly_score"] = (
        df["anomaly_score"]
        .clip(lower=0)
    )

    return df


# ============================================================
# 11. PERSISTENCE
# ============================================================

def calculate_persistence(df):
    """
    Count consecutive windows in which activity is above baseline.

    Example:

        above baseline:
        False, True, True, True, False

        persistence:
        0, 1, 2, 3, 0
    """

    section(
        "11. PERSISTENCE"
    )

    df = df.copy()

    df["above_baseline"] = (
        (
            df["volume"]
            >
            df["baseline_volume"]
        )
        &
        (
            df["baseline_volume"]
            > 0
        )
    )

    persistence = pd.Series(
        0.0,
        index=df.index,
    )

    # Work cluster by cluster.
    for (
        cluster_id,
        indices,
    ) in df.groupby(
        "cluster_id"
    ).groups.items():

        count = 0

        for index in indices:

            if df.loc[
                index,
                "above_baseline",
            ]:

                count += 1

            else:

                count = 0

            persistence.loc[
                index
            ] = count

    df["persistence_windows"] = (
        persistence
    )

    # --------------------------------------------------------
    # FIX:
    # The original version returned before creating
    # persistence_score. That made the scoring stage unable
    # to use persistence properly.
    # --------------------------------------------------------

    df["persistence_score"] = (
        df["persistence_windows"]
        .clip(
            lower=0,
            upper=3,
        )
        / 3.0
    )

    return df


# ============================================================
# 12. ACTIVITY FILTER
# ============================================================

def get_eligible_clusters(df):
    """
    Remove clusters with insufficient evidence.

    Requirements:

        total_posts >= MIN_TOTAL_POSTS
        active_windows >= MIN_ACTIVE_WINDOWS
    """

    section(
        "12. ACTIVITY FILTER"
    )

    stats = (
        df.groupby(
            "cluster_id"
        )
        .agg(
            total_posts=(
                "volume",
                "sum",
            ),
            active_windows=(
                "volume",
                lambda x: int(
                    (x > 0).sum()
                ),
            ),
            max_volume=(
                "volume",
                "max",
            ),
        )
        .reset_index()
    )

    eligible = stats[
        (
            stats["total_posts"]
            >= MIN_TOTAL_POSTS
        )
        &
        (
            stats["active_windows"]
            >= MIN_ACTIVE_WINDOWS
        )
    ].copy()

    print(
        f"Clusters before filtering: "
        f"{len(stats):,}"
    )

    print(
        f"Eligible clusters: "
        f"{len(eligible):,}"
    )

    return stats, eligible


# ============================================================
# 13. NORMALIZATION
# ============================================================

def min_max(series):
    """
    Normalize a numeric Series to 0-1.
    """

    series = series.astype(float)

    if series.empty:
        return pd.Series(
            0.0,
            index=series.index,
        )

    low = series.min()
    high = series.max()

    if (
        pd.isna(low)
        or pd.isna(high)
        or abs(high - low)
        < EPSILON
    ):
        return pd.Series(
            0.0,
            index=series.index,
        )

    return (
        series - low
    ) / (
        high - low
    )


def create_scoring_features(
    df,
    eligible,
):
    """
    Take the latest observation for every eligible cluster.

    We rank the current state of each cluster at the end
    of the selected analysis period.
    """

    section(
        "13. NORMALIZING SCORING FEATURES"
    )

    eligible_ids = set(
        eligible[
            "cluster_id"
        ]
    )

    working = df[
        df["cluster_id"]
        .isin(eligible_ids)
    ].copy()

    if working.empty:
        raise ValueError(
            "No clusters passed "
            "the activity filters."
        )

    latest = (
        working
        .sort_values(
            [
                "cluster_id",
                "time_window",
            ]
        )
        .groupby(
            "cluster_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    latest["positive_growth"] = (
        latest["growth_rate"]
        .clip(lower=0)
    )

    latest["growth_score"] = (
        min_max(
            np.log1p(
                latest[
                    "positive_growth"
                ]
            )
        )
    )

    # --------------------------------------------------------
    # Velocity
    # --------------------------------------------------------

    latest["positive_velocity"] = (
        latest["velocity"]
        .clip(lower=0)
    )

    latest["velocity_score"] = (
        min_max(
            latest[
                "positive_velocity"
            ]
        )
    )

    # --------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------

    latest[
        "positive_acceleration"
    ] = (
        latest[
            "acceleration"
        ]
        .clip(lower=0)
    )

    latest[
        "acceleration_score"
    ] = min_max(
        latest[
            "positive_acceleration"
        ]
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    latest["log_engagement"] = (
        np.log1p(
            latest[
                "engagement"
            ].clip(lower=0)
        )
    )

    latest["engagement_score"] = (
        min_max(
            latest[
                "log_engagement"
            ]
        )
    )

    # --------------------------------------------------------
    # Anomaly
    # --------------------------------------------------------

    latest[
        "anomaly_score_normalized"
    ] = min_max(
        np.log1p(
            latest[
                "positive_anomaly_score"
            ]
        )
    )

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    latest[
        "persistence_score"
    ] = min_max(
        latest[
            "persistence_windows"
        ]
    )

    # --------------------------------------------------------
    # Community spread
    # --------------------------------------------------------

    latest[
        "community_spread_score"
    ] = min_max(
        latest[
            "community_velocity"
        ].clip(lower=0)
    )

    return latest


# ============================================================
# 14. SIGNAL SCORE
# ============================================================

def calculate_signal_score(df):
    """
    Calculate the final emerging-signal score on a 0-100 scale.

    The weighted normalized features form the raw score.

    Persistence is then applied as a multiplier:

        <= 1 window : 0.50
        2 windows   : 0.75
        >= 3 windows: 1.00

    Status thresholds:

        LOW    < 40
        MEDIUM >= 40
        HIGH   >= 70

    Medium/high status also requires persistence.
    """

    section(
        "14. SIGNAL SCORING"
    )

    df = df.copy()

    # --------------------------------------------------------
    # Weighted feature score
    # --------------------------------------------------------

    df["raw_signal_score"] = 0.0

    for (
        feature,
        weight,
    ) in SIGNAL_WEIGHTS.items():

        if feature not in df.columns:
            continue

        df["raw_signal_score"] += (
            df[feature]
            .fillna(0)
            * weight
        )

    # --------------------------------------------------------
    # Convert 0-1 to 0-100
    # --------------------------------------------------------

    df["raw_signal_score"] = (
        df["raw_signal_score"]
        * 100
    ).clip(
        lower=0,
        upper=100,
    )

    # --------------------------------------------------------
    # Persistence multiplier
    # --------------------------------------------------------

    df[
        "persistence_multiplier"
    ] = np.select(
        [
            (
                df[
                    "persistence_windows"
                ]
                <= 1
            ),
            (
                df[
                    "persistence_windows"
                ]
                == 2
            ),
            (
                df[
                    "persistence_windows"
                ]
                >= 3
            ),
        ],
        [
            0.50,
            0.75,
            1.00,
        ],
        default=0.50,
    )

    df["signal_score"] = (
        df["raw_signal_score"]
        *
        df[
            "persistence_multiplier"
        ]
    ).clip(
        lower=0,
        upper=100,
    )

    # --------------------------------------------------------
    # Signal status
    # --------------------------------------------------------

    df["signal_status"] = "LOW"

    medium_mask = (
        (
            df["signal_score"]
            >= MEDIUM_THRESHOLD
        )
        &
        (
            df[
                "persistence_windows"
            ]
            >= 2
        )
    )

    high_mask = (
        (
            df["signal_score"]
            >= HIGH_THRESHOLD
        )
        &
        (
            df[
                "persistence_windows"
            ]
            >= 3
        )
    )

    df.loc[
        medium_mask,
        "signal_status",
    ] = "MEDIUM"

    df.loc[
        high_mask,
        "signal_status",
    ] = "HIGH"

    return df


# ============================================================
# 15. PREPARE OUTPUT
# ============================================================

def prepare_output(
    scored,
    stats,
):
    """
    Merge cluster statistics, rank clusters, and prepare
    the final temporal output.
    """

    section(
        "15. PREPARING OUTPUT"
    )

    output = scored.merge(
        stats,
        on="cluster_id",
        how="left",
    )

    output = (
        output
        .sort_values(
            "signal_score",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    output["signal_rank"] = (
        np.arange(
            1,
            len(output) + 1,
        )
    )

    columns = [
        "signal_rank",
        "cluster_id",
        "time_window",

        "volume",
        "total_posts",
        "active_windows",
        "max_volume",

        "growth_rate",
        "velocity",
        "acceleration",

        "engagement",
        "average_engagement",
        "engagement_growth",
        "engagement_velocity",

        "community_count",
        "community_velocity",

        "baseline_volume",
        "baseline_std",
        "anomaly_score",
        "positive_anomaly_score",

        "persistence_windows",

        "growth_score",
        "velocity_score",
        "acceleration_score",
        "engagement_score",
        "anomaly_score_normalized",
        "persistence_score",
        "community_spread_score",

        "signal_score",
        "signal_status",
    ]

    available_columns = [
        column
        for column in columns
        if column in output.columns
    ]

    return output[
        available_columns
    ]


# ============================================================
# 16. SAVE
# ============================================================

def save_output(output):
    """Save temporal features and signal scores."""

    section(
        "16. SAVING TEMPORAL FEATURES"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print(
        f"Rows: {len(output):,}"
    )


# ============================================================
# 17. PRINT TOP SIGNALS
# ============================================================

def print_top_signals(
    output,
    n=20,
):
    """
    Print the top ranked clusters.

    At this stage we only have cluster IDs.
    """

    section(
        f"17. TOP {n} EMERGING CLUSTERS"
    )

    if output.empty:
        print(
            "No eligible clusters."
        )
        return

    for (
        _,
        row,
    ) in output.head(n).iterrows():

        print(
            f"\n"
            f"Rank:            "
            f"{int(row['signal_rank'])}\n"
            f"Cluster:         "
            f"{int(row['cluster_id'])}\n"
            f"Signal score:    "
            f"{row['signal_score']:.2f}/100\n"
            f"Status:           "
            f"{row['signal_status']}\n"
            f"Latest volume:   "
            f"{row['volume']:.0f}\n"
            f"Growth rate:     "
            f"{row['growth_rate']:.2f}\n"
            f"Velocity:        "
            f"{row['velocity']:.2f}\n"
            f"Acceleration:    "
            f"{row['acceleration']:.2f}\n"
            f"Engagement:      "
            f"{row['engagement']:.2f}\n"
            f"Anomaly:         "
            f"{row['anomaly_score']:.2f}\n"
            f"Persistence:     "
            f"{row['persistence_windows']:.0f} windows\n"
            f"Communities:     "
            f"{row['community_count']:.0f}"
        )


# ============================================================
# MAIN
# ============================================================

def main():
    """Run the complete Temporal Analysis V1 pipeline."""

    print(
        "\nSignalForge Temporal Analysis V1"
    )

    print(
        "=" * 70
    )

    print(
        f"Input : {INPUT_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # 1. Load clustered posts
    # --------------------------------------------------------

    df = load_clustered_posts()

    # --------------------------------------------------------
    # 2. Select recent analysis window
    # --------------------------------------------------------

    df = select_analysis_window(
        df
    )

    # --------------------------------------------------------
    # 3. Create weekly time windows
    # --------------------------------------------------------

    df = create_time_windows(
        df
    )

    # --------------------------------------------------------
    # 4. Aggregate clusters over time
    # --------------------------------------------------------

    temporal = aggregate_cluster_time(
        df
    )

    # --------------------------------------------------------
    # 5. Add zero-activity windows
    # --------------------------------------------------------

    temporal = complete_time_series(
        temporal
    )

    # --------------------------------------------------------
    # 6. Volume dynamics
    # --------------------------------------------------------

    temporal = calculate_volume_dynamics(
        temporal
    )

    # --------------------------------------------------------
    # 7. Engagement dynamics
    # --------------------------------------------------------

    temporal = calculate_engagement_dynamics(
        temporal
    )

    # --------------------------------------------------------
    # 8. Community dynamics
    # --------------------------------------------------------

    temporal = calculate_community_dynamics(
        temporal
    )

    # --------------------------------------------------------
    # 9. Historical baseline
    # --------------------------------------------------------

    temporal = calculate_baseline(
        temporal
    )

    # --------------------------------------------------------
    # 10. Anomaly detection
    # --------------------------------------------------------

    temporal = calculate_anomaly(
        temporal
    )

    # --------------------------------------------------------
    # 11. Persistence
    # --------------------------------------------------------

    temporal = calculate_persistence(
        temporal
    )

    # --------------------------------------------------------
    # 12. Activity filtering
    # --------------------------------------------------------

    stats, eligible = (
        get_eligible_clusters(
            temporal
        )
    )

    # --------------------------------------------------------
    # 13. Feature normalization
    # --------------------------------------------------------

    scored = create_scoring_features(
        temporal,
        eligible,
    )

    # --------------------------------------------------------
    # 14. Signal scoring
    # --------------------------------------------------------

    scored = calculate_signal_score(
        scored
    )

    # --------------------------------------------------------
    # 15. Prepare final output
    # --------------------------------------------------------

    output = prepare_output(
        scored,
        stats,
    )

    # --------------------------------------------------------
    # 16. Save output
    # --------------------------------------------------------

    save_output(
        output
    )

    # --------------------------------------------------------
    # 17. Print top signals
    # --------------------------------------------------------

    print_top_signals(
        output
    )

    section(
        "TEMPORAL ANALYSIS COMPLETE"
    )

    print(
        f"Eligible clusters scored: "
        f"{len(output):,}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()