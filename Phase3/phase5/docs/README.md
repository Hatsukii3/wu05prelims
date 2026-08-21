# Smart Parking System - Phase 5

This folder contains the documentation for the Kubernetes implementation of the Smart Parking System.

## Technologies Used

- Docker
- Kubernetes
- RabbitMQ
- Redis
- MongoDB
- KEDA
- YOLOv11
- Python

## Folder Structure

docker/
Contains the inference program and Docker image.

kubernetes/
Contains all Kubernetes deployment files.

scripts/
Contains PowerShell scripts for building, deploying, and monitoring the cluster.

docs/
Contains documentation, screenshots, and notes.

## Workflow

1. Build Docker Image
2. Deploy Kubernetes Resources
3. Install KEDA
4. Test Autoscaling
5. Evaluate Performance