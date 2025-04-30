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
import numpy as np

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
            category = ', '.join([f"{k}={v}" for k, v in el.get('tags', {}).items() if k != 'name'])
            pois.append((name, lat, lon, category, "poi"))

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
                walkable_areas.append((name, lat_center, lon_center, f"highway={highway_type}", "walkable"))
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

def calculate_utility(user_lat, user_lon, locations):
    if not locations:
        return 0
    
    distances = [calculate_distance(user_lat, user_lon, float(loc[1]), float(loc[2])) for loc in locations]
    avg_distance = sum(distances) / len(distances)
    
    # Lower distance means higher utility (inverse relationship)
    # Normalize to a 0-100 scale where 100 is best (closest)
    max_utility = 100
    # Assuming anything over 5km is low utility
    utility_score = max(0, max_utility - (avg_distance * 20))
    
    return utility_score, avg_distance

def calculate_privacy(user_lat, user_lon, chosen_locations):
    if not chosen_locations:
        return 0, 0
    
    # Calculate centroid of chosen locations
    centroid_lat = sum(float(loc[1]) for loc in chosen_locations) / len(chosen_locations)
    centroid_lon = sum(float(loc[2]) for loc in chosen_locations) / len(chosen_locations)
    
    # Calculate distance between user location and centroid
    privacy_distance = calculate_distance(user_lat, user_lon, centroid_lat, centroid_lon)
    
    # Higher distance means better privacy
    # Normalize to a 0-100 scale where 100 is best (farthest)
    max_privacy = 100
    # Assuming anything over 2km is good privacy
    privacy_score = min(max_privacy, privacy_distance * 50)
    
    return privacy_score, privacy_distance

def CreateMap(lat, lon, rad, locations, location_counter, noise):
    Map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="Selected Location", icon=folium.Icon(color='red')).add_to(Map)

    Circle(
        location=(lat, lon),
        radius=rad * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.3
    ).add_to(Map)

    # Track chosen locations for utility and privacy calculation
    chosen_locations = []
    
