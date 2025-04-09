import numpy as np
import matplotlib.pyplot as plt

# Function to add Laplace noise with adjustable epsilon
def add_laplace_noise(data_point, epsilon):
    noise = np.random.laplace(0, 1 / epsilon, size=2)
    return tuple(np.array(data_point) + noise)

# Compact locations into clusters of size l (in this case, l=2)
def l_clustering(locations, l=2):
    sorted_locations = sorted(locations)
    clusters = []
    for i in range(0, len(sorted_locations), l):
        cluster = sorted_locations[i:i + l]
        if len(cluster) == l:
            clusters.append(cluster)
    return clusters

# Apply differential privacy to each cluster's centroid
def compute_noisy_centroids(clusters, epsilon):
    noisy_compact_locations = []
    for cluster in clusters:
        cluster = np.array(cluster)
        centroid = np.mean(cluster, axis=0)
        noisy_centroid = add_laplace_noise(centroid, epsilon)
        noisy_compact_locations.extend([noisy_centroid] * len(cluster))
    return noisy_compact_locations

# Plot original clusters and noisy centroids
def visualize_clusters(clusters, noisy_centroids):
    colors = ['blue', 'green', 'red', 'purple', 'orange']
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, cluster in enumerate(clusters):
        cluster = np.array(cluster)
        ax.scatter(cluster[:, 1], cluster[:, 0], color=colors[i % len(colors)],
                   label=f"Cluster {i+1} Original")
        noisy = noisy_centroids[i * len(cluster):(i + 1) * len(cluster)]
        noisy = np.array(noisy)
        ax.scatter(noisy[0][1], noisy[0][0], color=colors[i % len(colors)], marker='x', s=100,
                   label=f"Cluster {i+1} Noisy Centroid")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("L-Clustering with Differential Privacy")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()

# Main function
def main():
    # Sample data (2 per cluster for simplicity)
    locations = [
        (37.7749, -122.4194), (37.7750, -122.4195),   # San Francisco
        (34.0522, -118.2437), (34.0523, -118.2436),   # Los Angeles
        (40.7128, -74.0060), (40.7129, -74.0059)      # New York
    ]

    l = 2
    epsilon = 2.0  # Higher = less noise

    clusters = l_clustering(locations, l)
    noisy_centroids = compute_noisy_centroids(clusters, epsilon)

    print("Noisy Compact Locations:")
    for loc in noisy_centroids:
        print(loc)

    print("\nClusters:")
    for cluster in clusters:
        print(cluster)

    visualize_clusters(clusters, noisy_centroids)

if __name__ == "__main__":
    main()
