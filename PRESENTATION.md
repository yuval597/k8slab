Presentation / Interview Notes: k8slab

Elevator pitch

I built a small sample DevOps pipeline that demonstrates how to package, validate, and publish a containerized Python application and prepare it for Kubernetes deployment via Helm. The pipeline uses GitHub Actions to build and push images to DockerHub, uses Helm for templated manifests, and sends Slack notifications for pipeline results. The app is instrumented with Prometheus metrics so it can be monitored when running in a cluster.

Architecture (one-liner)
Developer -> GitHub -> GitHub Actions -> Docker build -> DockerHub push -> Helm template -> (optionally Helm install) -> Kubernetes cluster -> Slack notifications

Key components and what I did

- Application: `app.py` — Flask app that simulates traffic and exposes Prometheus metrics at `/metrics`.
- Containerization: `Dockerfile` builds a Python 3.10 image, installs `requirements.txt`, exposes port 5001, and runs `app.py`.
- Helm: Chart in `k8s/` provides parameterized `Deployment`, `Service`, `Ingress`, and `ConfigMap` to deploy the app consistently across environments.
- CI: GitHub Actions workflow (`.github/workflows/start.yaml`) demonstrates a multi-job flow: checkout, Docker login, build, push, helm template, and Slack notify.

Why this is useful in a real environment

- Reproducible builds: Dockerfile + CI produce deterministic images tagged by build number.
- Configuration-as-code: Helm chart allows parameterized deployments across environments.
- Observability readiness: Prometheus metrics endpoint exposes runtime metrics for monitoring.
- Notification / feedback loop: Slack integration provides immediate visibility into CI runs.

Challenges and decisions

- The workflow uses `helm template` for validation rather than deploying directly; this is appropriate for CI validation but requires a separate deploy mechanism (ArgoCD/Helm in CD job) for actual cluster rollout.
- Image tagging is simple (run number); for production you'd want semantic tags or commit SHA pins and a clear promotion strategy.

Possible follow-ups I would implement in a real job interview project

- Add unit tests + integration tests and run them in CI.
- Add image scanning (Trivy) to the pipeline to detect vulnerabilities early.
- Automate Helm deployments with `helm upgrade --install` behind a gated approval step, or adopt ArgoCD for GitOps.
- Add health/readiness probes, resource requests/limits, and HPA to the chart.

Short script to show during an interview

1. Show repository tree and key files.
2. Open `app.py` and explain the metrics and background simulation.
3. Show `Dockerfile` — explain how container is built.
4. Show the workflow file — explain each job and the secrets usage.
5. Show `k8s/templates` — explain templating and how `values.yaml` controls deployment.

One-minute summary to close

This project demonstrates the core DevOps lifecycle for a microservice: developers push code, CI builds and publishes images, Helm templates allow consistent deployments, and notification channels provide feedback. It's intentionally compact so the pipeline pieces are visible and can be extended to full GitOps with ArgoCD or automated deployments with Helm in CD jobs.

