# Kubernetes deployment

This guide covers the manifests in `k8s/` for the LogCommerce monitoring
platform. The resources use the `logcommerce` namespace and connect the
Elasticsearch, Logstash, Kibana, MongoDB, and Redis services.

## Directory guides

- [Elasticsearch](elasticsearch/README.md)
- [Ingress](ingress/README.md)
- [Kibana](kibana/README.md)
- [Logstash](logstash/README.md)
- [Logstash pipelines](logstash/pipeline/README.md)
- [MongoDB](mongodb/README.md)
- [Redis](redis/README.md)
- [Web application](webapp/README.md)

## Deployment scope

The root [Kustomization](../../k8s/kustomization.yaml) applies the namespace,
Elasticsearch, Logstash, Kibana, MongoDB, and Redis. It does **not** include
the `webapp/` or `ingress/` directories. Apply those resources separately when
you want to expose the application.

Before deploying, ensure the cluster has a default StorageClass for the
PersistentVolumeClaims and create the `logcommerce-secrets` Secret. The
workload manifests expect the Secret keys documented in the relevant
[MongoDB](mongodb/README.md), [Redis](redis/README.md), and
[web application](webapp/README.md) guides. Follow the project
[README](../../README.md) for the repository's secret-creation procedure.

Deploy the core stack:

```shell
kubectl apply -k k8s/
```

Apply the optional web application and Ingress after the core services are
available:

```shell
kubectl apply -f k8s/webapp/configmap.yaml
kubectl apply -f k8s/webapp/deployment.yaml
kubectl apply -f k8s/webapp/service.yaml
kubectl apply -f k8s/ingress/ingress.yaml
```

The cluster must have an Ingress controller matching the manifest's `nginx`
IngressClass. Configure name resolution for `logcommerce.local` to reach the
Ingress controller before using the host-based routes.

## Verify the deployment

```shell
kubectl get pods,services,pvc -n logcommerce
kubectl get ingress -n logcommerce
```

Use `kubectl describe` on a pending PVC or workload, and `kubectl logs` on a
pod, to investigate scheduling, storage, startup, or application issues.

## Operational considerations

- Elasticsearch has `xpack.security.enabled: false` and is intended for a
  trusted local or development cluster, not direct exposure to an untrusted
  network.
- MongoDB and Redis read credentials from a Kubernetes Secret. Protect that
  Secret and do not commit generated credentials to the repository.
- Each database uses a single replica and a `ReadWriteOnce` claim. These
  manifests provide persistent local state, not a highly available production
  topology.
- Inspect the individual service guides for ports, storage requests, health
  checks, configuration, and service exposure.
