import requests

def get_nearest_poi_osm(location, radius, poi_type):
    """
    Get the nearest point of interest (POI) using OpenStreetMap Overpass API.

    :param location: A tuple of (latitude, longitude).
    :param radius: Search radius in meters.
    :param poi_type: Type of POI (e.g., 'restaurant', 'hospital', 'park').
    :return: Details of the nearest POI or None if not found.
    """

    # Define Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Define Overpass query to search for POI types near the location
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="{poi_type}"](around:{radius},{location[0]},{location[1]});
    );
    out center;
    """

    # Send request to Overpass API
    response = requests.get(overpass_url, params={"data": overpass_query})
    data = response.json()

    # Check if results were returned
    if "elements" in data and len(data["elements"]) > 0:
        # Get the nearest POI
        nearest_poi = data["elements"][0]
        name = nearest_poi.get("tags", {}).get("name", "Unnamed POI")
        latitude = nearest_poi["lat"]
        longitude = nearest_poi["lon"]

        return {
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "type": poi_type,
        }
    else:
        return None


# Example usage
if __name__ == "__main__":
    # Define location (latitude, longitude) - Example: Baltimore, MD
    location = (39.2904, -76.6122)

    # Define radius in meters (1000m = 1km)
    radius = 1000

    # Define POI type (e.g., 'restaurant', 'hospital', 'park')
    poi_type = "restaurant"

    # Get nearest POI
    nearest_poi = get_nearest_poi_osm(location, radius, poi_type)

    if nearest_poi:
        print(f"Nearest {poi_type.capitalize()}: {nearest_poi['name']}")
        print(f"Location: {nearest_poi['latitude']}, {nearest_poi['longitude']}")
    else:
        print(f"No {poi_type} found within {radius} meters.")