def CreateMap(lat, lon, rad, locations, location_counter, noise):
    Map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="Selected Location", icon=folium.Icon(color='red')).add_to(Map)

    Circle(
        location=(lat, lon),
        radius=rad * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.3
    ).add_to(Map)

    # Track chosen locations for utility and privacy calculation
    chosen_locations = []
    
    # Create map markers
    for location in locations:
        name, lat_loc, lon_loc, category, loc_type = location
        marker_color = 'green' if loc_type == 'poi' else 'orange'
        
        # Add the original marker
        folium.Marker(
            location=[float(lat_loc), float(lon_loc)],
            popup=f"{name}<br>{category}",
            icon=folium.Icon(color=marker_color, icon='info-sign' if loc_type == 'poi' else 'road')
        ).add_to(Map)
        
        location_key = f"{name} at ({lat_loc}, {lon_loc}) [{category}]"
        count = location_counter.get(location_key, 0)
        
        if count > 0:
            chosen_locations.append(location)
            
            # Add the noise points for chosen locations
            for x in range(count):
                offset_lat = float(lat_loc) + random.uniform(-noise, noise)
                offset_lon = float(lon_loc) + random.uniform(-noise, noise)
                folium.CircleMarker(
                    location=[offset_lat, offset_lon],
                    radius=2,
                    color='black' if loc_type == 'poi' else 'purple',
                    fill=True,
                    fill_opacity=1
                ).add_to(Map)

    # Calculate utility and privacy metrics
    utility_score, avg_distance = calculate_utility(lat, lon, chosen_locations)
    privacy_score, privacy_distance = calculate_privacy(lat, lon, chosen_locations)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px">
        <p><b>Legend:</b></p>
        <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> User Location</p>
        <p><i class="fa fa-info-sign fa-2x" style="color:green"></i> Points of Interest</p>
        <p><i class="fa fa-road fa-2x" style="color:orange"></i> Walkable Areas</p>
        <p>● Black Dots: Selected POIs</p>
        <p>● Purple Dots: Selected Walkable Areas</p>
        <hr>
        <p><b>Metrics:</b></p>
        <p>Utility Score: {:.2f}/100</p>
        <p>Avg Distance: {:.2f} km</p>
        <p>Privacy Score: {:.2f}/100</p>
        <p>Privacy Distance: {:.2f} km</p>
    </div>
    '''.format(utility_score, avg_distance, privacy_score, privacy_distance)
    
    Map.get_root().html.add_child(folium.Element(legend_html))
    Map.save("Map.html")
    webbrowser.open('file://' + os.path.realpath("Map.html"))

    # Save results to files
    with open("POIS.txt", "w", encoding="utf-8") as file:
        file.write("Locations within the radius:\n\n")
        file.write("Points of Interest:\n")
        for loc in locations:
            if loc[4] == "poi":
                file.write(f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]\n")
        
        file.write("\nWalkable Areas:\n")
        for loc in locations:
            if loc[4] == "walkable":
                file.write(f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]\n")

    with open("chosen_locations.txt", "w", encoding="utf-8") as file:
        file.write("METRICS SUMMARY:\n")
        file.write(f"Utility Score: {utility_score:.2f}/100\n")
        file.write(f"Average Distance: {avg_distance:.2f} km\n")
        file.write(f"Privacy Score: {privacy_score:.2f}/100\n")
        file.write(f"Privacy Distance: {privacy_distance:.2f} km\n\n")
        
        file.write("POIs chosen:\n")
        for loc in locations:
            if loc[4] == "poi":
                loc_key = f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]"
                count = location_counter.get(loc_key, 0)
                if count > 0:
                    file.write(f"{loc_key} -> chosen {count} times\n")
        
        file.write("\nWalkable areas chosen:\n")
        for loc in locations:
            if loc[4] == "walkable":
                loc_key = f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]"
                count = location_counter.get(loc_key, 0)
                if count > 0:
                    file.write(f"{loc_key} -> chosen {count} times\n")

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

    print(f"\nLocation summary: Found {len(pois)} POIs and {len(walkable_areas)} walkable areas.")
        
        # Create location keys for the counter
    location_keys = [f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]" for loc in all_locations]
        
    # Run the simulation
    print(f"\nRunning simulation with {num_runs} iterations...")
    location_counter = defaultdict(int)
    for i in range(num_runs):
        chosen = random.choice(location_keys)
        location_counter[chosen] += 1
        if (i+1) % 10 == 0:
            print(f"Completed {i+1}/{num_runs} simulation runs")
    
    # Create the map with the results
    print("\nGenerating map and metrics...")
    CreateMap(coords[0], coords[1], radius, all_locations, location_counter, noise)
    
    print("\nDone! Map and results files have been created.")
    print("Output files:")
    print("- Map.html: Interactive map with all locations")
    print("- POIS.txt: List of all locations found")
    print("- chosen_locations.txt: Selected locations with metrics")
    

def Main():
    # Read configuration from file
    config = parse_config_file("day_in_a_life2.txt")
    
    if not config:
        print("Failed to read configuration file. Make sure day_in_a_life.txt exists and is properly formatted.")
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
    noise = config.get('noise', 0.05)
    num_runs = config.get('num_runs', 10)
    
    print(f"Using coordinates: {coords}")
    print(f"Radius: {radius} km")
    print(f"Noise: {noise} km")
    print(f"Number of runs: {num_runs}")
    
    # Find POIs and walkable areas
    pois = FindPOIs(coords[0], coords[1], radius)
    walkable_areas = FindWalkableAreas(coords[0], coords[1], radius)
    
    # Combine both types of locations
    all_locations = pois + walkable_areas
    
    if not all_locations:
        print("No locations found within the specified radius.")
        return
        
    print(f"Found {len(pois)} POIs and {len(walkable_areas)} walkable areas.")
    
    # Create location keys for the counter
    location_keys = [f"{loc[0]} at ({loc[1]}, {loc[2]}) [{loc[3]}]" for loc in all_locations]
    
    # Run the simulation
    location_counter = defaultdict(int)
    for _ in range(num_runs):
        chosen = random.choice(location_keys)
        location_counter[chosen] += 1
    
    # Create the map with the results
    CreateMap(coords[0], coords[1], radius, all_locations, location_counter, noise)

if __name__ == "__main__":
    Main()