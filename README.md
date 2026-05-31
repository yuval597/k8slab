# k8slab

## 1. Project Overview

End-to-end DevOps CI pipeline for a containerized Python application. This repository demonstrates a real CI workflow that builds, validates, and publishes container images and Helm charts — suitable for later deployment into Kubernetes.

From a DevOps perspective, the project focuses on automation patterns for building and releasing containerized applications (CI), validating infrastructure templates (Helm), managing secrets for CI, and providing feedback via notifications.

Problems it addresses:
- Automates Docker image builds and image publishing.
- Validates Helm chart rendering in CI to catch template/configuration issues early.
- Demonstrates CI pipeline patterns, secrets handling, and notification hooks.


## 2. Architecture Overview

Flow (actual implemented flow in this repository):

Developer → GitHub Repository → GitHub Actions CI Pipeline → Checkout repository → Docker login → Docker build → Docker image push to DockerHub → Helm template validation → Slack notification

- Developer: pushes commits or manually triggers the workflow.
- GitHub Actions: executes jobs on hosted runners.
- Checkout: `actions/checkout` fetches repository files to the runner.
- Docker login: `docker/login-action` authenticates to DockerHub using repository secrets.
- Docker build & push: runner builds the image using the `Dockerfile` and pushes it to DockerHub.
- Helm template validation: CI runs `helm template` to render Kubernetes manifests locally and validate templating and values.
- Slack notification: posts the build status and metadata to a Slack webhook.

Note: This pipeline does not automatically deploy to a Kubernetes cluster. The Helm chart is prepared for deployment, but deployment to a cluster would be performed separately (for example with `helm upgrade --install` or via a GitOps tool like ArgoCD).


## 3. Repository Structure

- [app.py](app.py) — Application source code (Flask web app).
- [Dockerfile](Dockerfile) — Container build instructions.
- [requirements.txt](requirements.txt) — Python dependencies.
- [get_helm.sh](get_helm.sh) — Helper script for installing Helm (from upstream Helm project).
- [k8s/Chart.yaml](k8s/Chart.yaml) — Helm chart metadata.
- [k8s/values.yaml](k8s/values.yaml) — Helm default values.
- [k8s/templates/](k8s/templates/) — Helm templates:
  - `_helpers.tpl` — template helpers/labels
  - `configmap.yaml` — ConfigMap template
  - `deployment.yaml` — Deployment template (image/tag/ports)
  - `ingress.yaml` — Ingress template (conditional)
  - `service.yaml` — Service template (port mapping and type)
- [.github/workflows/start.yaml](.github/workflows/start.yaml) — GitHub Actions workflow that builds/pushes the Docker image, renders Helm templates, and sends Slack notification.
- [.gitignore](.gitignore) — ignored files (venv, pyc, env files, keys).

Purpose summary:
- Application files: the runnable Python service.
- Dockerfile: produces a portable container image.
- .github/workflows: CI pipeline for building and validating artifacts.
- Kubernetes/Helm directory: holds chart artifacts to deploy the app to Kubernetes when desired.


## 4. Application Layer

- Language/Framework: Python 3.10 using `Flask`.
- What it does: Serves a simple HTML overview via `/` and starts a Flask server when run.
- Startup: `python app.py` starts the Flask server on `0.0.0.0:5001` when executed as `__main__`.
- Dependencies: Listed in `requirements.txt` (includes `flask`, `boto3`, and utility typing libs).
- Ports: The app listens on port `5001` (container `EXPOSE 5001` in the Dockerfile).
- Runtime behavior: The application runs a Flask process that serves an index page. (Note: previous README references to Prometheus or `/metrics` have been removed — this repository does not include monitoring instrumentation.)


## 5. Docker Implementation

- Build process: The CI runs `docker build -t yuval597/k8slab:${{ github.run_number }} .` inside the repo root.
- Dockerfile steps:
  1. `FROM python:3.10-slim` — lightweight Python base image.
  2. `WORKDIR /app` — set working directory.
  3. `COPY requirements.txt .` — copy dependency manifest.
  4. `RUN pip install --no-cache-dir -r requirements.txt` — install dependencies.
  5. `COPY . .` — copy repository files into the image.
  6. `EXPOSE 5001` — document the listening port.
  7. `CMD ["python", "app.py"]` — start the application.
- Image tagging strategy: CI tags images with the workflow run number (`${{ github.run_number }}`) producing `yuval597/k8slab:<run_number>`; this gives incremental, unique tags for each run.
- DockerHub usage: The workflow logs into DockerHub using `docker/login-action` with `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` stored as repository secrets, then pushes the image.


