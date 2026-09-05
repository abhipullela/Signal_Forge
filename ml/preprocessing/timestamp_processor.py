"""Timestamp processing utilities for SignalForge preprocessing."""

import pandas as pd


# ============================================================
# PROCESS TIMESTAMPS
# ============================================================

def process_timestamps(df):
    """
    Convert published_at to UTC datetime, remove invalid
    timestamps, and sort posts chronologically.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if "published_at" not in df.columns:
        raise ValueError(
            "Required column 'published_at' is missing."
        )

    df = df.copy()

    before_count = len(df)

    # --------------------------------------------------------
    # Convert to datetime
    # --------------------------------------------------------

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True,
    )

    # --------------------------------------------------------
    # Remove invalid timestamps
    # --------------------------------------------------------

    invalid_count = df["published_at"].isna().sum()

    if invalid_count > 0:
        print(
            f"Invalid timestamps removed: {invalid_count}"
        )

        df = df.dropna(
            subset=["published_at"]
        )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = (
        df.sort_values(
            "published_at"
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("TIMESTAMP PROCESSING")
    print("-" * 70)

    print(f"Posts before       : {before_count}")
    print(f"Invalid timestamps : {invalid_count}")
    print(f"Posts after        : {len(df)}")

    if not df.empty:
        print(
            f"Time range         : "
            f"{df['published_at'].min()} "
            f"→ "
            f"{df['published_at'].max()}"
        )

    return df


# ============================================================
# ADD TIME FEATURES
# ============================================================

def add_time_features(df):
    """
    Add useful temporal fields derived from published_at.

    These fields are used by downstream temporal analysis.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if "published_at" not in df.columns:
        raise ValueError(
            "Column 'published_at' is required."
        )

    df = df.copy()

    # Make sure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(
        df["published_at"]
    ):
        df["published_at"] = pd.to_datetime(
            df["published_at"],
            errors="coerce",
            utc=True,
        )

    # --------------------------------------------------------
    # Calendar features
    # --------------------------------------------------------

    df["date"] = (
        df["published_at"]
        .dt.date
    )

    df["hour"] = (
        df["published_at"]
        .dt.hour
    )

    df["day"] = (
        df["published_at"]
        .dt.day
    )

    df["month"] = (
        df["published_at"]
        .dt.month
    )

    df["year"] = (
        df["published_at"]
        .dt.year
    )

    # --------------------------------------------------------
    # Useful temporal grouping fields
    # --------------------------------------------------------

    df["day_of_week"] = (
        df["published_at"]
        .dt.dayofweek
    )

    df["week"] = (
        df["published_at"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # Start of the week
    df["week_start"] = (
        df["published_at"]
        .dt.to_period("W")
        .dt.start_time
    )

    # Start of the month
    df["month_start"] = (
        df["published_at"]
        .dt.to_period("M")
        .dt.start_time
    )

    return df