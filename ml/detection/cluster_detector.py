"""Semantic cluster detection for SignalForge."""

from collections import defaultdict

import hdbscan


def cluster_embeddings(embeddings):
    """
    Cluster normalized semantic embeddings using HDBSCAN.

    Official SignalForge configuration:
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

    labels = clusterer.fit_predict(embeddings)

    return labels


def group_posts_by_cluster(posts, labels):
    """Group post text by cluster label."""

    clusters = defaultdict(list)

    for post, label in zip(posts, labels):
        clusters[label].append(post)

    return dict(clusters)


def print_clusters(posts, labels):
    """Print posts grouped by semantic cluster."""

    clusters = group_posts_by_cluster(
        posts,
        labels,
    )

    print("\n")
    print("=" * 60)
    print("SEMANTIC CLUSTERS")
    print("=" * 60)

    for cluster_no, cluster_posts in clusters.items():

        print(
            f"\n--- Cluster {cluster_no} ---"
        )

        for post in cluster_posts:
            print(post["text"])


#* EVALUATION 

import numpy as np

from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    normalized_mutual_info_score,
    silhouette_score,
)


def evaluate_clustering(
    embeddings,
    labels,
    rows,
):
    """Calculate clustering evaluation metrics."""

    # HDBSCAN uses -1 for noise.
    # Exclude noise from internal metrics.

    mask = labels != -1

    clustered_embeddings = embeddings[mask]
    clustered_labels = labels[mask]

    results = {
        "num_posts": len(labels),
        "num_clusters": len(
            set(labels) - {-1}
        ),
        "num_noise_points": int(
            np.sum(labels == -1)
        ),
    }

    # --------------------------------------------------------
    # Internal metrics
    # --------------------------------------------------------

    if len(set(clustered_labels)) >= 2:

        results["silhouette"] = silhouette_score(
            clustered_embeddings,
            clustered_labels,
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

    else:

        results["silhouette"] = None
        results["davies_bouldin"] = None
        results["calinski_harabasz"] = None

    # --------------------------------------------------------
    # Ground-truth metrics
    # --------------------------------------------------------

    true_labels = [
        row[8]
        for row in rows
    ]

    results["ari"] = adjusted_rand_score(
        true_labels,
        labels,
    )

    results["nmi"] = normalized_mutual_info_score(
        true_labels,
        labels,
    )

    return results