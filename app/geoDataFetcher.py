import requests
import xml.etree.ElementTree as ET
import datetime
from geopy.geocoders import Nominatim
import collections

""" GeoDataFetcher class, interacts with OSM data to fetch tourist attractions
for a specified location and manage the caching of this data in the database """

class GeoDataFetcher:
    def __init__(self, db):
        # initializing with database collection & geolocator
        self.collection = db.attractions
        self.geolocator = Nominatim(user_agent="tourist_spotter")
    
    def fetch_osm_data(self, bbox):
        # fetch osm data for given bounding box
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:xml][timeout:1000];
        (
          node["tourism"="attraction"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["tourism"="attraction"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          relation["tourism"="attraction"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.get(overpass_url, params={'data': overpass_query}) # fire call for api
        response.raise_for_status() # raise an error in case of bad responses
        return response.text # get xml data as string 
    
    def parse_osm_data(self, xml_data):
        attractions = []
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        for node in root.findall('.//node'):
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            name = None
            for tag in node.findall('tag'):
                if tag.get('k') == 'name':
                    name = tag.get('v')
            if name:
                attractions.append({'name': name, 'lat': lat, 'lon': lon})
        return attractions
    
    def parse_osm_data(self, xml_data):
        attractions = []
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        
        # Initializing a queue for BFS traversal
        queue = collections.deque([root])
        
        while queue:
            node = queue.popleft()
            if node.tag == 'node': # procesing nodes
                lat = float(node.get('lat'))
                lon = float(node.get('lon'))
                name = None
                for tag in node.findall('tag'):
                    if tag.get('k') == 'name':
                        name = tag.get('v')
                if name:
                    attractions.append({'name': name, 'lat': lat, 'lon': lon})
            elif node.tag == 'way' or node.tag == 'relation': # processing ways and relations
                # If it's a way or relation, add its children nodes to the queue
                queue.extend(node.findall('.//node'))
    
        return attractions #final list of attractions

    def get_attractions(self, place):
        # attractions for a given place
        location = self.geolocator.geocode(place) #geocode the name to get coordinates
        if location:
            # bounding box around the location
            bbox = (location.latitude - 0.1, location.longitude - 0.1, location.latitude + 0.1, location.longitude + 0.1)
            # checking cache for existing data
            cached_data = self.collection.find_one({'place': place})
            if cached_data and (datetime.datetime.now() - cached_data['timestamp']).days < 7:
                # if less than e week old use them
                attractions = cached_data['attractions']
            else:
                # fetching new data if no cache exists or if it is outdated 
                xml_data = self.fetch_osm_data(bbox)
                 # Saving the XML data to a file
                with open(f'osm_data_{bbox}.xml', 'w') as file:
                    file.write(xml_data)
                attractions = self.parse_osm_data(xml_data)
                # updating cache with new data
                self.collection.update_one(
                    {'place': place},
                    {'$set': {'attractions': attractions, 'timestamp': datetime.datetime.now()}},
                    upsert=True
                )
                # return attractions & location
            return {
                'attractions': attractions,
                'location': {'lat': location.latitude, 'lon': location.longitude}
            }
        else:
            return [] # if no location found - retunr empty list
