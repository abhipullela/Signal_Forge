"""Main preprocessing pipeline for SignalForge."""

import os
import pandas as pd

from ml.ingestion.loaders import (
    connect_to_database,
    load_posts,
)

from ml.ingestion.validators import (
    validate_posts,
)

from ml.preprocessing.deduplicator import (
    remove_duplicates,
)

from ml.preprocessing.timestamp_processor import (
    process_timestamps,
    add_time_features,
)

from ml.preprocessing.text_cleaner import (
    create_clean_text,
    filter_unusable_posts,
    create_embedding_text,
)

from ml.preprocessing.normalizer import (
    create_text_length,
)


# ============================================================
# PREPROCESS POSTS
# ============================================================

def preprocess_posts(posts):
    """
    Run the complete SignalForge preprocessing pipeline.

    Input:
        posts - list of dictionaries returned by ingestion

    Output:
        pandas DataFrame containing cleaned and prepared posts
    """

    if not posts:
        raise ValueError(
            "Cannot preprocess an empty post collection."
        )

    # --------------------------------------------------------
    # Convert ingestion output to DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(posts)

    original_count = len(df)

    print("\n" + "=" * 70)
    print("SIGNALFORGE PREPROCESSING")
    print("=" * 70)

    print(
        f"Posts received: {original_count}"
    )

    # --------------------------------------------------------
    # 1. REMOVE DUPLICATES
    # --------------------------------------------------------

    print("\n[1/5] Removing duplicates...")

    df = remove_duplicates(df)

    # --------------------------------------------------------
    # 2. PROCESS TIMESTAMPS
    # --------------------------------------------------------

    print("\n[2/5] Processing timestamps...")

    df = process_timestamps(df)

    # --------------------------------------------------------
    # 3. ADD TIME FEATURES
    # --------------------------------------------------------

    print("\n[3/5] Adding temporal features...")

    df = add_time_features(df)

    # --------------------------------------------------------
    # 4. CLEAN TEXT
    # --------------------------------------------------------

    print("\n[4/5] Cleaning text...")

    df = create_clean_text(df)

    df = filter_unusable_posts(df)

    df = create_embedding_text(df)

    # --------------------------------------------------------
    # 5. CREATE BASIC NUMERICAL FEATURES
    # --------------------------------------------------------

    print("\n[5/5] Creating text features...")

    df = create_text_length(df)

    # --------------------------------------------------------
    # FINAL SORT
    # --------------------------------------------------------

    df = (
        df.sort_values("published_at")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("PREPROCESSING SUMMARY")
    print("-" * 70)

    print(
        f"Original posts : {original_count}"
    )

    print(
        f"Final posts    : {len(df)}"
    )

    print(
        f"Removed        : {original_count - len(df)}"
    )

    print(
        f"Output columns : {len(df.columns)}"
    )

    print("-" * 70)

    return df


# ============================================================
# DATABASE PIPELINE
# ============================================================

def run_database_preprocessing():
    """
    Load posts from PostgreSQL, validate them, and run
    preprocessing.
    """

    # --------------------------------------------------------
    # INGESTION
    # --------------------------------------------------------

    conn = connect_to_database()

    try:
        posts = load_posts(conn)
    finally:
        conn.close()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validate_posts(posts)

    # --------------------------------------------------------
    # PREPROCESSING
    # --------------------------------------------------------

    return preprocess_posts(posts)


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_processed_data(
    df,
    output_path="outputs/cleaned_posts.csv",
):
    """
    Save processed posts to CSV.
    """

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True,
        )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nProcessed data saved to: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = run_database_preprocessing()

    save_processed_data(df)

    print("\n" + "=" * 70)
    print("PREPROCESSING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()