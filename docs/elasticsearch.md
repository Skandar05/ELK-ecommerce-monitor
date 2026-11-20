# Elasticsearch

Elasticsearch stores and searches the platform's indexed log events. Its
manifests define a single-node StatefulSet, persistent data storage, runtime
configuration, and internal Kubernetes Services.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `configmap.yaml` | ConfigMap `elasticsearch-config` | Supplies `elasticsearch.yml`. |
| `pvc.yaml` | PVC `elasticsearch-data` | Requests 10 GiB of persistent data storage. |
| `service.yaml` | Services `elasticsearch-headless`, `elasticsearch` | Provides StatefulSet identity and internal HTTP access. |
| `statefulset.yaml` | StatefulSet `elasticsearch` | Runs one Elasticsearch 8.17.0 pod. |

## Configuration and connectivity

- HTTP listens on port `9200`; transport listens on `9300`.
- The `elasticsearch` ClusterIP Service exposes HTTP internally at
  `http://elasticsearch:9200`. The headless Service exposes both named ports
  for pod identity and transport.
- The ConfigMap sets the cluster name to `logcommerce`, enables single-node
  discovery, disables memory mapping, and disables Elasticsearch security.
- Logstash and Kibana use the internal HTTP Service.
- The pod requests `500m` CPU and `1 GiB` memory, with a `2 GiB` memory limit.
  The JVM heap is configured to `512 MiB`.
- The data claim uses `ReadWriteOnce`; the cluster needs a compatible
  provisioner or pre-provisioned volume.

## Apply and verify

Elasticsearch is included in the root Kustomize deployment:

```shell
kubectl apply -k k8s/
kubectl get statefulset,pod,service,pvc -n logcommerce
kubectl logs statefulset/elasticsearch -n logcommerce
```

Check the internal endpoint from a pod in the namespace:

```shell
kubectl run es-check --rm -it --restart=Never -n logcommerce \
  --image=curlimages/curl -- curl -fsS http://elasticsearch:9200/
```

## Security and operations

Authentication and authorization are disabled in this configuration. Keep the
service internal to a trusted cluster network; do not expose it directly to the
public Internet. Use an appropriately secured Elasticsearch configuration for
production workloads.

The single replica and single PVC are suitable for development and small
demonstrations, but do not provide node-level high availability.
