from flask import Flask, request, render_template
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