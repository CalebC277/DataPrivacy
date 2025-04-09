import numpy as np
from sklearn.cluster import DBSCAN
import random

# Function to add Laplace noise to a data point
def add_laplace_noise(data_point, epsilon):
    # Ensure the data point is a numpy array (convert if it's a tuple)
    data_point = np.array(data_point)
    
    # Laplace noise generator (mean = 0, scale = 1/epsilon)
    noise = np.random.laplace(0, 1/epsilon, data_point.shape)
    
    return data_point + noise

# Function to cluster location data using DBSCAN
def cluster_locations(locations, eps=0.5, min_samples=1):  # Increased eps and reduced min_samples
    """
    Cluster locations using DBSCAN. Locations are clustered based on latitude and longitude proximity.
    :param locations: List of tuples [(lat1, lon1), (lat2, lon2), ...]
    :param eps: The maximum distance between two samples for them to be considered as in the same neighborhood.
    :param min_samples: The number of samples in a neighborhood for a point to be considered as a core point.
    :return: List of cluster labels
    """
    # Convert locations to a numpy array for clustering
    X = np.array(locations)
    
    # DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X)
    
    print(f"DBSCAN Labels: {labels}")  # Debugging output
    
    return labels, dbscan.components_


# Function to apply differential privacy (DPLPA) to the clusters
def apply_differential_privacy(clusters, epsilon=0.1):
    """
    Apply differential privacy to the cluster centroids and the location data.
    :param clusters: List of clusters, each containing a set of locations.
    :param epsilon: The privacy budget (controls the amount of noise).
    :return: List of noisy clusters with Laplace noise added
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
    
    print("Starting Clustering...")  # Debugging output
    
    # Step 1: Cluster the locations
    labels, _ = cluster_locations(locations)
    
    # Step 2: Group locations into clusters based on the labels
    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue  # Ignore noise points (DBSCAN labels them as -1)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(locations[idx])
    
    print(f"Clusters: {clusters}")  # Debugging output
    
    # Step 3: Apply differential privacy (Laplace noise)
    epsilon = 0.1  # Privacy budget
    noisy_clusters = apply_differential_privacy(list(clusters.values()), epsilon)
    
    # Print the noisy clusters with centroids
    for i, (noisy_centroid, noisy_cluster) in enumerate(noisy_clusters):
        print(f"Cluster {i + 1}:")
        print(f"  Noisy Centroid: {noisy_centroid}")
        for point in noisy_cluster:
            print(f"  Noisy Location: {point}")
        print()

# Run the main function
if __name__ == "__main__":
    main()
