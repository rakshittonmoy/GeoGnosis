# GeoGnossis
Built leveraging OpenStreetMap data to create an interactive map of tourist spots.

GeoGnossis aims to provide the user the opportunity to find the tourist attractions in an area by name or coordinates. By leveraging OpenStreetMap(OSM) data through the Overpass API, this project extracts tourist attraction data, processes it, and presents it on an interactive map.

## Collect: 
Utilizing the Overpass API, Geognossis retrieves tourist attraction data
from OSM and saves it in XML format.

## Prepare: 
The XML data is parsed using XPath to extract pertinent information
about tourist attractions. Subsequently, the data undergoes conversion from XML
to JSON format, enabling seamless storage in MongoDb.

## Access: 
Geognossis facilitates database queries to retrieve specific tourist
attractions, which are then plotted on an interactive map displayed in HTML
format.

## License: 
OpenStreetMap (OSM) data is available under the Open Database
License (ODbL)

# Key technologies:  
Flask, XML, MongoDB, Leaflet.js, Geopy, Overpass API

# Setup   

Setup python environment   
python -m venv venv    
source venv/bin/activate    
pip install -r ./config/requirements.txt   

Run the Flask app   
flask run    

Open your browser and navigate to http://127.0.0.1:5000 to see the application in action.   
