from flask import Flask, request
from src import get_chaughadiya, get_muhurat

app = Flask(__name__)

@app.route('/api/get-chaughadiya', methods=['GET'])
def api_get_chaughadiya():
    """
    Returns the chaughadiya for the given date.
    """
    date = request.args.get('date')
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    response = get_chaughadiya(date, latitude, longitude)
    return response

@app.route('/api/get-muhurat', methods=['GET'])
def api_get_muhurat():
    """
    Returns the muhurat for the given timestamp.
    """
    timestamp = request.args.get('timestamp')
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    response = get_muhurat(timestamp, latitude, longitude)
    return response

if __name__ == '__main__':
    app.run(debug=True)