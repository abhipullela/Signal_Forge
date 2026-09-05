"""Semantic embedding generation for SignalForge."""

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# LOAD MODEL
# ============================================================

def load_embedding_model(model_name=MODEL_NAME):
    """Load the SentenceTransformer model."""

    print(
        f"Loading SentenceTransformer: {model_name}"
    )

    model = SentenceTransformer(model_name)

    print("Embedding model loaded.")

    return model


# ============================================================
# BUILD TEXT
# ============================================================

def build_embedding_text(posts):
    """
    Build the text representation used for semantic embeddings.

    Each post is represented using:

        title + content

    Returns:
        list[str]
    """

    texts = []

    for post in posts:

        title = post.get("title") or ""
        content = post.get("content") or ""

        text = (
            f"{title} {content}"
            .strip()
        )

        texts.append(text)

    return texts


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(
    posts,
    model,
    batch_size=32,
):
    """
    Generate normalized semantic embeddings
    for the supplied posts.

    Parameters
    ----------
    posts : list[dict]
        Posts containing title and content.

    model : SentenceTransformer
        Loaded embedding model.

    batch_size : int
        Number of posts encoded at once.

    Returns
    -------
    numpy.ndarray
        Normalized semantic embeddings.
    """

    if not posts:
        raise ValueError(
            "No posts supplied for embedding generation."
        )

    texts = build_embedding_text(posts)

    print(
        f"\nGenerating embeddings for "
        f"{len(texts):,} posts..."
    )

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    print("\nEmbeddings:")
    print(
        f"  Shape: {embeddings.shape}"
    )

    print(
        f"  Dtype: {embeddings.dtype}"
    )

    return embeddings