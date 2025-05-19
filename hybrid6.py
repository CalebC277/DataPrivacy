import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests
import re
import random
from collections import defaultdict
import warnings
import math

OVERPASS_URL = "http://overpass-api.de/api/interpreter"
os.environ["OMP_NUM_THREADS"] = "1"
warnings.filterwarnings(
    "ignore",
    message="Could not find the number of physical cores*",
    category=UserWarning
)

def GetCoordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def FindPOIs(lat, lon, rad):
    query = f"""
    [out:json];
    (
      node["amenity"](around:{rad * 1000},{lat},{lon});
      node["tourism"](around:{rad * 1000},{lat},{lon});
      node["leisure"](around:{rad * 1000},{lat},{lon});
      node["shop"](around:{rad * 1000},{lat},{lon});

      way["amenity"](around:{rad * 1000},{lat},{lon});
      way["tourism"](around:{rad * 1000},{lat},{lon});
      way["leisure"](around:{rad * 1000},{lat},{lon});
      way["shop"](around:{rad * 1000},{lat},{lon});

      relation["amenity"](around:{rad * 1000},{lat},{lon});
      relation["tourism"](around:{rad * 1000},{lat},{lon});
      relation["leisure"](around:{rad * 1000},{lat},{lon});
      relation["shop"](around:{rad * 1000},{lat},{lon});
    );
    out center tags;
    """
    response = requests.get(OVERPASS_URL, params={'data': query})
    data = response.json()
    pois = []
    for el in data['elements']:
        name = el.get('tags', {}).get('name', 'Unnamed POI')
        lat = el.get('lat')
        lon = el.get('lon')

        if lat is None or lon is None:
            center = el.get('center')
            if center:
                lat = center.get('lat')
                lon = center.get('lon')

        if lat is not None and lon is not None and name != 'Unnamed POI':
            pois.append((name, lat, lon, "poi"))

    return pois

def FindWalkableAreas(lat, lon, rad):
    query = f"""
    [out:json];
    (
      way["highway"](around:{rad * 1000},{lat},{lon})
        ["highway"!~"motorway|motorway_link"];
    );
    out center tags;
    """
    response = requests.get(OVERPASS_URL, params={'data': query})
    data = response.json()
    walkable_areas = []
    for el in data['elements']:
        center = el.get('center')
        if center:
            lat_center = center.get('lat')
            lon_center = center.get('lon')
            if lat_center and lon_center:
                highway_type = el['tags'].get('highway', 'unknown')
                name = el['tags'].get('name', f"Walkable Area ({highway_type})")
                walkable_areas.append((name, lat_center, lon_center, "walkable"))
    return walkable_areas

def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate distance in kilometers using the Haversine formula
    R = 6371  # Radius of the Earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

def calculate_centroid(locations):
    if not locations:
        return (0, 0)
    
    centroid_lat = sum(float(loc[1]) for loc in locations) / len(locations)
    centroid_lon = sum(float(loc[2]) for loc in locations) / len(locations)
    return (centroid_lat, centroid_lon)

def calculate_privacy_distance(user_lat, user_lon, chosen_locations):
    if not chosen_locations:
        return 0
    
    # Calculate centroid of chosen locations
    centroid_lat, centroid_lon = calculate_centroid(chosen_locations)
    
    # Calculate distance between user location and centroid
    privacy_distance = calculate_distance(user_lat, user_lon, centroid_lat, centroid_lon)
    return privacy_distance

def calculate_utility_distance(user_lat, user_lon, chosen_locations):
    if not chosen_locations:
        return 0
    
    # Calculate centroid of chosen locations
    centroid_lat, centroid_lon = calculate_centroid(chosen_locations)
    
    # Calculate average distance from centroid to all chosen locations
    distances = [calculate_distance(centroid_lat, centroid_lon, float(loc[1]), float(loc[2])) 
                 for loc in chosen_locations]
    
    utility_distance = sum(distances) / len(distances) if distances else 0
    return utility_distance

def CreateMap(lat, lon, rad, locations, location_counter):
    Map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="User Location", icon=folium.Icon(color='red')).add_to(Map)

    Circle(
        location=(lat, lon),
        radius=rad * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.3
    ).add_to(Map)

    # Track chosen locations
    chosen_locations = []
    
    # Create map markers ONLY for chosen locations
    for location in locations:
        name, lat_loc, lon_loc, loc_type = location
        location_key = f"{name} ({lat_loc}, {lon_loc})"
        count = location_counter.get(location_key, 0)
        
        if count > 0:
            chosen_locations.append(location)
            marker_color = 'green' if loc_type == 'poi' else 'orange'
            
            # Add only the chosen locations
            folium.Marker(
                location=[float(lat_loc), float(lon_loc)],
                popup=f"{name}<br>Visits: {count}",
                icon=folium.Icon(color=marker_color, icon='info-sign' if loc_type == 'poi' else 'road')
            ).add_to(Map)

    Map.save("Map.html")
    webbrowser.open('file://' + os.path.realpath("Map.html"))
    
    return chosen_locations

