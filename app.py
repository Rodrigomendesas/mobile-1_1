from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from functools import wraps
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

BASE_URL = 'https://api.openweathermap.org/data/3.0/onecall'

def validate_params(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        if not lat or not lon:
            raise BadRequest('Latitude and longitude are required')
        try:
            float(lat)
            float(lon)
        except ValueError:
            raise BadRequest('Latitude and longitude must be valid numbers')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/weather', methods=['GET'])
@validate_params
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    exclude = request.args.get('exclude', default='')

    params = {
        'lat': lat,
        'lon': lon,
        'exclude': exclude,
        'appid': API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)