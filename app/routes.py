from flask import request, jsonify, render_template
from app import app, db
from app.geoDataFetcher import GeoDataFetcher
from pymongo import GEOSPHERE

# ensuring the collection has a geospatial index foe efficient querying 
collection = db.attractions
collection.create_index([('attractions.location', GEOSPHERE)])

@app.route('/')
def index():
    # render the main html page
    return render_template('index.html')

# Endpoint to fetch the attractions given a place or coordinates.
@app.route('/getAttractions', methods=['POST'])
def get_attractions():
    try:
        place = request.json.get('place') # getting the place name or coordinates from request 
        geo_fetcher = GeoDataFetcher(db) # instantiating the geodatafetcher with the database
        response_data = geo_fetcher.get_attractions(place) # fetch attractions data
        return jsonify(response_data) # get them back as json
    except Exception as e:
        app.logger.error(f"Error fetching attractions: {e}") # log error
        return jsonify({"error": "An error occurred while fetching attractions."}), 500 # return error response


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
        }).sort([('timestamp', -1)]).limit(10) # sorted by descending order of timestamp

        # Converting MongoDB cursor to list of dictionaries
        attractions_list = []
        for attraction in cursor:
            # Converting ObjectId to string
            attraction['_id'] = str(attraction['_id'])
            attractions_list.append(attraction)

        # Closing the cursor
        cursor.close()

        # Returning JSON response
        return jsonify(attractions_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# Endpoint to fetch attractions within a radius
@app.route('/nearby_attractions', methods=['GET'])
def get_attractions_within_a_radius():
    # Retrieving query parameters from the request URL
    longitude = request.args.get('longitude', type=float, default=-87.6298)
    latitude = request.args.get('latitude', type=float, default=41.8781)
    max_distance = request.args.get('max_distance', type=int, default=5000)  # distance in meters
    limit = request.args.get('limit', type=int, default=10)  # number of results to return

    try:
        # Defining the aggregation pipeline for geoNear query
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
                    'key': 'attractions.location'  # Specifying the geospatial index key
                }
            },
            {
                '$unwind': '$attractions'  # Unwinding the attractions array
            },
            {
                '$group': {
                    '_id': '$attractions.name',  # Grouping by attraction name to remove duplicates
                    'place': {'$first': '$place'},  # Retaining the place field from the first document
                    'name': {'$first': '$attractions.name'},  # Retaining the attraction name
                    'lat': {'$first': '$attractions.lat'},  # Retaining the attraction latitude
                    'lon': {'$first': '$attractions.lon'},  # Retaining the attraction longitude
                    'distance': {'$first': '$distance'}  # Retaining the calculated distance
                }
            },
            {
                '$limit': limit  # Limiting the number of results to return
            },
            {
                '$project': {
                    '_id': 0,  # Excluding the _id field from the output
                    'place': 1,  # Including the place field
                    'name': 1,  # Including the name field
                    'lat': 1,  # Including the lat field
                    'lon': 1,  # Including the lon field
                    'distance': 1  # Including the distance field
                }
            }
        ]

        # Executing the aggregation pipeline and fetch results
        results = list(collection.aggregate(pipeline))

        # Return the results as JSON response with HTTP status code 200
        return jsonify(results), 200

    except Exception as e:
        # Handling any exceptions and return an error response with http status code 500
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) # run flask in debug mode

