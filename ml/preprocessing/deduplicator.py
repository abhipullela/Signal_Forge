"""Duplicate removal utilities for SignalForge preprocessing."""

import pandas as pd


# ============================================================
# DUPLICATE REMOVAL
# ============================================================

def remove_duplicates(df):
    """
    Remove duplicate Reddit posts.

    Priority:
        1. external_id
        2. post_id
        3. complete-row duplication

    Returns:
        pandas.DataFrame
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if df.empty:
        print("Deduplication skipped: dataset is empty.")
        return df.copy()

    before_count = len(df)

    # --------------------------------------------------------
    # 1. Prefer Reddit external ID
    # --------------------------------------------------------

    if "external_id" in df.columns:

        valid_external_id = (
            df["external_id"]
            .notna()
            & df["external_id"]
            .astype(str)
            .str.strip()
            .ne("")
        )

        duplicate_mask = (
            valid_external_id
            & df["external_id"].duplicated(
                keep="first"
            )
        )

        df = df.loc[~duplicate_mask].copy()

    # --------------------------------------------------------
    # 2. Remove duplicate internal post IDs
    # --------------------------------------------------------

    elif "post_id" in df.columns:

        valid_post_id = (
            df["post_id"].notna()
        )

        duplicate_mask = (
            valid_post_id
            & df["post_id"].duplicated(
                keep="first"
            )
        )

        df = df.loc[~duplicate_mask].copy()

    # --------------------------------------------------------
    # 3. Final exact-row duplicate check
    # --------------------------------------------------------

    df = df.drop_duplicates(
        keep="first"
    ).copy()

    # --------------------------------------------------------
    # 4. Reset index
    # --------------------------------------------------------

    df = df.reset_index(drop=True)

    removed_count = before_count - len(df)

    # --------------------------------------------------------
    # 5. Summary
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("DEDUPLICATION")
    print("-" * 70)

    print(f"Posts before : {before_count}")
    print(f"Duplicates   : {removed_count}")
    print(f"Posts after  : {len(df)}")

    return df