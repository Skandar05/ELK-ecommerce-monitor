# Logstash pipelines

This directory contains the Logstash pipeline configurations generated into
the `logstash-pipeline` ConfigMap by the parent Kustomization. The Deployment
mounts that ConfigMap at `/usr/share/logstash/pipeline`.

## Pipeline files

| File | Input | Processing and output |
|---|---|---|
| `csv.conf` | CSV files in `/usr/share/logstash/data/input/csv/*.csv` | Parses `timestamp`, `service`, `level`, and `message`; writes to `ecommerce-csv-*` indices. |
| `json.conf` | JSON Lines over TCP port `5000`, and JSON files in `/usr/share/logstash/data/input/json/*.json` | Writes events to `ecommerce-json-*` indices. |

## CSV pipeline

The CSV input starts reading files from the beginning and stores its file
tracking state at `/usr/share/logstash/data/sincedb-csv`. It uses a comma
separator, expects a header row, and maps columns in this order:
`timestamp`, `service`, `level`, `message`. Events are indexed in
`ecommerce-csv-YYYY.MM.dd`.

## JSON pipeline

The TCP input listens on port `5000` and uses the `json_lines` codec, so send
one JSON object per line. The file input reads `.json` files with the JSON
codec and stores its tracking state at
`/usr/share/logstash/data/sincedb-json`. Events are indexed in
`ecommerce-json-YYYY.MM.dd`.

Both pipelines send data to `http://elasticsearch:9200`. The input directories
are paths on the Logstash data volume; these manifests do not populate them.
Arrange for files to be present in the volume before expecting file-based
ingestion.

## Updating and verifying

Edit the relevant `.conf` file, then rebuild and apply the parent
Kustomization:

```shell
kubectl apply -k k8s/
kubectl logs deployment/logstash -n logcommerce
```

Kustomize generates a content-hashed ConfigMap name and updates the Deployment
reference when the pipeline content changes.
