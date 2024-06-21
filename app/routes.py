from flask import request, jsonify, render_template
from app import app, db
from app.geoDataFetcher import GeoDataFetcher
from pymongo import GEOSPHERE


collection = db.attractions
# Ensure the index for geospatial queries
collection.create_index([('attractions.location', GEOSPHERE)])

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to fetch the attractions given a place or coordinates.
@app.route('/getAttractions', methods=['POST'])
def get_attractions():
    try:
        place = request.json.get('place')
        geo_fetcher = GeoDataFetcher(db)
        response_data = geo_fetcher.get_attractions(place)
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Error fetching attractions: {e}")
        return jsonify({"error": "An error occurred while fetching attractions."}), 500



# Endpoint to fetch the recently searched attractions in the database 
@app.route('/fetchRecentTenAttractions', methods=['GET'])
def get_recent_ten_attractions():
    try:
        # Query MongoDB
        cursor = collection.find({
            '$and': [
                {'place': {'$exists': True}},
                {'attractions': {'$exists': True}},
                {'timestamp': {'$exists': True}}
            ]
        }).sort([('timestamp', -1)]).limit(10) # sorted by descending order of timestamp. 

        # Convert MongoDB cursor to list of dictionaries
        attractions_list = []
        for attraction in cursor:
            # Convert ObjectId to string
            attraction['_id'] = str(attraction['_id'])
            attractions_list.append(attraction)

        # Close the cursor
        cursor.close()

        # Return JSON response
        return jsonify(attractions_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# Endpoint to fetch attractions within a radius
@app.route('/nearby_attractions', methods=['GET'])
def get_attractions_within_a_radius():
    # Retrieve query parameters from the request URL
    longitude = request.args.get('longitude', type=float, default=-87.6298)
    latitude = request.args.get('latitude', type=float, default=41.8781)
    max_distance = request.args.get('max_distance', type=int, default=5000)  # distance in meters
    limit = request.args.get('limit', type=int, default=10)  # number of results to return

    try:
        # Define the aggregation pipeline for geoNear query
        pipeline = [
            {
                '$geoNear': {
                    'near': {
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    },
                    'distanceField': 'distance',
                    'maxDistance': max_distance,
                    'spherical': True,
                    'key': 'attractions.location'  # Specify the geospatial index key
                }
            },
            {
                '$unwind': '$attractions'  # Unwind the attractions array
            },
            {
                '$group': {
                    '_id': '$attractions.name',  # Group by attraction name to remove duplicates
                    'place': {'$first': '$place'},  # Retain the place field from the first document
                    'name': {'$first': '$attractions.name'},  # Retain the attraction name
                    'lat': {'$first': '$attractions.lat'},  # Retain the attraction latitude
                    'lon': {'$first': '$attractions.lon'},  # Retain the attraction longitude
                    'distance': {'$first': '$distance'}  # Retain the calculated distance
                }
            },
            {
                '$limit': limit  # Limit the number of results to return
            },
            {
                '$project': {
                    '_id': 0,  # Exclude the _id field from the output
                    'place': 1,  # Include the place field
                    'name': 1,  # Include the name field
                    'lat': 1,  # Include the lat field
                    'lon': 1,  # Include the lon field
                    'distance': 1  # Include the distance field
                }
            }
        ]

        # Execute the aggregation pipeline and fetch results
        results = list(collection.aggregate(pipeline))

        # Return the results as JSON response with HTTP status code 200
        return jsonify(results), 200

    except Exception as e:
        # Handle any exceptions and return an error response with HTTP status code 500
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

