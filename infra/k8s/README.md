# Kubernetes Manifests

## Purpose
- Stores YAML files that describe how the API and supporting services run on Kubernetes.
- Supports portable deployments across dev, test, and production clusters.

## Key manifests
- `api-deployment.yaml` and `api-service.yaml`: define the API pods and network endpoints.
- `postgres-deployment.yaml`: example database deployment, adjustable per environment.
- `storage-secrets.yaml`: references secrets mounted into pods.

## Practical guidance
- Use these manifests as a starting point; adjust replicas, resources, and namespaces per environment.
- Coordinate with the infrastructure team before applying changes to shared clusters.
- Keep security policies (network, RBAC) aligned with the metadata and compliance requirements.

