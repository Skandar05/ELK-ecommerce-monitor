# MongoDB

MongoDB stores application metadata and other document-oriented data. The
manifests define a single-replica StatefulSet, persistent storage, and
headless and client-facing Services.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `pvc.yaml` | PVC `mongodb-data` | Requests 5 GiB with `ReadWriteOnce` access. |
| `service.yaml` | Services `mongodb-headless`, `mongodb` | Provides StatefulSet identity and an internal client endpoint. |
| `statefulset.yaml` | StatefulSet `mongodb` | Runs MongoDB 7.0 and mounts persistent database storage. |

## Configuration and connectivity

- The client-facing ClusterIP Service is `mongodb:27017`.
- The container initializes the `logcommerce` database and configures the root
  username and password from the `logcommerce-secrets` Secret keys
  `mongo-root-username` and `mongo-root-password`.
- The web application manifest reads the same credentials and sets
  `MONGO_AUTH_SOURCE=admin`.
- The pod requests `250m` CPU and `512 MiB` memory, with a `1 GiB` memory
  limit.
- The PVC is mounted at `/data/db`. A compatible StorageClass or
  pre-provisioned volume is required.
- Readiness runs an authenticated `mongosh` ping; startup and liveness probes
  check the MongoDB TCP port.

## Apply and verify

MongoDB is included in the root Kustomize deployment:

```shell
kubectl apply -k k8s/
kubectl get statefulset,service,pod,pvc -n logcommerce
kubectl logs statefulset/mongodb -n logcommerce
```

Create the `logcommerce-secrets` Secret before starting the StatefulSet. If the
pod does not become ready, confirm the expected Secret keys exist and inspect
the pod events and logs.

## Security and operations

The root database credentials are privileged credentials. Store them in a
protected Secret and do not commit the Secret manifest or credential values.
This single-replica configuration does not provide database replication or
high availability.
