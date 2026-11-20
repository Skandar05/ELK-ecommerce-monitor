# Web application

The web application manifests configure the Flask backend, its runtime
environment, and its internal Service. This directory is optional and is not
included in the root `k8s/kustomization.yaml`.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `configmap.yaml` | ConfigMap `webapp-config` | Supplies non-secret service endpoints and application settings. |
| `deployment.yaml` | Deployment `webapp` | Runs one backend pod using `skandar55/monitoring-backend:latest`. |
| `service.yaml` | Service `webapp` | Exposes HTTP port `5000` inside the cluster. |

## Configuration and dependencies

The container listens on port `5000`. The ConfigMap configures these service
endpoints:

| Variable | Configured value |
|---|---|
| `ELASTICSEARCH_HOSTS` | `http://elasticsearch:9200` |
| `LOGSTASH_HOST` / `LOGSTASH_PORT` | `logstash` / `5000` |
| `MONGO_HOST` / `MONGO_PORT` | `mongodb` / `27017` |
| `MONGO_DATABASE` / `MONGO_AUTH_SOURCE` | `logcommerce` / `admin` |
| `REDIS_HOST` / `REDIS_PORT` | `redis` / `6379` |

The Deployment also requires these keys in the `logcommerce-secrets` Secret:

- `mongo-root-username`
- `mongo-root-password`
- `redis-password`
- `flask-secret-key`

The pod requests `100m` CPU and `128 MiB` memory, with a `512 MiB` memory
limit. Startup, readiness, and liveness probes check the container's HTTP
port.

## Apply and verify

Apply the ConfigMap, Deployment, and Service after deploying the core
dependencies and creating the required Secret:

```shell
kubectl apply -f k8s/webapp/configmap.yaml
kubectl apply -f k8s/webapp/deployment.yaml
kubectl apply -f k8s/webapp/service.yaml
kubectl get deployment,service,pod -n logcommerce
kubectl logs deployment/webapp -n logcommerce
```

The Deployment uses the image `skandar55/monitoring-backend:latest`; ensure the
cluster can pull the image and that it listens on port `5000`. The
[Ingress](../ingress/README.md) is a separate resource and can route
`logcommerce.local/` to this Service.

## Security and operations

Keep credentials and the Flask secret key in a protected Kubernetes Secret,
not in the ConfigMap or source control. The default replica count is one; add
replicas only after confirming the backend supports the intended scaling and
session behavior.
