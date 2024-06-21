import requests
import xml.etree.ElementTree as ET
import datetime
from geopy.geocoders import Nominatim
import collections

class GeoDataFetcher:
    def __init__(self, db):
        self.collection = db.attractions
        self.geolocator = Nominatim(user_agent="tourist_spotter")
    
    def fetch_osm_data(self, bbox):
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
        response = requests.get(overpass_url, params={'data': overpass_query})
        response.raise_for_status()
        return response.text
    
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
        
        # Initialize a queue for BFS traversal
        queue = collections.deque([root])
        
        while queue:
            node = queue.popleft()
            if node.tag == 'node':
                lat = float(node.get('lat'))
                lon = float(node.get('lon'))
                name = None
                for tag in node.findall('tag'):
                    if tag.get('k') == 'name':
                        name = tag.get('v')
                if name:
                    attractions.append({'name': name, 'lat': lat, 'lon': lon})
            elif node.tag == 'way' or node.tag == 'relation':
                # If it's a way or relation, add its children nodes to the queue
                queue.extend(node.findall('.//node'))
    
        return attractions

    def get_attractions(self, place):
        location = self.geolocator.geocode(place)
        if location:
            bbox = (location.latitude - 0.1, location.longitude - 0.1, location.latitude + 0.1, location.longitude + 0.1)
            cached_data = self.collection.find_one({'place': place})
            if cached_data and (datetime.datetime.now() - cached_data['timestamp']).days < 7:
                attractions = cached_data['attractions']
            else:
                xml_data = self.fetch_osm_data(bbox)
                 # Save the XML data to a file
                with open(f'osm_data_{bbox}.xml', 'w') as file:
                    file.write(xml_data)
                attractions = self.parse_osm_data(xml_data)
                self.collection.update_one(
                    {'place': place},
                    {'$set': {'attractions': attractions, 'timestamp': datetime.datetime.now()}},
                    upsert=True
                )
            return {
                'attractions': attractions,
                'location': {'lat': location.latitude, 'lon': location.longitude}
            }
        else:
            return []
