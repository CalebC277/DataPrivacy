# Location Obfuscation Based On Points Of Interest 

## Project Overview

For the project we implemented three different methods for protecting location data. We are trying
to implement methods for delivery apps or ride share apps that based upon the users location it suggest
a new location that is inside of a given radius. The radius for is going to be how far the indiviudal 
would potentially want to walk to pickup or dropff from their given location such as your house, place of work,
or other locations you would want to keep private. Each method has its own way of getting a suggested location
The three methods are listed below.

- Points of Interests - This method grabs the points of interests in the given radius of the user and selects one of the random POIs. A POI in this instance can be a place that has been identitified as an amenity, leisure, tourism, or a shop. Something like a restraunt or a park would be considered a POI in our program
- Walkable Locations - This method grabs a random walkable location along a road or a path that the user could walk to easily and safely. 
- Hybrid - This method combines the POIs and the walkable location methods. It gets the users location and radius and see if there are a certian number of POIs in the radius of said location. If there are less than 20 POIs in the given location then it will grab both POIs and walkable locations. If there 20 or more POIs in the given radius then it will just suggest the POIs in that area. 

Each tool uses OpenStreetMaps Overpass API to find locations. When each method is built and compiled it will give a couple of output files. 

### Python Files

- poi.py - This implements the Point of Interests method. 
- walkable.py - This implements the walkable locations methods

Both the poi.py and the walkable.py ask the user if they want to type in Address or Coordinates. Then they have to type in 
the Address of Cordinates that they want to use as their location. They have to type in the radius size that they want the 
suggested locations to be inside of. We suggest that the radius size is between 0.5 and .75 km. This allows for the user 
to not have to walk way to far while also being able to protect their privacy. It will then asks for the number of runs. This 
is the amount of times the program will run to grab a location. 

- compare.py - This compares the POI and the walkable locations methods. It reads in a text file called day_in_a_life.txt which consists of the amount of times you want to run each location at the top. Then below you have multiple locations and the radius's each on a new line. It then uses the day in the life file to run the poi.py and walkable.py with those locations. Then it compares the privacy and utility metrics of each both methods. Generate visual output files at the end.

- hybrid.py - This implements the hybrid method. It calls the hybrid_day_in_life.txt file which consists of all the same inputs that would be needed for the poi.py and walkable.py. 

### Output Files

## Installation and Setup

### Setup

- Python 3.6+
- These are the required libraries:
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

