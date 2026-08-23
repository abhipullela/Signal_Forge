"""Semantic embedding generation for SignalForge."""

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model(model_name=MODEL_NAME):
    """Load the SentenceTransformer model."""

    print(
        f"Loading SentenceTransformer: {model_name}"
    )

    return SentenceTransformer(model_name)


def create_embeddings(posts, model):
    """
    Generate normalized semantic embeddings
    for the supplied posts.
    """

    texts = [
        post["text"]
        for post in posts
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    print("\nEmbeddings:")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Dtype: {embeddings.dtype}")

    return embeddings