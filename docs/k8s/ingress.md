# Ingress

The Ingress routes HTTP traffic for `logcommerce.local` to the web application
and Kibana. It is an optional resource and is not included in the root
Kustomization.

## Manifest inventory

| File | Resource | Purpose |
|---|---|---|
| `ingress.yaml` | Ingress `logcommerce` | Routes `/` to the web app and `/kibana` to Kibana. |

## Routing

| Host | Path prefix | Backend Service | Backend port |
|---|---|---|---:|
| `logcommerce.local` | `/` | `webapp` | `5000` |
| `logcommerce.local` | `/kibana` | `kibana` | `5601` |

The manifest selects the `nginx` IngressClass and sets the NGINX
`proxy-body-size` annotation to `10m`. TLS is not configured.

## Prerequisites and apply

Before applying this manifest:

1. Install an Ingress controller that serves the `nginx` IngressClass.
2. Deploy the backend Services. The web application is optional and is not part
   of the root Kustomization.
3. Configure DNS or a local hosts-file entry for `logcommerce.local` to point
   to the Ingress controller's address.

```shell
kubectl apply -f k8s/ingress/ingress.yaml
kubectl get ingress -n logcommerce
kubectl describe ingress logcommerce -n logcommerce
```

After DNS and the controller are configured, the intended routes are
`http://logcommerce.local/` and `http://logcommerce.local/kibana`.

## Operational notes

- The `/kibana` route matches the Kibana base path configured in
  `k8s/kibana/configmap.yaml`.
- This manifest provides HTTP routing only; configure TLS separately if
  encrypted client connections are required.
- Check the Ingress controller's events and logs if the resource has no address
  or requests do not reach the backend Services.