## 6. GitHub Actions CI/CD Pipeline

Workflow file: [.github/workflows/start.yaml](.github/workflows/start.yaml)

- Trigger: `workflow_dispatch` — manual workflow trigger. Replace or extend with `push`/`pull_request` to run on commits/PRs.

Jobs and flow (actual implementation):
- `hello`: a simple demo action that runs first.
- `build` (`needs: hello`): checks out the repo, logs into DockerHub, builds the Docker image, pushes it to DockerHub, and runs `helm template` to validate Kubernetes manifests.
- `slack-notify` (`needs: build`): posts a Slack notification with repository, branch, image tag, and commit details.

Key steps:
- `uses: actions/checkout@v4`: checks out repository files for subsequent steps.
- `uses: docker/login-action@v4`: logs into DockerHub using secrets.
- `run: docker build ...` and `run: docker push ...`: shell commands executed on the runner to build and push the image.
- `run: helm template k8slab ./k8s`: renders Helm templates locally to validate rendering and configuration — this is a validation step only and does not deploy to Kubernetes.
- `uses: rtCamp/action-slack-notify@v2`: posts to Slack using a webhook secret.

`run` vs `uses`:
- `uses`: reuses a published GitHub Action (container or JavaScript action).
- `run`: executes inline shell commands on the runner.


## 7. Secrets Management

This repository uses GitHub Actions Secrets to store and inject sensitive information into workflows at runtime. Specifically:

- `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` — DockerHub credentials used by `docker/login-action` to authenticate and push images.
- `SLACK_WEBHOOK` — Slack incoming webhook URL used by the Slack notification action.

Best practices applied:
- Secrets are stored in GitHub repository settings (encrypted) and are not committed to Git.
- Secrets are only exposed to workflows at runtime and can be restricted to specific branches/environments.


## 8. Kubernetes & Helm

- Purpose of `helm template` in CI: to validate Helm chart rendering and catch template or configuration issues early in CI.
- Chart contents: `Chart.yaml`, `values.yaml`, and `templates/` with `Deployment`, `Service`, `Ingress` and `ConfigMap` templates.
- Deployment: This repository prepares a Helm chart for Kubernetes deployment. The CI does not perform a cluster deployment. To deploy to a cluster you could run (manually or from a CD process):

```bash
helm upgrade --install k8slab ./k8s -f k8s/values.yaml --set pod.image=yuval597/k8slab --set pod.tag=<tag>
```

- For automated CD you can integrate `helm upgrade --install` into the pipeline or use a GitOps operator like ArgoCD to reconcile the chart from Git.


## 9. Notification Flow

- Slack integration: The `slack-notify` job posts a message to Slack via a webhook using `rtCamp/action-slack-notify`.
- When notifications are sent: after the `build` job completes successfully (the `slack-notify` job is dependent on `build`). The message includes repository, branch, image tag, and commit SHA.


## 10. DevOps Concepts Demonstrated

- Git source control and change-driven pipelines.
- CI: GitHub Actions for building and validating artifacts.
- Docker: containerizing the application and publishing images.
- Helm: templated Kubernetes manifests and values-driven configuration.
- Automation: fully scripted pipeline and notifications.
- Secrets management: secrets stored in GitHub Actions Secrets.
- CI platform migration: the project was originally implemented using Jenkins Pipeline and later migrated/recreated using GitHub Actions, demonstrating understanding of Jenkins stages vs GitHub Actions jobs/steps.


## 11. Future Improvements

- Add `helm upgrade --install` or a gated deployment step to the pipeline to perform actual cluster deployments.
- Adopt ArgoCD or Flux for GitOps continuous delivery and promotion between environments.
- Add unit tests and CI test steps (pytest) to prevent regressions.
- Add container image scanning (Trivy) and CI security checks.
- Add multi-environment values and promotion strategy (dev/stage/prod) using separate `values-*.yaml`.
- Add health/readiness probes, resource requests/limits, and HPA to the chart.
- Add logging/tracing and monitoring (Prometheus/Grafana) as part of observability (listed here as a future improvement, not an existing feature).


## 12. Interview Explanation (Short Pitch)

"I built an end-to-end CI pipeline around a Python application. The application is containerized using Docker, automatically built through GitHub Actions, pushed to DockerHub, validated using Helm charts, and integrated with Slack notifications. I also implemented the pipeline using Jenkins previously to understand different CI/CD approaches. The project is prepared for future Kubernetes deployment using Helm or ArgoCD."


