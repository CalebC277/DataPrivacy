# Location Obfuscation Based On Points Of Intreset 

## Project Overview

For the project we implemented three different methods for protecting location data. We are trying
to implement methods for delivery apps or ride share apps that based upon the users location it suggest
a new location that is inside of a given radius. The radius for is going to be how far the indiviudal 
would potentially want to walk to pickup or dropff from their given location such as your house, place of work,
or other locations you would want to keep private. Each method has its own way of getting a suggested location
The three methods are listed below.

- Points of Interests (poi.py) - This method grabs the points of interests in the given radius of the user and selects one of the random POIs. A POI in this instance can be a place that has been identitified as an amenity, leisure, tourism, or a shop. Something like a restraunt or a park would be considered a POI in our program
- Walkable Locations (walkable.py) - This method grabs a random walkable location along a road or a path that the user could walk to easily and safely. 
- Hybrid (hybrid.py) - This method combines the POIs and the walkable location methods. It gets the users location and radius and see if there are a certian number of POIs in the radius of said location. If there are less than 20 POIs in the given location then it will grab both POIs and walkable locations. If there 20 or more POIs in the given radius then it will just suggest the POIs in that area. 

Each tool uses OpenStreetMaps Overpass API to find locations. When each method is built and compiled it will give a couple of output files. 

## Output Files

## Installation and Setup

### Setup

- Python 3.6+
- These are the required libraries
  - folium
  - geopy
  - requests
  - numpy
  - pandas
  - matplotlib
  - tqdm

Install all of these packages:

```bash
pip install folium geopy requests numpy pandas matplotlib tqdm
```

### Build and Compile

All of these files can be built and comiled by:

```bash
python3 hybrid.py
```
```bash
python3 poi.py
```
```bash
python3 walkable.py
```
```bash
python3 compare.py
```
## Testing

