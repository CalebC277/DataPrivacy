import numpy as np
from sklearn.cluster import DBSCAN

# Function to add Laplace noise to a data point
def add_laplace_noise(data_point, epsilon):
    # Ensure the data point is a numpy array
    data_point = np.array(data_point)
    # Laplace noise generator (mean = 0, scale = 1/epsilon)
    noise = np.random.laplace(0, 1/epsilon, data_point.shape)
    return data_point + noise

# Function to cluster location data using DBSCAN
def cluster_locations(locations, eps=0.5, min_samples=1):
    """
    Cluster locations using DBSCAN. Locations are clustered based on latitude and longitude proximity.
    """
    X = np.array(locations)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X)
    print(f"DBSCAN Labels: {labels}")  # Debugging output
    return labels, dbscan.components_

# Function to apply differential privacy (Laplace noise) to the clusters
def apply_differential_privacy(clusters, epsilon=0.1):
    """
    Apply differential privacy to the cluster centroids and the location data.
    """
    noisy_clusters = []

    for cluster in clusters:
        # Calculate the centroid of the cluster
        centroid = np.mean(cluster, axis=0)
        # Add Laplace noise to the centroid
        noisy_centroid = add_laplace_noise(centroid, epsilon)

        noisy_cluster = []
        for point in cluster:
            # Add Laplace noise to each location point
            noisy_point = add_laplace_noise(point, epsilon)
            noisy_cluster.append(noisy_point)

        noisy_clusters.append((noisy_centroid, noisy_cluster))

    return noisy_clusters

# Main function
def main():
    # Sample location data (latitude, longitude)
    locations = [
        (37.7749, -122.4194),  # San Francisco
        (34.0522, -118.2437),  # Los Angeles
        (40.7128, -74.0060),   # New York
        (51.5074, -0.1278),    # London
        (48.8566, 2.3522),     # Paris
        (35.6895, 139.6917),   # Tokyo
    ]

    print("Starting Clustering...")

    # Step 1: Cluster the locations
    labels, _ = cluster_locations(locations)

    # Step 2: Group locations into clusters based on the labels
    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue  # Ignore noise points
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(locations[idx])

    print(f"Clusters: {clusters}")

    # Step 3: Apply differential privacy
    epsilon = 0.1
    noisy_clusters = apply_differential_privacy(list(clusters.values()), epsilon)

    # Step 4: Print the noisy clusters
    for i, (noisy_centroid, noisy_cluster) in enumerate(noisy_clusters):
        print(f"\nCluster {i + 1}:")
        print(f"  Noisy Centroid: {noisy_centroid}")
        for point in noisy_cluster:
            print(f"  Noisy Location: {point}")

# Run the main function
if __name__ == "__main__":
    main()