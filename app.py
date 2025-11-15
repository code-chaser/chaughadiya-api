from flask import Flask, request, render_template, jsonify
from src import get_chaughadiya, get_muhurat, get_tithi, get_tithi_for_date_range
import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# Configuration for self-ping
SELF_PING_INTERVAL = 600  # 10 minutes (600 seconds)
SELF_PING_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:8080') + '/health'

def keep_alive():
    """
    Background task that pings the service periodically to prevent it from spinning down.
    Only runs if RENDER_EXTERNAL_URL is set (i.e., deployed on Render).
    """
    while True:
        time.sleep(SELF_PING_INTERVAL/2)
        try:
            # Only ping if we're on Render (RENDER_EXTERNAL_URL is set)
            if os.environ.get('RENDER_EXTERNAL_URL'):
                response = requests.get(SELF_PING_URL, timeout=10)
                print(f"[Keep-Alive] Ping successful: {response.status_code}")
        except Exception as e:
            print(f"[Keep-Alive] Ping failed: {str(e)}")
        time.sleep(SELF_PING_INTERVAL/2)
        

# Start the keep-alive thread only if deployed on Render
if os.environ.get('RENDER_EXTERNAL_URL'):
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("[Keep-Alive] Background thread started")

@app.route('/api/get-chaughadiya', methods=['GET'])
def api_get_chaughadiya():
    """
    Returns the chaughadiya for the given date.
    """
    try:
        # Validate required parameters
        date = request.args.get('date')
        if not date:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        # Validate date format
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate latitude
        latitude_str = request.args.get('latitude')
        if not latitude_str:
            return jsonify({'error': 'Latitude parameter is required'}), 400
        
        try:
            latitude = float(latitude_str)
            if not (-90 <= latitude <= 90):
                return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid latitude value'}), 400
        
        # Validate longitude
        longitude_str = request.args.get('longitude')
        if not longitude_str:
            return jsonify({'error': 'Longitude parameter is required'}), 400
        
        try:
            longitude = float(longitude_str)
            if not (-180 <= longitude <= 180):
                return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid longitude value'}), 400
        
        response = get_chaughadiya(date, latitude, longitude)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/get-muhurat', methods=['GET'])
def api_get_muhurat():
    """
    Returns the muhurat for the given timestamp.
    """
    try:
        # Validate required parameters
        timestamp = request.args.get('timestamp')
        if not timestamp:
            return jsonify({'error': 'Timestamp parameter is required'}), 400
        
        # Validate timestamp format
        try:
            datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        # Validate latitude
        latitude_str = request.args.get('latitude')
        if not latitude_str:
            return jsonify({'error': 'Latitude parameter is required'}), 400
        
        try:
            latitude = float(latitude_str)
            if not (-90 <= latitude <= 90):
                return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid latitude value'}), 400
        
        # Validate longitude
        longitude_str = request.args.get('longitude')
        if not longitude_str:
            return jsonify({'error': 'Longitude parameter is required'}), 400
        
        try:
            longitude = float(longitude_str)
            if not (-180 <= longitude <= 180):
                return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid longitude value'}), 400
        
        response = get_muhurat(timestamp, latitude, longitude)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/get-tithi', methods=['GET'])
def api_get_tithi():
    """
    Returns the Tithi (lunar day) for the given date and location.
    """
    try:
        # Validate required parameters
        date = request.args.get('date')
        if not date:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        # Validate date format (accept both YYYY-MM-DD and YYYY-MM-DD HH:MM:SS)
        try:
            if len(date) == 10:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS'}), 400
        
        # Validate latitude
        latitude_str = request.args.get('latitude')
        if not latitude_str:
            return jsonify({'error': 'Latitude parameter is required'}), 400
        
        try:
            latitude = float(latitude_str)
            if not (-90 <= latitude <= 90):
                return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid latitude value'}), 400
        
        # Validate longitude
        longitude_str = request.args.get('longitude')
        if not longitude_str:
            return jsonify({'error': 'Longitude parameter is required'}), 400
        
        try:
            longitude = float(longitude_str)
            if not (-180 <= longitude <= 180):
                return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid longitude value'}), 400
        
        # Get timezone parameter (optional, defaults to UTC)
        timezone = request.args.get('timezone', 'UTC')
        
        response = get_tithi(date, latitude, longitude, timezone)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/get-tithi-range', methods=['GET'])
def api_get_tithi_range():
    """
    Returns the Tithi for a range of dates.
    """
    try:
        # Validate required parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Both start_date and end_date parameters are required'}), 400
        
        # Validate date formats
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate latitude
        latitude_str = request.args.get('latitude')
        if not latitude_str:
            return jsonify({'error': 'Latitude parameter is required'}), 400
        
        try:
            latitude = float(latitude_str)
            if not (-90 <= latitude <= 90):
                return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid latitude value'}), 400
        
        # Validate longitude
        longitude_str = request.args.get('longitude')
        if not longitude_str:
            return jsonify({'error': 'Longitude parameter is required'}), 400
        
        try:
            longitude = float(longitude_str)
            if not (-180 <= longitude <= 180):
                return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid longitude value'}), 400
        
        # Get timezone parameter (optional, defaults to UTC)
        timezone = request.args.get('timezone', 'UTC')
        
        response = get_tithi_for_date_range(start_date, end_date, latitude, longitude, timezone)
        return jsonify({'tithis': response})
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint for keep-alive pings.
    """
    return jsonify({'status': 'ok', 'timestamp': datetime.datetime.now().isoformat()}), 200

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """
    Returns the documentation for the API.
    """
    return render_template('./static/api-documentation.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    Returns the 404 page.
    """
    return render_template('./static/page-not-found.html'), 404

@app.route('/')
def home():
    """
    Returns the home page.
    """
    return render_template('./static/home.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)