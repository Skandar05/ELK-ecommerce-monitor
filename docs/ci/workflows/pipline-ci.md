# GitHub Actions workflows

The `.github/workflows/` directory currently contains one workflow:

| Workflow file | Display name | Purpose |
|---|---|---|
| [`ci.yaml`](../../../.github/workflows/ci.yaml) | Flask CI | Checks the Flask backend, builds and scans its Docker image, then pushes the image to Docker Hub. |

## Triggers

The workflow runs on:

- `push` events to the `dev` branch.
- `pull_request` events targeting the `dev` branch.

It does not currently run for pushes or pull requests targeting other branches.

## Backend job

The `backend` job runs on `ubuntu-latest` with `App/backend` as its default
working directory. Its steps execute in this order:

1. Check out the repository with `actions/checkout@v4`.
2. Set up Python 3.11 with `actions/setup-python@v5`.
3. Install packages from `requirements.txt`.
4. Compile Python files with `python -m compileall -q .`.
5. Run a Flask test-client smoke check asserting that `GET /` returns HTTP
   `200`.
6. Log in to Docker Hub with the `DOCKER_USER` and `DOCKER_PASS` Actions
   secrets.
7. Build the image `skandar55/monitoring-backend:latest` from the backend
   directory.
8. Scan that image with Trivy for `CRITICAL` severity vulnerabilities. The
   job fails if the scan reports a critical finding.
9. Push the image to Docker Hub. This step only runs if preceding steps,
   including the scan, succeed.

The Python checks are a syntax check and a single endpoint smoke test; the
workflow does not currently run a dedicated test suite.

## Secrets and pull-request behavior

Add these repository Actions secrets before expecting Docker steps to succeed:

- `DOCKER_USER`: Docker Hub username.
- `DOCKER_PASS`: Docker Hub password or access token.

The Docker login, build, scan, and push steps are not conditional on event
type. GitHub does not provide repository secrets to workflows triggered by
pull requests from forks, so the Docker login step will fail for those runs.
If fork pull requests should receive the Python checks, update the workflow to
skip or safely separate the secret-dependent Docker steps for that event.

## Image and security notes

- The workflow always builds and pushes the mutable `latest` tag. Consumers
  cannot use that tag alone to identify an immutable build.
- The Trivy action is referenced as `aquasecurity/trivy-action@master`.
  Consider pinning third-party actions to a reviewed version or commit SHA
  when tightening supply-chain controls.
- Only `CRITICAL` findings are configured as a failing scan; other severity
  levels are not used as a gate by this workflow.
- Since the push step follows the scan, a failed critical-vulnerability scan
  prevents publication of the image.

## Related documentation

- [Backend implementation and local run instructions](../../app/backend/README.md)
- [CI overview](../README.md)
