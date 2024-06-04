import requests
import xml.etree.ElementTree as ET
import folium

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:xml][timeout:25];
(
  node["tourism"="attraction"](24.396308,-124.848974,49.384358,-66.885444);
  way["tourism"="attraction"](24.396308,-124.848974,49.384358,-66.885444);
  relation["tourism"="attraction"](24.396308,-124.848974,49.384358,-66.885444);
);
out body;
>;
out skel qt;
"""
# Initialize the map
east_coast_map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

bounding_boxes = [
    (24.396308, -124.848974, 37.0902, -66.885444),  # Southern East Coast
    (37.0902, -124.848974, 49.384358, -66.885444),  # Northern East Coast
    # Add more bounding boxes as needed for other regions
]
filenames = []


# Iterate over bounding boxes and fetch data for each region
for bbox in bounding_boxes:
    # Define the Overpass API query
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

    # Send the request to the Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.text

    filename = f'east_coast_data_{bbox}.xml'
    filenames.append(filename)

    # Save the XML data to a file
    with open(f'east_coast_data_{bbox}.xml', 'w') as file:
        file.write(data)

print(filenames)

# Function to parse XML data and add attractions to the map
def add_attractions_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for node in root.findall('.//node'):
        name = None
        lat = float(node.get('lat'))
        lon = float(node.get('lon'))
        for tag in node.findall('tag'):
            if tag.get('k') == 'name':
                name = tag.get('v')
        if name:
            folium.Marker([lat, lon], popup=name).add_to(east_coast_map)


# Add attractions from each XML file to the map
for xml_file in filenames:
    add_attractions_from_xml(xml_file)

# Save the map as an HTML file
east_coast_map.save('east_coast_attractions.html')

