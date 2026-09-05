"""Text cleaning utilities for SignalForge preprocessing."""

import re

import pandas as pd


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Clean and normalize a single text value.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        "",
        text,
    )

    # Remove Reddit-style deleted/removed content
    text = re.sub(
        r"\[deleted\]|\[removed\]",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip().lower()


# ============================================================
# CREATE CLEAN TEXT COLUMNS
# ============================================================

def create_clean_text(df):
    """
    Create clean_title and clean_content columns.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    df = df.copy()

    if "title" not in df.columns:
        raise ValueError(
            "Required column 'title' is missing."
        )

    if "content" not in df.columns:
        raise ValueError(
            "Required column 'content' is missing."
        )

    df["clean_title"] = (
        df["title"]
        .apply(normalize_text)
    )

    df["clean_content"] = (
        df["content"]
        .apply(normalize_text)
    )

    return df


# ============================================================
# CHECK UNUSABLE POSTS
# ============================================================

def is_unusable_text(text):
    """
    Return True if a text field contains no usable content.
    """

    if pd.isna(text):
        return True

    text = str(text).strip()

    return len(text) == 0


def filter_unusable_posts(df):
    """
    Remove posts where both title and content are unusable.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if (
        "clean_title" not in df.columns
        or "clean_content" not in df.columns
    ):
        raise ValueError(
            "clean_title and clean_content must exist "
            "before filtering."
        )

    df = df.copy()

    before_count = len(df)

    unusable_title = (
        df["clean_title"]
        .apply(is_unusable_text)
    )

    unusable_content = (
        df["clean_content"]
        .apply(is_unusable_text)
    )

    # Remove only when BOTH title and content are empty
    unusable = (
        unusable_title
        & unusable_content
    )

    removed_count = unusable.sum()

    df = (
        df.loc[~unusable]
        .reset_index(drop=True)
    )

    print("\n" + "-" * 70)
    print("TEXT VALIDATION")
    print("-" * 70)

    print(f"Posts before : {before_count}")
    print(f"Removed      : {removed_count}")
    print(f"Posts after  : {len(df)}")

    return df


# ============================================================
# CREATE EMBEDDING TEXT
# ============================================================

def create_embedding_text(df):
    """
    Combine cleaned title and content into the text that will
    later be passed to the embedding model.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame."
        )

    if (
        "clean_title" not in df.columns
        or "clean_content" not in df.columns
    ):
        raise ValueError(
            "clean_title and clean_content are required."
        )

    df = df.copy()

    title = (
        df["clean_title"]
        .fillna("")
        .astype(str)
    )

    content = (
        df["clean_content"]
        .fillna("")
        .astype(str)
    )

    df["embedding_text"] = (
        title + " " + content
    ).str.strip()

    return df