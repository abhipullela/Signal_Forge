"""Normalization utilities for SignalForge preprocessing."""

import pandas as pd


# ============================================================
# TEXT LENGTH
# ============================================================

def create_text_length(df):
    """
    Calculate the character length of embedding_text.

    This provides a basic numerical feature for downstream
    analysis.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if "embedding_text" not in df.columns:
        raise ValueError(
            "Required column 'embedding_text' is missing."
        )

    df = df.copy()

    df["text_length"] = (
        df["embedding_text"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    return df


# ============================================================
# NORMALIZE NUMERICAL FEATURES
# ============================================================

def normalize_numeric_columns(df, columns):
    """
    Min-max normalize selected numerical columns.

    Values are scaled to the range [0, 1].

    Constant columns are assigned 0.0 to avoid division
    by zero.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    df = df.copy()

    for column in columns:

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' is missing."
            )

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        minimum = numeric_values.min()
        maximum = numeric_values.max()

        if pd.isna(minimum) or pd.isna(maximum):
            df[column] = 0.0
            continue

        if maximum == minimum:
            df[column] = 0.0
        else:
            df[column] = (
                (numeric_values - minimum)
                / (maximum - minimum)
            )

    return df