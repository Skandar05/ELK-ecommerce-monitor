# Kibana

Kibana provides a web interface for exploring Elasticsearch data. The
manifests configure one Kibana 8.17.0 pod, its base path, and a Kubernetes
Service.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `configmap.yaml` | ConfigMap `kibana-config` | Supplies Kibana server and Elasticsearch settings. |
| `deployment.yaml` | Deployment `kibana` | Runs one Kibana pod and mounts its configuration. |
| `service.yaml` | Service `kibana` | Exposes port `5601` to cluster clients. |

## Configuration and connectivity

- Kibana listens on `0.0.0.0:5601` and connects to
  `http://elasticsearch:9200`.
- Its base path is `/kibana`; `server.rewriteBasePath` is enabled and the
  public URL is configured as `http://logcommerce.local/kibana`.
- The Service is declared as `LoadBalancer` and exposes HTTP port `5601`.
  Availability of an external address depends on the cluster's load-balancer
  implementation.
- The pod requests `250m` CPU and `512 MiB` memory, with a `1 GiB` memory
  limit. Startup, readiness, and liveness probes check the HTTP listener and
  Kibana status endpoint.

## Apply and verify

Kibana is included in the root Kustomize deployment:

```shell
kubectl apply -k k8s/
kubectl get deployment,service,pod -n logcommerce
kubectl logs deployment/kibana -n logcommerce
```

The optional [Ingress](../ingress/README.md) routes `/kibana` to the Service.
The Ingress resource must be applied separately, and the cluster must have an
NGINX Ingress controller for that route.

## Operational notes

Elasticsearch must be reachable at the configured Service name. Kibana's
readiness probe uses `/kibana/api/status`, so keep the probe and base-path
configuration aligned if the URL prefix is changed.
