# Logstash

Logstash ingests log events and forwards them to Elasticsearch. The directory
contains a Deployment, internal TCP Service, persistent data claim, and a
Kustomize configuration that generates the pipeline ConfigMap.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `deployment.yaml` | Deployment `logstash` | Runs one Logstash 8.17.0 pod. |
| `pvc.yaml` | PVC `logstash-data` | Requests 2 GiB for Logstash data and file-input state. |
| `service.yaml` | Service `logstash` | Exposes the TCP input on port `5000` inside the cluster. |
| `kustomization.yaml` | Kustomization | Includes the resources and generates `logstash-pipeline` from the pipeline files. |
| `pipeline/` | Pipeline configuration | Defines the CSV and JSON event inputs. See the [pipeline guide](pipeline/README.md). |

## Runtime and data flow

- The TCP input listens on port `5000`; JSON Lines events are parsed by the
  JSON pipeline.
- Logstash connects to `http://elasticsearch:9200`.
- The generated `logstash-pipeline` ConfigMap is mounted read-only at
  `/usr/share/logstash/pipeline`.
- The `logstash-data` claim is mounted at `/usr/share/logstash/data`. File
  inputs read from subdirectories under this path and store their `sincedb`
  state there.
- Port `9600` is exposed by the container for Logstash monitoring probes; it
  is not published by the Kubernetes Service.
- The pod requests `250m` CPU and `512 MiB` memory, with a `1 GiB` memory
  limit.

## Apply and verify

The root Kustomization includes this directory as a nested Kustomization:

```shell
kubectl apply -k k8s/
kubectl get deployment,service,pvc -n logcommerce
kubectl logs deployment/logstash -n logcommerce
```

The `logcommerce` namespace and Elasticsearch endpoint must be available. The
pipeline ConfigMap is generated from the files listed in
`k8s/logstash/kustomization.yaml`; after editing a pipeline, reapply the
Kustomize build so its generated ConfigMap is updated.

## Operational notes

The TCP input is reachable only within the cluster through the `logstash`
ClusterIP Service. Provide CSV or JSON files to the mounted data volume if
using the file inputs; the manifests do not define a file-ingestion producer
or an automated file-copy process.
