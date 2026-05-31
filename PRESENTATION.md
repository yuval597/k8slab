Presentation / Interview Notes: k8slab

Elevator pitch

End-to-end DevOps CI pipeline for a containerized Python application. The repository demonstrates a real-world DevOps CI workflow that builds container images, pushes them to DockerHub, validates Helm charts in CI, and reports pipeline results to Slack. The pipeline was originally implemented using Jenkins Pipeline and later migrated/recreated using GitHub Actions to demonstrate familiarity with both CI platforms.

Architecture (one-liner)

Developer → GitHub Repository → GitHub Actions CI Pipeline → Checkout → Docker login → Docker build → Docker push to DockerHub → Helm template validation → Slack notification

Key components and what I did

- Application: `app.py` — Flask app that serves an index page and runs a simulated workload.
- Containerization: `Dockerfile` builds a Python 3.10 image, installs `requirements.txt`, exposes port 5001, and runs `app.py`.
- Helm: Chart in `k8s/` provides parameterized `Deployment`, `Service`, `Ingress`, and `ConfigMap` templates prepared for Kubernetes deployment.
- CI: GitHub Actions workflow (`.github/workflows/start.yaml`) performs checkout, Docker login, build, push, `helm template` for validation, and Slack notify.

Why this is useful in a real environment

- Reproducible builds: Dockerfile + CI produce consistent images tagged by build number.
- Configuration-as-code: Helm chart enables parameterized deployments across environments.
- Secure automation: DockerHub credentials and Slack webhooks are stored using GitHub Actions Secrets.
- Notification / feedback loop: Slack integration provides immediate visibility into CI runs.

Notes on CI platform migration

This project was originally implemented with a Jenkins Pipeline (stages, scripted/Declarative syntax) and later migrated to GitHub Actions. The transition demonstrates understanding of:
- Jenkins stages and pipeline structure (checkout, build, publish, and deployment-related stages).
- GitHub Actions jobs and steps (needs dependencies, reusable Marketplace actions).
- Trade-offs between CI platforms and practical migration steps.

Interview talking points / challenges

- The workflow uses `helm template` in CI to validate rendering but does not deploy to Kubernetes; deployment is a separate step.
- Image tagging uses the workflow run number; for production you'd prefer semantic tags or commit SHAs and a promotion strategy.
- Sensitive values such as DockerHub tokens and Slack webhooks are managed through GitHub Secrets and are not stored in the repository.

Possible follow-ups to mention

- Add unit and integration tests and run them in CI.
- Add image scanning (Trivy) to the pipeline.
- Add a gated `helm upgrade --install` deployment step or use ArgoCD for GitOps-driven CD.
- Add health/readiness probes and resource requests/limits to the Helm chart.

Short script to demo in an interview

1. Show repository tree and key files (`app.py`, `Dockerfile`, `k8s/`, `.github/workflows/start.yaml`).
2. Explain the `Dockerfile` and how the image is built in CI.
3. Walk through the workflow jobs and emphasize `actions/checkout`, Docker login, build/push, `helm template` validation, and Slack notify.
4. Show `k8s/templates` and `values.yaml` to explain how configuration is parameterized.
5. Summarize next steps (CD via ArgoCD or `helm upgrade --install`).

One-minute summary

"I built an end-to-end CI pipeline around a Python application. The application is containerized using Docker, automatically built through GitHub Actions, pushed to DockerHub, validated using Helm charts, and integrated with Slack notifications. I also implemented the pipeline using Jenkins previously to understand different CI/CD approaches. The project currently focuses on CI validation and is prepared for future Kubernetes deployment using Helm or ArgoCD."
