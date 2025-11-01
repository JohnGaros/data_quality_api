# Infrastructure Assets

## Purpose
- Houses everything needed to deploy the platform in the cloud or on Kubernetes.
- Keeps infrastructure-as-code close to the application so changes stay in sync.

## Structure
- `azure/`: templates and policies for Azure-native services (Key Vault, API Management, monitoring).
- `k8s/`: Kubernetes manifests for running the API and supporting services.
- `ci_cd/`: pipeline definitions for build, test, and deployment automation.
- Root files like `Dockerfile` or `docker-compose.yaml` support container builds and local orchestration.

## When to use
- Planning new environments (dev, test, prod).
- Reviewing security controls with cloud teams.
- Coordinating releases with DevOps or platform engineering.

