import numpy as np
import matplotlib.pyplot as plt

# Function to add Laplace noise with adjustable epsilon
def add_laplace_noise(data_point, epsilon):
    noise = np.random.laplace(0, 1 / epsilon, size=2)
    return tuple(np.array(data_point) + noise)

# Compact locations into clusters of size l (in this case, l=2)
def l_clustering(locations, l=5):
    sorted_locations = sorted(locations)
    clusters = []
    for i in range(0, len(sorted_locations), l):
        cluster = sorted_locations[i:i + l]
        if len(cluster) == l:
            clusters.append(cluster)
    return clusters

# Apply differential privacy to each cluster's centroid
def compute_noisy_centroids(clusters, epsilon):
    noisy_centroids = []
    print("Centroid ")
    for cluster in clusters:
        cluster = np.array(cluster)
        centroid = np.mean(cluster, axis=0)
        print(centroid)
        noisy_centroid = add_laplace_noise(centroid, epsilon)
        noisy_centroids.append(noisy_centroid)
    return noisy_centroids


# Main function
def main():
    # Sample data with 5 cities, each with 5 locations
    locations = [
        # San Francisco (5 locations)
        (37.7749, -122.4194), (37.7750, -122.4195), (37.7747, -122.4190), 
        (37.7752, -122.4196), (37.7751, -122.4193),
        
        # Los Angeles (5 locations)
        (34.0522, -118.2437), (34.0523, -118.2436), (34.0519, -118.2438), 
        (34.0525, -118.2440), (34.0518, -118.2435),
        
        # New York (5 locations)
        (40.7128, -74.0060), (40.7129, -74.0059), (40.7130, -74.0057), 
        (40.7125, -74.0063), (40.7127, -74.0061),
        
        # Chicago (5 locations)
        (41.8781, -87.6298), (41.8782, -87.6300), (41.8779, -87.6297), 
        (41.8785, -87.6301), (41.8778, -87.6299),
        
        # Miami (5 locations)
        (25.7617, -80.1918), (25.7618, -80.1920), (25.7620, -80.1915), 
        (25.7619, -80.1917), (25.7621, -80.1919)
    ]

    l = 5
    epsilon = 50.0  # Higher = less noise

    clusters = l_clustering(locations, l)
    noisy_centroids = compute_noisy_centroids(clusters, epsilon)

    print("\nNoisy Compact Locations:")
    for loc in noisy_centroids:
        print((float(loc[0]), float(loc[1])))

    print("\nClusters:")
    for cluster in clusters:
        print(cluster)

if __name__ == "__main__":
    main()
