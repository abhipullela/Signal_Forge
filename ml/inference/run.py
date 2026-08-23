"""SignalForge ML inference entry point."""

from collections import Counter

from ml.detection.cluster_detector import (
    cluster_embeddings,
    evaluate_clustering,
    print_clusters,
)
from ml.features.embeddings import (
    create_embeddings,
    load_embedding_model,
)
from ml.ingestion.loaders import (
    connect_to_database,
    load_posts,
)


def run_semantic_clustering():
    """Run the SignalForge semantic clustering stage."""

    print(
        "SignalForge Semantic Clustering"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    model = load_embedding_model()

    # --------------------------------------------------------
    # Connect to database
    # --------------------------------------------------------

    conn = connect_to_database()

    try:

        # ----------------------------------------------------
        # Load posts
        # ----------------------------------------------------

        posts = load_posts(conn)

        if not posts:
            print(
                "No posts found. Nothing to cluster."
            )
            return None

        # ----------------------------------------------------
        # Generate embeddings
        # ----------------------------------------------------

        embeddings = create_embeddings(
            posts,
            model,
        )

        # ----------------------------------------------------
        # Cluster embeddings
        # ----------------------------------------------------

        labels = cluster_embeddings(
            embeddings
        )

        print("\nLABELS:")
        print(labels)

        print("\nUnique labels:")
        print(
            sorted(set(labels))
        )

        print("\nCluster sizes:")
        print(
            Counter(labels)
        )

        # ----------------------------------------------------
        # Display clusters
        # ----------------------------------------------------

        print_clusters(
            posts,
            labels,
        )

        # ----------------------------------------------------
        # Evaluate clustering
        # ----------------------------------------------------

        metrics = evaluate_clustering(
            embeddings,
            labels,
        )

        print("\n--- Metrics ---")

        for name, value in metrics.items():

            if isinstance(value, float):
                print(
                    f"{name}: {value:.4f}"
                )
            else:
                print(
                    f"{name}: {value}"
                )

        return {
            "posts": posts,
            "embeddings": embeddings,
            "labels": labels,
            "metrics": metrics,
        }

    finally:

        conn.close()

        print(
            "\nDatabase connection closed."
        )


if __name__ == "__main__":
    run_semantic_clustering()