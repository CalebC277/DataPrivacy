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

    # Now we expect sets of 3 lines: address, radius, poi_count
    for i in range(0, len(lines), 3):
        if i + 2 >= len(lines):
            print(f"Skipping incomplete data set at line {i+1}")
            continue
            
        address = lines[i]
        radius = float(lines[i + 1])
        poi_count = int(lines[i + 2])  # New parameter for number of POIs
        
        coords = get_coordinates(address)

        if not coords[0]:
            print(f"Skipping invalid address: {address}")
            continue

        print(f"\nProcessing location: {address} (radius {radius} km, POI count: {poi_count})")

        # === map_random_poi.py ===
        print("Running POI-based method...")
        proc = subprocess.Popen(
            f'python map_random_poi.py',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Pass the poi_count parameter to the script
        proc.communicate(input=f"address\n{address}\n{radius}\n0.002\n{poi_count}\n")
        time.sleep(2)

        poi_coords = extract_coords_from_file("POIS.txt")
        utility_poi = average_distance(coords, poi_coords)
        results.append((address, "POI", utility_poi, "N/A", poi_count))

        # === map_random_walkable_osrm.py ===
        print("Running OSRM walkable method...")
        proc = subprocess.Popen(
            f'python map_random_walkable_osrm.py',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=f"address\n{address}\n{radius}\n")
        time.sleep(2)

        walkable_coords = extract_coords_from_file("walkable_osrm.txt")
        utility_osrm = average_distance(coords, walkable_coords)
        results.append((address, "OSRM", utility_osrm, "N/A", "N/A"))  # OSRM doesn't use POI count

    # Print summary
    total_utility_poi = []
    total_utility_osrm = []
    print("\n==== Privacy vs Utility Summary ====")
    for address, method, utility, privacy, poi_count in results:
        print(f"Address: {address}")
        print(f"  Method: {method}")
        print(f"  Utility: {utility:.4f} km")
        print(f"  Privacy: {privacy}")
        if method == "POI":
            print(f"  POI Count: {poi_count}")
        print()
        if method == "POI":
            total_utility_poi.append(utility)
        if method == "OSRM":
            total_utility_osrm.append(utility)

    if total_utility_poi:
        print(f"Average Utility for POI: {statistics.mean(total_utility_poi):.4f} km")
    if total_utility_osrm:
        print(f"Average Utility for OSRM: {statistics.mean(total_utility_osrm):.4f} km")

if __name__ == "__main__":
    main()