def parse_config_file(filename):
    try:
        config = {}
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'location_type':
                config[key] = value.lower()
            elif key in ['latitude', 'longitude', 'radius', 'noise']:
                config[key] = float(value)
            elif key == 'address':
                config[key] = value
            elif key == 'num_runs':
                config[key] = int(value)
                
        return config
    except Exception as e:
        print(f"Error parsing config file: {e}")
        return None

def Main():
    # Read configuration from file
    config = parse_config_file("day_in_a_life2.txt")
    
    if not config:
        print("Failed to read configuration file. Make sure day_in_a_life2.txt exists and is properly formatted.")
        return
        
    # Get location coordinates
    if 'location_type' in config and config['location_type'] == 'address':
        if 'address' not in config:
            print("Address not specified in config file.")
            return
            
        coords = GetCoordinates(config['address'])
        if not coords:
            print("Address not found")
            return
    elif 'latitude' in config and 'longitude' in config:
        coords = (config['latitude'], config['longitude'])
    else:
        print("Invalid location information in config file.")
        return
        
    # Get other parameters
    radius = config.get('radius', 1.0)
    num_runs = config.get('num_runs', 10)
    
    print(f"Using coordinates: {coords}")
    print(f"Radius: {radius} km")
    print(f"Number of runs: {num_runs}")
    
    # Find POIs and walkable areas
    pois = FindPOIs(coords[0], coords[1], radius)
    walkable_areas = FindWalkableAreas(coords[0], coords[1], radius)
    
    print(f"Found {len(pois)} POIs and {len(walkable_areas)} walkable areas.")
    
    # MODIFIED LOGIC: Only use walkable areas if not enough POIs are found
    locations_to_use = []
    location_keys = []
    
    # First try to use POIs if there are at least 20 of them
    if len(pois) >= 20:
        print("Using POIs as there are at least 5 available.")
        locations_to_use = pois
    else:
        # If not enough POIs, combine POIs with walkable areas
        print(f"Only {len(pois)} POIs found, which is less than 5. Adding walkable areas.")
        locations_to_use = pois + walkable_areas
        
        # If still not enough locations, use what we have but print a warning
        if len(locations_to_use) < 5:
            print(f"Warning: Only {len(locations_to_use)} total locations found within radius.")
    
    if not locations_to_use:
        print("No locations found within the specified radius.")
        return
    
    # Create location keys for the counter and a dictionary to map keys back to locations
    location_dict = {}
    for loc in locations_to_use:
        key = f"{loc[0]} ({loc[1]}, {loc[2]})"
        location_keys.append(key)
        location_dict[key] = loc
    
    # Create a file to record per-run privacy and utility metrics
    with open("privacy_utility_metrics.csv", "w", encoding="utf-8") as metrics_file:
        metrics_file.write("Run,Location,Utility(km),Privacy(km)\n")
        
        # Initialize empty list for chosen locations
        chosen_locations = []
        location_counter = defaultdict(int)
        
        # Run the simulation
        for run in range(1, num_runs + 1):
            # Select a random location
            chosen_key = random.choice(location_keys)
            chosen_location = location_dict[chosen_key]
            location_counter[chosen_key] += 1
            
            # Add to list of chosen locations
            chosen_locations.append(chosen_location)
            
            # Calculate utility (average distance from centroid to locations)
            utility = calculate_utility_distance(
                coords[0], coords[1], chosen_locations
            )
            
            # Calculate privacy (distance from user to centroid)
            privacy = calculate_privacy_distance(
                coords[0], coords[1], chosen_locations
            )
            
            # Write metrics to file for this run
            metrics_file.write(
                f'{run},"{chosen_key}",{utility:.4f},{privacy:.4f}\n'
            )
            
            print(f"Run {run}: Selected {chosen_location[0]}")
            print(f"  - Utility: {utility:.4f} km")
            print(f"  - Privacy: {privacy:.4f} km")
    
    # Create the map with the user location and suggested locations
    CreateMap(coords[0], coords[1], radius, locations_to_use, location_counter)
    
    # Calculate final metrics for all chosen locations
    final_utility = calculate_utility_distance(coords[0], coords[1], chosen_locations)
    final_privacy = calculate_privacy_distance(coords[0], coords[1], chosen_locations)
    
    # Save aggregated results to file
    with open("suggested_locations.txt", "w", encoding="utf-8") as file:
        file.write("Final Utility and Privacy Metrics:\n")
        file.write(f"Utility: {final_utility:.4f} km\n")
        file.write(f"Privacy: {final_privacy:.4f} km\n\n")
        
        file.write("Suggested locations:\n")
        for loc_key, count in location_counter.items():
            if count > 0:
                file.write(f"{loc_key} -> suggested {count} times\n")
    
    print("\nMap and results files have been printed and created!.")
    print("Output files:")
    print("Map.html: This is an interactive map with the spots of users location and suggested locations")
    print("suggested_locations.txt: Provides final metrics and suggested locations")
    print("privacy_utility_metrics.csv: A CSV file of every run with location, priavcy, utility")

if __name__ == "__main__":
    Main()