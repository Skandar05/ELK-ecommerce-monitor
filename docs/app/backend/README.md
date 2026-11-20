# Backend

The backend is a Python 3.11 Flask application in `App/backend/`. Its current
implementation is a minimal API example rather than the complete
e-commerce monitoring backend.

## Files

| File | Purpose |
|---|---|
| [`app.py`](../../../App/backend/app.py) | Defines the Flask application and its HTTP routes. |
| [`requirements.txt`](../../../App/backend/requirements.txt) | Pins Python package versions. |
| [`dockerfile`](../../../App/backend/dockerfile) | Builds a Python 3.11 container and starts the application. |
| `.gitignore` | Excludes virtual environments, secrets, caches, and generated files from Git. |
| `.dockerignore` | Currently empty; no files are excluded from the Docker build context. |


## Dependencies

The dependency file pins Flask and supporting packages, including Flask-CORS,
the Elasticsearch Python client, PyMongo, and python-dotenv. Several
transitive dependencies are pinned as well. The current `app.py` only imports
Flask and `jsonify`; it does not yet use the database clients, dotenv, or
CORS.

## Run locally on Windows

From the repository root, create and activate a virtual environment, install
the pinned dependencies, and start the Flask app:

```powershell
py -3.11 -m venv App\backend\.venv
.\App\backend\.venv\Scripts\Activate.ps1
python -m pip install -r App\backend\requirements.txt
python App\backend\app.py
```

The application listens on port `5000`. Check the routes at
`http://localhost:5000/`, `http://localhost:5000/hello`, and
`http://localhost:5000/users`.

## Build and run the container

Build from the backend directory so the Dockerfile and requirements file are
available in the build context:

```powershell
docker build -f App/backend/dockerfile -t logcommerce-backend:local App/backend
docker run --rm -p 5000:5000 logcommerce-backend:local
```

The Dockerfile uses `python:3.11-slim`, installs `requirements.txt`, copies the
build context into `/app`, exposes port `5000`, and starts `python app.py`.
Because `.dockerignore` is empty, local files such as a virtual environment
may be included in the Docker build context; keep the context free of local
artifacts or add appropriate Docker ignore rules.

## Kubernetes image

The repository's [web application Deployment](../../../k8s/webapp/deployment.yaml)
references `skandar55/monitoring-backend:latest`. Ensure the image you build
and publish uses the expected name and tag, or update the deployment
configuration for your registry. The Deployment also supplies service-related
environment variables, but the current Flask source does not consume them.

## Current limitations

- `/users` returns sample data defined in process memory; it is not backed by
  MongoDB.
- Elasticsearch, Logstash, Redis, and environment-based configuration are not
  currently used by `app.py`.
- The app has no frontend templates or static assets in this backend
  directory.
- Debug mode is enabled by the development entry point and is not suitable for
  production.
