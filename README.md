# k8slab

## 1. Project Overview

k8slab is a reference DevOps demo project demonstrating a full build-and-deploy pipeline for a simple Python web application with monitoring. The project shows how a developer change moves from source control through CI (GitHub Actions), containerization (Docker), image registry (DockerHub), templated Kubernetes manifests (Helm), and finally to a cluster deployment — with notification hooks (Slack).

From a DevOps perspective, this repository focuses on the automation patterns and artifacts required to continuously build, package, validate, and release containerized applications to Kubernetes using Helm.

Problems it solves:
- Demonstrates automated CI for building and publishing Docker images.
- Provides a Helm chart for consistent, parameterized Kubernetes deployments.
- Exposes application metrics for monitoring (Prometheus format).
- Demonstrates basic notification integration (Slack) for pipeline status.


## 2. Architecture Overview

Flow (high level):
Developer → GitHub → GitHub Actions → Docker Build → DockerHub → Helm (templating) → Kubernetes → Slack notifications

- Developer: Pushes code and Helm chart changes to the repository on GitHub.
- GitHub: Hosts repo and triggers the workflow on `workflow_dispatch` (manual run in this repo).
- GitHub Actions: Runs jobs to build the Docker image, push it to DockerHub, render Helm templates for validation, and send Slack notifications.
- Docker: The CI builds a Docker image using the contained `Dockerfile` and tags it with the run number.
- DockerHub: The built image is pushed to DockerHub under the configured repository/user (requires secrets).
- Helm: The CI runs `helm template` against the `k8s/` chart to validate templates (rendering only — does not perform cluster deploy in the current workflow).
- Kubernetes: The chart contains templates for `Deployment`, `Service`, `Ingress`, `ConfigMap`; a cluster would consume the chart via `helm install|upgrade` to deploy.
- Slack: A final job in the workflow posts a message to a Slack webhook with repository, branch, image, and commit information.

Communication:
- GitHub Actions runs on GitHub-hosted runners and uses `docker` binary to build/push images to DockerHub via authenticated HTTP API.
- Helm template is executed locally in the runner environment and only communicates with local files, not with the cluster (validation step).
- Slack notification sends an HTTPS POST to the webhook URL (credential provided via secrets).


## 3. Repository Structure

- [app.py](app.py) — Application source code (Flask + Prometheus metrics simulation).
- [Dockerfile](Dockerfile) — Container build instructions.
- [requirements.txt](requirements.txt) — Python dependencies.
- [get_helm.sh](get_helm.sh) — Helper script for installing Helm (from upstream Helm project).
- [k8s/Chart.yaml](k8s/Chart.yaml) — Helm chart metadata.
- [k8s/values.yaml](k8s/values.yaml) — Helm default values.
- [k8s/templates/](k8s/templates/) — Helm templates:
  - `_helpers.tpl` — template helpers/labels
  - `configmap.yaml` — ConfigMap with DB config and conditional values
  - `deployment.yaml` — Deployment manifest (image/tag/ports)
  - `ingress.yaml` — Ingress manifest (conditional on values)
  - `service.yaml` — Service manifest (port mapping and type)
- [.github/workflows/start.yaml](.github/workflows/start.yaml) — GitHub Actions workflow that builds/pushes the Docker image, templates the Helm chart, and sends Slack notification.
- [.gitignore](.gitignore) — ignored files (venv, pyc, env files, keys).

Purpose of important files/folders:
- Application files: implement the service logic, metrics exposure and simulate workload.
- Dockerfile: builds an image so the app is portable and runnable in containers.
- .github/workflows: defines CI pipeline actions triggered in GitHub.
- Kubernetes/Helm directory: contains chart artifacts used to deploy the app to K8s in a parameterized way.
- values.yaml: exposes configuration knobs (image, tag, ports, replicas, service type, ingress toggles) so changes are applied through Helm values.


## 4. Application Layer

- Language/Framework: Python 3.10 using `Flask`.
- What it does: Exposes two endpoints — `/` shows sample counters and app info; `/metrics` exposes Prometheus metrics.
- Startup: `python app.py` starts the Flask server on `0.0.0.0:5001` when run as `__main__`.
- Dependencies: Listed in `requirements.txt` including `flask` and `prometheus-client` (plus some typing/pydantic libs and `boto3`).
- Ports: The app listens on port `5001` (container `EXPOSE 5001` in the Dockerfile).
- Runtime behavior: A background thread `simulate_traffic()` continuously updates Prometheus Counters, Gauges, Histograms, a custom collector, and an Enum to mimic runtime metrics. The `/metrics` endpoint uses the `prometheus-client` global registry to return metrics in the standard format.


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

Workflow file: [/.github/workflows/start.yaml](.github/workflows/start.yaml)

- Trigger: `workflow_dispatch` — manual workflow trigger (can be started from GitHub UI). You can change to `push` or `pull_request` to automate on commits.

Jobs (order & dependencies):
- `hello` — runs a sample action (hello-world JavaScript action). This is independent and runs first.
- `build` — `needs: hello` (runs after `hello`) and performs: checkout, Docker login, Docker build, Docker push, and `helm template` to render chart templates.
- `slack-notify` — `needs: build` (runs after build) and posts a Slack notification with image/commit info.

