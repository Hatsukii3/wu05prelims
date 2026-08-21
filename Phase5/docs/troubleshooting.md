# Common Errors

## kubectl not found

Install Kubernetes CLI and ensure it is added to PATH.

## Docker daemon not running

Open Docker Desktop and wait until the engine is running.

## RabbitMQ Connection Error

Verify that RabbitMQ is deployed.

kubectl get pods

## Redis Connection Error

Verify that the Redis pod is running.

## MongoDB Connection Error

Verify that MongoDB is deployed.

## ImagePullBackOff

Rebuild the Docker image and restart the deployment.

docker build -t inference-program .

kubectl rollout restart deployment inference -n smart-parking