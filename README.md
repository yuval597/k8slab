## Project Overview

k8slab is a project built as part of my DevOps studies to practice a complete CI/CD and GitOps workflow.

The project uses GitHub Actions, Docker, Helm and ArgoCD to build, package and deploy a Flask application to Kubernetes across multiple environments (DEV, QA and PROD). The pipeline also sends deployment notifications to Slack after each successful deployment.


## Technologies

- Python / Flask
- Docker & DockerHub
- Helm
- Kubernetes
- GitHub Actions
- ArgoCD
- GitOps
- Slack Notifications


## Repository Structure

```text
k8slab
├── .github
│   └── workflows
│       └── cicd.yaml
├── chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       └── configmap.yaml
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md
```

.github/workflows contains the CI/CD pipeline.

chart directory contains the Helmchart used to generate Kubernetes manifests.

app.py is the Flask application.

Dockerfile is used to build the container image.


## Architecture

The process starts when I manually trigger the GitHub Actions workflow.

The pipeline checks out the source code, builds a Docker image and pushes it to DockerHub.

Next, Helm generates Kubernetes manifests using the latest image tag and stores them in a separate GitOps repository under the relevant environment directory (DEV, QA or PROD).

ArgoCD continuously monitors the GitOps repository for changes. When a new manifest is pushed, ArgoCD automatically synchronizes the target Kubernetes namespace with the desired state.

Finally, the pipeline sends a Slack notification indicating that the deployment process completed successfully.


## Git repos for exam:

GitOps repo: https://github.com/yuval597/GitOps

Terraform repo: https://github.com/yuval597/tfexam
