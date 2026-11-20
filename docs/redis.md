# Redis

Redis provides the application's cache and session-related storage. The
manifests run one Redis StatefulSet with persistent storage, password
authentication, and internal Services.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `pvc.yaml` | PVC `redis-data` | Requests 1 GiB with `ReadWriteOnce` access. |
| `service.yaml` | Services `redis-headless`, `redis` | Provides StatefulSet identity and an internal client endpoint. |
| `statefulset.yaml` | StatefulSet `redis` | Runs Redis 7 with append-only persistence enabled. |

## Configuration and connectivity

- The client-facing ClusterIP Service is `redis:6379`.
- Redis starts with append-only persistence enabled and requires a password
  read from the `logcommerce-secrets` Secret key `redis-password`.
- The web application Deployment reads the same password into
  `REDIS_PASSWORD`.
- The pod requests `100m` CPU and `128 MiB` memory, with a `512 MiB` memory
  limit.
- The PVC is mounted at `/data`. A compatible StorageClass or pre-provisioned
  volume is required.
- Readiness and liveness probes authenticate with `REDISCLI_AUTH` before
  running `redis-cli ping`.

## Apply and verify

Redis is included in the root Kustomize deployment:

```shell
kubectl apply -k k8s/
kubectl get statefulset,service,pod,pvc -n logcommerce
kubectl logs statefulset/redis -n logcommerce
```

Create the `logcommerce-secrets` Secret before starting the StatefulSet. Check
that its `redis-password` key is present if the pod fails its probes.

## Security and operations

Keep the Redis Service internal and protect the password Secret. The single
replica and append-only file persistence do not provide replication or
high availability.
