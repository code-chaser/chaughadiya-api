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

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """
    Returns the documentation for the API.
    """
    return """
    <h1>Chaughadiya API</h1>
    <p>API to get chaughadiya and muhurat.</p>
    <table>
        <thead>
            <tr>
                <th>Endpoint</th>
                <th>Method</th>
                <th>Parameters</th>
                <th>Description</th>
                <th>Example</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>/api/get-chaughadiya</td>
                <td>GET</td>
                <td>
                    <ul>
                        <li>date: string (format: YYYY-MM-DD)</li>
                        <li>latitude: float</li>
                        <li>longitude: float</li>
                    </ul>
                </td>
                <td>Returns the chaughadiya for the given date.</td>
                <td><a href="/api/get-chaughadiya?date=2021-01-01&latitude=23.0225&longitude=72.5714">/api/get-chaughadiya?date=2021-01-01&latitude=23.0225&longitude=72.5714</a></td>
            </tr>
            <tr>
                <td>/api/get-muhurat</td>
                <td>GET</td>
                <td>
                    <ul>
                        <li>timestamp: string (format: YYYY-MM-DD HH:MM:SS)</li>
                        <li>latitude: float</li>
                        <li>longitude: float</li>
                    </ul>
                </td>
                <td>Returns the muhurat for the given timestamp with the chaughadiya of that day.</td>
                <td><a href="/api/get-muhurat?timestamp=2021-01-01 12:00:00&latitude=23.0225&longitude=72.5714">/api/get-muhurat?timestamp=2021-01-01 12:00:00&latitude=23.0225&longitude=72.5714</a></td>
            </tr>
        </tbody>
    </table>
    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 10px;
        }
    </style>
    <p><b>Note:</b> Please provide date and time in UTC timezone.</p>
    """

@app.errorhandler(404)
def page_not_found(e):
    """
    Returns the 404 page.
    """
    return """
    <h1>404</h1>
    <p>Looks like you are lost. Go back to <a href="/">home</a>.</p>
    """, 404

@app.route('/')
def home():
    """
    Returns the home page.
    """
    return """
    <h1>Chaughadiya API</h1>
    <p>Go to <a href="/api/docs">documentation</a>.</p>
    """


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)