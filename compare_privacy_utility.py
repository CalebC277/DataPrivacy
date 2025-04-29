import subprocess
import time
import math
import re
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import statistics

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else (None, None)

def extract_coords_from_file(filepath):
    coords = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r"\(([-\d.]+), ([-\d.]+)\)", line)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                coords.append((lat, lon))
    return coords

def average_distance(from_coord, to_coords):
    if not to_coords:
        return float('inf')
    total = sum(geodesic(from_coord, point).km for point in to_coords)
    return total / len(to_coords)

def run_program(command):
    subprocess.run(command, shell=True)

def main():
    with open("day_in_a_life.txt", "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    results = []

    num_runs = lines[0]
    #print(f"{num_runs}")
    for i in range(1, len(lines), 2):
        address = lines[i]
        radius = float(lines[i + 1])
        coords = get_coordinates(address)

        if not coords[0]:
            print(f"Skipping invalid address: {address}")
            continue

        print(f"\nProcessing location: {address} (radius {radius} km)")

        # === map_random_poi.py ===
        print("Running POI-based method...")
        proc = subprocess.Popen(
            f'python map_random_poi.py',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=f"address\n{address}\n{radius}\n0.002\n{num_runs}\n")
        time.sleep(2)

        poi_coords = extract_coords_from_file("POIS.txt")
        utility_poi = average_distance(coords, poi_coords)
        results.append((address, "POI", utility_poi, "N/A"))  # Placeholder for privacy

        # === map_random_walkable_osrm.py ===
        print("Running OSRM walkable method...")
        proc = subprocess.Popen(
            f'python map_random_walkable_osrm.py',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=f"address\n{address}\n{radius}\n{num_runs}\n")
        time.sleep(2)

        walkable_coords = extract_coords_from_file("walkable_osrm.txt")
        utility_osrm = average_distance(coords, walkable_coords)
        results.append((address, "OSRM", utility_osrm, "N/A"))  # Placeholder for privacy

    # Print summary
    total_utility_poi = []
    total_utility_osrm = []
    print("\n==== Privacy vs Utility Summary ====")
    for address, method, utility, privacy in results:
        print(f"Address: {address}")
        print(f"  Method: {method}")
        print(f"  Utility: {utility:.4f} km")
        print(f"  Privacy: {privacy}")
        print()
        if method == "POI":
            total_utility_poi.append(utility)
        if method == "OSRM":
            total_utility_osrm.append(utility)

    print(f"Average Utility for POI: {statistics.mean(total_utility_poi):.4f} km")
    print(f"Average Utility for OSRM: {statistics.mean(total_utility_osrm):.4f} km")

if __name__ == "__main__":
    main()
