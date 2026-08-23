"""Semantic cluster detection for SignalForge."""

from collections import defaultdict

import hdbscan
import numpy as np

from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


# ============================================================
# CLUSTERING
# ============================================================

def cluster_embeddings(embeddings):
    """
    Cluster normalized semantic embeddings using HDBSCAN.

    Current SignalForge configuration:

        min_cluster_size=3
        min_samples=1
        metric='euclidean'
        cluster_selection_method='eom'
        prediction_data=True
    """

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,
        min_samples=1,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True,
    )

    labels = clusterer.fit_predict(
        embeddings
    )

    return labels


# ============================================================
# GROUP CLUSTERS
# ============================================================

def group_posts_by_cluster(posts, labels):
    """Group posts by their cluster label."""

    clusters = defaultdict(list)

    for post, label in zip(
        posts,
        labels,
    ):
        clusters[label].append(post)

    return dict(clusters)


# ============================================================
# PRINT CLUSTERS
# ============================================================

def print_clusters(
    posts,
    labels,
    max_clusters=10,
    posts_per_cluster=5,
):
    """
    Print a sample of posts from the largest
    non-noise clusters.

    HDBSCAN uses -1 to represent noise.
    """

    clusters = group_posts_by_cluster(
        posts,
        labels,
    )

    print("\n")
    print("=" * 60)
    print("SEMANTIC CLUSTERS")
    print("=" * 60)

    # Sort clusters by size.
    sorted_clusters = sorted(
        clusters.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    )

    shown_clusters = 0

    for cluster_no, cluster_posts in sorted_clusters:

        # Skip HDBSCAN noise.
        if cluster_no == -1:
            continue

        print("\n" + "=" * 60)

        print(
            f"Cluster {cluster_no} "
            f"| {len(cluster_posts)} posts"
        )

        print("=" * 60)

        for post in cluster_posts[
            :posts_per_cluster
        ]:

            title = (
                post["title"] or ""
            )

            content = (
                post["content"] or ""
            )

            print(
                f"\nPost ID: "
                f"{post['post_id']}"
            )

            print(
                f"Title: {title}"
            )

            print(
                f"Content: "
                f"{content[:300]}"
            )

        shown_clusters += 1

        if shown_clusters >= max_clusters:
            break

    # --------------------------------------------------------
    # Noise summary
    # --------------------------------------------------------

    noise_posts = clusters.get(
        -1,
        [],
    )

    print("\n")
    print("=" * 60)
    print("NOISE")
    print("=" * 60)

    print(
        f"Noise posts: "
        f"{len(noise_posts)}"
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_clustering(
    embeddings,
    labels,
):
    """
    Calculate internal clustering metrics.

    HDBSCAN noise points (-1) are excluded
    from the internal clustering metrics.

    Ground-truth metrics such as ARI and NMI
    are intentionally not calculated because
    the current posts table does not contain
    a true_topic / ground-truth label.
    """

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

    noise_mask = labels == -1

    clustered_mask = labels != -1

    clustered_embeddings = (
        embeddings[clustered_mask]
    )

    clustered_labels = (
        labels[clustered_mask]
    )

    num_clusters = len(
        set(labels) - {-1}
    )

    num_noise_points = int(
        np.sum(noise_mask)
    )

    num_clustered_points = int(
        np.sum(clustered_mask)
    )

    num_posts = len(labels)

    noise_percentage = (
        num_noise_points
        / num_posts
        * 100
        if num_posts > 0
        else 0
    )

    results = {
        "num_posts": num_posts,
        "num_clusters": num_clusters,
        "num_clustered_points": (
            num_clustered_points
        ),
        "num_noise_points": (
            num_noise_points
        ),
        "noise_percentage": (
            noise_percentage
        ),
        "silhouette": None,
        "davies_bouldin": None,
        "calinski_harabasz": None,
    }

    # --------------------------------------------------------
    # Print statistics
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("CLUSTERING STATISTICS")
    print("=" * 60)

    print(
        f"Number of posts: "
        f"{num_posts}"
    )

    print(
        f"Number of clustered posts: "
        f"{num_clustered_points}"
    )

    print(
        f"Number of clusters: "
        f"{num_clusters}"
    )

    print(
        f"Number of noise points: "
        f"{num_noise_points}"
    )

    print(
        f"Noise percentage: "
        f"{noise_percentage:.2f}%"
    )

    # --------------------------------------------------------
    # Internal metrics
    # --------------------------------------------------------

    unique_cluster_labels = set(
        clustered_labels
    )

    # Metrics require at least:
    # - 2 clusters
    # - more samples than clusters

    if (
        len(unique_cluster_labels) >= 2
        and len(clustered_labels)
        > len(unique_cluster_labels)
    ):

        results["silhouette"] = (
            silhouette_score(
                clustered_embeddings,
                clustered_labels,
            )
        )

        results["davies_bouldin"] = (
            davies_bouldin_score(
                clustered_embeddings,
                clustered_labels,
            )
        )

        results["calinski_harabasz"] = (
            calinski_harabasz_score(
                clustered_embeddings,
                clustered_labels,
            )
        )

        print("\n")
        print(
            "--- Internal Clustering Metrics ---"
        )

        print(
            f"Silhouette Score       : "
            f"{results['silhouette']:.4f}"
        )

        print(
            f"Davies-Bouldin Index   : "
            f"{results['davies_bouldin']:.4f}"
        )

        print(
            f"Calinski-Harabasz      : "
            f"{results['calinski_harabasz']:.4f}"
        )

    else:

        print(
            "\nNot enough valid clusters "
            "for internal metrics."
        )

    return results