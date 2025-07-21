# Week 04: Full-Stack Microservice Deployment with Kubernetes

This example extends previous weeks' concepts by demonstrating the deployment of a multi-service application (frontend and three backend microservices) onto a local Kubernetes cluster, typically running via Podman Desktop. This setup provides hands-on experience with container orchestration, configuration management, and service discovery within a Kubernetes environment.

## Update ConfigMap (`configmap.yaml`)
- Replace `AZURE_STORAGE_CONTAINER_NAME` value to your actual container name.

## Update Secrets (`secrets.yaml`)

This file contains non-sensitive configuration data, such as database names or API endpoints.

- Replace `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` to your actual values.

    **NOTE Make sure to convert both values to Base64 before you add in `secrets.yaml`. Command is given in comment about how to convert to base64.**

## Update Service k8s files (`frontend.yaml`, `product-service.yaml`, `order-service.yaml` and `customer-service.yaml`)

- Replace image name to your actual image for all services.