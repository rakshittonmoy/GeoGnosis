import xml.etree.ElementTree as ET
import sqlite3

# Parse XML data and extract relevant information
def parse_osm_xml(xml_file):
    attractions = []
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for node in root.findall('.//node'):
        tags = node.findall('tag')
        name = next((tag.attrib['v'] for tag in tags if tag.attrib['k'] == 'name'), None)
        tourism = next((tag.attrib['v'] for tag in tags if tag.attrib['k'] == 'tourism'), None)
        if name and tourism:
            attraction = {
                'name': name,
                'type': tourism,
                'latitude': float(node.attrib['lat']),
                'longitude': float(node.attrib['lon'])
            }
            attractions.append(attraction)
    return attractions

# Store data in SQLite database
def store_in_sqlite(attractions, db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attractions (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    latitude REAL,
                    longitude REAL
                )''')
    for attraction in attractions:
        c.execute('''INSERT INTO attractions (name, type, latitude, longitude)
                    VALUES (?, ?, ?, ?)''',
                    (attraction['name'], attraction['type'], attraction['latitude'], attraction['longitude']))
    conn.commit()
    conn.close()

# Fetch OSM data in XML format
osm_xml_file = 'tourist_attractions.xml'  # Replace with the path to your XML file
attractions = parse_osm_xml(osm_xml_file)

# Store extracted information in a SQLite database
sqlite_db_file = 'tourist_attractions.db'
store_in_sqlite(attractions, sqlite_db_file)



