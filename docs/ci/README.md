# Continuous integration

GitHub Actions automation is configured under `.github/`. The current CI
workflow validates the Flask backend, builds its Docker image, scans it for
critical vulnerabilities, and pushes the image to Docker Hub.

## Guides

- [Workflows](workflows/README.md)

## Configuration

The workflow definition is
[`ci.yaml`](../../.github/workflows/ci.yaml). It requires these repository
Actions secrets for Docker Hub authentication:

- `DOCKER_USER`
- `DOCKER_PASS`

Configure them under the repository's **Settings > Secrets and variables >
Actions**. Do not store registry credentials in the workflow file or source
code.

## Current scope

The workflow is limited to the Flask backend and triggers for pushes to, and
pull requests targeting, the `dev` branch. Review the
[workflow guide](workflows/README.md) for the job steps, image tagging,
security gate, and branch/fork behavior.
