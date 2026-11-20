# Application

The `App/` directory is organized into a backend and a frontend. The backend
currently contains a small Flask API; the frontend directory is an empty
placeholder with no application source or build configuration.

## Component guides

- [Backend](backend/README.md)
- [Frontend](frontend/README.md)

## Current application scope

The backend exposes a welcome route, a hello endpoint, and a sample users
endpoint. The users are hard-coded in the application. Although the Python
requirements include packages for Elasticsearch, MongoDB, Redis, and CORS,
the current Flask source does not yet connect to those services or configure
CORS.

The Kubernetes web application Deployment expects a container image named
`skandar55/monitoring-backend:latest`. Review the
[backend guide](backend/README.md) and
[Kubernetes Deployment manifest](../../k8s/webapp/deployment.yaml) when
building or publishing an image so the image name and tag match.
