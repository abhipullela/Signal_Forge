"""Input validation utilities for SignalForge ingestion."""

from datetime import datetime


# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {
    "post_id",
    "source_id",
    "community_id",
    "external_id",
    "title",
    "content",
    "published_at",
    "permalink",
    "url",
    "domain",
    "score",
}


# ============================================================
# VALIDATE STRUCTURE
# ============================================================

def validate_posts(posts):
    """
    Validate posts returned by ingestion/loaders.py.

    This function checks the raw structure of the data before
    it enters the preprocessing pipeline.

    It does NOT clean, modify, or transform the posts.
    """

    # --------------------------------------------------------
    # 1. Check container type
    # --------------------------------------------------------

    if not isinstance(posts, list):
        raise TypeError(
            "Invalid posts object. "
            "Expected a list of dictionaries."
        )

    # --------------------------------------------------------
    # 2. Check whether data was loaded
    # --------------------------------------------------------

    if not posts:
        raise ValueError(
            "No posts were loaded from the database."
        )

    # --------------------------------------------------------
    # 3. Check every post is a dictionary
    # --------------------------------------------------------

    invalid_posts = [
        index
        for index, post in enumerate(posts)
        if not isinstance(post, dict)
    ]

    if invalid_posts:
        raise TypeError(
            f"Invalid post records at indexes: "
            f"{invalid_posts[:10]}"
        )

    # --------------------------------------------------------
    # 4. Check required fields
    # --------------------------------------------------------

    missing_fields = set()

    for post in posts:
        missing_fields.update(
            REQUIRED_FIELDS - set(post.keys())
        )

    if missing_fields:
        raise ValueError(
            "Missing required fields: "
            f"{sorted(missing_fields)}"
        )

    # --------------------------------------------------------
    # 5. Check important identifier fields
    # --------------------------------------------------------

    identifier_fields = [
        "post_id",
        "external_id",
        "community_id",
        "source_id",
    ]

    for field in identifier_fields:

        missing_values = sum(
            post.get(field) is None
            for post in posts
        )

        if missing_values:
            print(
                f"WARNING: {missing_values} posts have "
                f"missing {field}"
            )

    # --------------------------------------------------------
    # 6. Check timestamp field
    # --------------------------------------------------------

    missing_timestamps = sum(
        post.get("published_at") is None
        for post in posts
    )

    if missing_timestamps:
        print(
            f"WARNING: {missing_timestamps} posts have "
            f"missing published_at"
        )

    # --------------------------------------------------------
    # 7. Check text fields
    # --------------------------------------------------------

    missing_title = sum(
        post.get("title") is None
        for post in posts
    )

    missing_content = sum(
        post.get("content") is None
        for post in posts
    )

    if missing_title:
        print(
            f"WARNING: {missing_title} posts have "
            f"missing title"
        )

    if missing_content:
        print(
            f"WARNING: {missing_content} posts have "
            f"missing content"
        )

    # --------------------------------------------------------
    # 8. Validation summary
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("INGESTION VALIDATION")
    print("-" * 70)

    print("Structure          : PASSED")
    print("Required fields    : PASSED")
    print(f"Posts validated    : {len(posts)}")

    print("-" * 70)

    return True


# ============================================================
# VALIDATE SINGLE POST
# ============================================================

def validate_post(post):
    """
    Validate a single post record.
    """

    if not isinstance(post, dict):
        raise TypeError(
            "Post must be a dictionary."
        )

    missing_fields = (
        REQUIRED_FIELDS - set(post.keys())
    )

    if missing_fields:
        raise ValueError(
            "Post is missing fields: "
            f"{sorted(missing_fields)}"
        )

    return True