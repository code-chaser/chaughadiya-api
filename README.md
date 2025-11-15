# Chaughadiya API

Modern Flask API that serves Hindu calendar utilities including Chaughadiya, Muhurat,
and Tithi calculations. The service is production ready with an application-factory
architecture, strict request validation, and clear separation between routing,
services, and domain logic.

## Features

- REST API powered by Flask 3 with blueprints and centralized error handling
- High-fidelity Chaughadiya calculations backed by the `suntime` library
- Detailed Tithi calculations using Swiss Ephemeris (`pyswisseph`)
- Automated keep-alive pings for Render deployments
- HTML landing page and docs served from the same process
- Ready-to-run health endpoint, logging, and testing stubs

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=app.py flask run
```

Environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `FLASK_ENV` | `development`, `testing`, `production` | `production` |
| `RENDER_EXTERNAL_URL` | Public URL used for keep-alive pings | `http://localhost:8080` |
| `KEEP_ALIVE_INTERVAL` | Seconds between keep alive pings | `600` |

## API Overview

| Endpoint | Description | Required parameters |
| --- | --- | --- |
| `GET /api/get-chaughadiya` | Full chaughadiya table for a date | `date`, `latitude`, `longitude` |
| `GET /api/get-muhurat` | Current muhurat for a timestamp | `timestamp`, `latitude`, `longitude` |
| `GET /api/get-tithi` | Tithi for a moment/location | `date`, `latitude`, `longitude` |
| `GET /api/get-tithi-range` | Tithi across a date range | `start_date`, `end_date`, `latitude`, `longitude` |

All parameters must be supplied as query string values. Optional `timezone`
defaults to `UTC` for Tithi requests.

## Project Layout

```
├── app.py                # Entry point that instantiates the Flask app
├── chaughadiya_api/      # Application package
│   ├── api/              # API blueprints and routes
│   ├── pages/            # Public pages (home, docs, health)
│   ├── services/         # Thin services wrapping domain logic
│   ├── domain/           # Pure calculation modules
│   ├── schemas/          # Request parsers & validators
│   ├── utils/            # Shared utilities
│   └── config.py         # Config classes & logging helpers
└── templates/            # HTML templates (home, docs, etc.)
```

## Testing

Add your tests under `tests/` and run them with:

```bash
pytest
```

Because Tithi calculations depend on Swiss Ephemeris, ensure the native
dependencies for `pyswisseph` are available on your system before running tests.