Steps explained:
- `actions/checkout@v4` (`uses`): checks out repo code onto the runner so later steps can access files.
- `docker/login-action@v4` (`uses`): performs Docker registry login using provided credentials (securely via secrets).
- `docker build` (`run`): shell command that builds an image from the repo `Dockerfile`.
- `docker push` (`run`): shell command to push the built image to DockerHub.
- `helm template` (`run`): renders Helm templates locally for validation and outputs the Kubernetes YAML to stdout (no cluster interaction).
- Slack job uses `rtCamp/action-slack-notify@v2` (`uses`) which posts to Slack via webhook environment variable.

Difference between `run` and `uses`:
- `uses`: references a pre-built reusable action from GitHub Marketplace or the repo itself. It runs the action's container or JavaScript code and often has built-in behavior and inputs.
- `run`: executes shell commands directly on the runner (for simple custom commands or when no action exists for the task).


## 7. Secrets Management

- This repo expects several GitHub repository secrets to be configured:
  - `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` — for Docker authentication.
  - `SLACK_WEBHOOK` — webhook URL used by the Slack notify action.

- How secrets are used: the `docker/login-action` uses username/token to authenticate; Slack action reads `SLACK_WEBHOOK` from environment to send messages.

- Why secrets are not in the repository: embedding credentials in source control is insecure (exposes tokens to anyone with repo access or in forks). GitHub Secrets provide encrypted storage and inject values only at runtime in Actions.


## 8. Kubernetes & Helm

- Why Helm: Helm provides templating, value-driven configuration, and release management. It lets us parameterize image names/tags, ports, service type, replicas, and easy environment overrides.
- Chart structure: `Chart.yaml` (metadata), `values.yaml` (defaults), and `templates/` (K8s manifest templates). `_helpers.tpl` holds reusable template snippets.
- Templates: Generate `Deployment`, `Service`, `Ingress` (conditional), and `ConfigMap`. They reference `Values` to make behavior configurable.
- Values file: `k8s/values.yaml` includes `pod.image`, `pod.tag`, `port`, `target_port`, `replicas`, `service_type`, and `ingress.enabled`.
- How to deploy: On a system with `kubectl` and `helm` configured against a cluster you could run:

```bash
helm install k8slab ./k8s -f k8s/values.yaml --set pod.image=yuval597/k8slab --set pod.tag=<tag>
# or upgrade
helm upgrade --install k8slab ./k8s -f k8s/values.yaml --set pod.tag=<tag>
```

- `helm template` vs `helm upgrade`:
  - `helm template`: Renders templates locally and prints Kubernetes manifests for inspection/validation — no cluster interaction.
  - `helm upgrade --install`: Applies the chart to a Kubernetes cluster (creates/patches resources) via the Helm client talking to Tiller-less Helm v3 logic using Kubernetes API.


## 9. Monitoring / Notification Flow

- Metrics: The application exports Prometheus metrics through `/metrics`. This is standard Prometheus exposition format, enabling scraping by Prometheus servers or other metric collectors.
- Slack integration: The GitHub Actions workflow sends a Slack message using the `rtCamp/action-slack-notify` action in `slack-notify` job. It runs after the build job completes and posts a message containing the repository, branch, image tag, and commit SHA.
- When notifications are sent: After the CI build/push passes (the `slack-notify` job is a downstream job that runs when `build` completes). You can extend this to send on failures using conditional steps or a separate job.


## 10. DevOps Concepts Demonstrated

- Git: Source control and change-driven automation.
- CI/CD: GitHub Actions pipeline to build/test/package artifacts.
- Docker: Containerizing the app for reproducible deployment.
- Container registries: Image tagging and pushing to DockerHub.
- Kubernetes: Manifests and deployment primitives.
- Helm: Templating, values-driven configuration, chart packaging.
- Automation: Fully scripted pipeline for building/publishing artifacts and sending notifications.
- Secrets management: Use of GitHub Secrets for credentials and webhooks.
- GitOps readiness: Chart and image artifacts are present and can be consumed by GitOps tools (ArgoCD/Flux) for continuous deployment.


## 11. Future Improvements

- Add `helm upgrade --install` step to the pipeline to automate cluster deployment (with proper environment protections).
- Add ArgoCD or Flux for GitOps continuous delivery and environment promotion flows.
- Add unit tests and CI test steps (pytest) to prevent regressions.
- Add container image scanning (Trivy) and CI security checks.
- Add multi-environment values and promotion strategy (dev/stage/prod) using separate `values-*.yaml`.
- Add health checks and readiness/liveness probes in the Deployment manifest.
- Add resource requests/limits and HPA for resilience.
- Add logging/observability exporters (structured logs, tracing, Prometheus scrape config in chart).


## 12. Interview Explanation (Short Pitch)

I built a small sample DevOps pipeline that shows how to go from code to a deployable container image and Helm chart. The app is a Flask microservice instrumented with Prometheus metrics. CI is implemented via GitHub Actions: it checks out the code, builds a Docker image, pushes it to DockerHub, and validates Helm templates. A Slack job posts the build information.

Technologies covered: Git, GitHub Actions, Docker, DockerHub, Helm, Kubernetes manifests, Prometheus metrics, and Slack notifications. The repo is designed to be extended to full GitOps (ArgoCD) or environment-specific deployments.


---

Files added:
- README.md (this file)
- PRESENTATION.md — interview-ready speaking notes (also added to repo)

If you want, I can:
- Create a `helm upgrade --install` step and add environment protection
- Add a basic `health` endpoint and readiness probe to the `Deployment` template
- Add a GitHub Actions `push` trigger to automate builds on every commit

