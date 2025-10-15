from flask import Flask, request, render_template, jsonify
from src import get_chaughadiya, get_muhurat
import datetime

app = Flask(__name__)

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