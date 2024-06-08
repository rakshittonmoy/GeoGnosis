from flask import request, jsonify, render_template
from app import app, db
from app.utils import GeoDataFetcher

@app.route('/')
def index():
    return render_template('index.html')

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
