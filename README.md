# GeoGnosis
Built leveraging OpenStreetMap data to create an interactive map of tourist spots.

GeoGnosis aims to discover and display tourist attractions within a
specified area, such as the USA or New York. By leveraging OpenStreetMap
(OSM) data through the Overpass API, this project extracts tourist attraction data,
processes it, and presents it on an interactive map.

# Collect: Utilizing the Overpass API, TouristSpotter retrieves tourist attraction data
from OSM and saves it in XML format.

# Prepare: The XML data is parsed using XPath to extract pertinent information
about tourist attractions. Subsequently, the data undergoes conversion from XML
to JSON format, enabling seamless storage in a relational database management
system (RDBMS) or NoSQL database.

# Access: TouristSpotter facilitates database queries to retrieve specific tourist
attractions, which are then plotted on an interactive map displayed in HTML
format.

# License: OpenStreetMap (OSM) data is available under the Open Database
License (ODbL)
