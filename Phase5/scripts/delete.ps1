Write-Host "Deleting Smart Parking resources from Kubernetes..." -ForegroundColor Yellow

kubectl delete -f "$PSScriptRoot/../kubernetes/scaledobject.yaml" --ignore-not-found
kubectl delete -f "$PSScriptRoot/../kubernetes/deployment.yaml" --ignore-not-found
kubectl delete -f "$PSScriptRoot/../kubernetes/init.yaml" --ignore-not-found

kubectl delete -f "$PSScriptRoot/../kubernetes/mongodb-service.yaml" --ignore-not-found
kubectl delete -f "$PSScriptRoot/../kubernetes/mongodb.yaml" --ignore-not-found

kubectl delete -f "$PSScriptRoot/../kubernetes/redis-service.yaml" --ignore-not-found
kubectl delete -f "$PSScriptRoot/../kubernetes/redis.yaml" --ignore-not-found

kubectl delete -f "$PSScriptRoot/../kubernetes/rabbitmq-service.yaml" --ignore-not-found
kubectl delete -f "$PSScriptRoot/../kubernetes/rabbitmq.yaml" --ignore-not-found

kubectl delete -f "$PSScriptRoot/../kubernetes/namespace.yaml" --ignore-not-found

Write-Host "Cleanup complete." -ForegroundColor Green