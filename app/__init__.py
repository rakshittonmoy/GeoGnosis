from flask import Flask
from config import Config
from pymongo import MongoClient
import logging
import os

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')
logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# MongoDB setup
client = MongoClient(app.config['MONGO_URI'])
db = client.osm_data

from app import routes