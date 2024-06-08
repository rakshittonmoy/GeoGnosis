import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    OVERPASS_URL = 'http://overpass-api.de/api/interpreter'