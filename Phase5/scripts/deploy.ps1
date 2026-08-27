Write-Host "Deploying Smart Parking System..."

kubectl apply -f "$PSScriptRoot/../kubernetes/namespace.yaml"

kubectl apply -f "$PSScriptRoot/../kubernetes/rabbitmq.yaml"
kubectl apply -f "$PSScriptRoot/../kubernetes/rabbitmq-service.yaml"

kubectl apply -f "$PSScriptRoot/../kubernetes/redis.yaml"
kubectl apply -f "$PSScriptRoot/../kubernetes/redis-service.yaml"

kubectl apply -f "$PSScriptRoot/../kubernetes/mongodb.yaml"
kubectl apply -f "$PSScriptRoot/../kubernetes/mongodb-service.yaml"

kubectl apply -f "$PSScriptRoot/../kubernetes/init.yaml"

kubectl apply -f "$PSScriptRoot/../kubernetes/deployment.yaml"
kubectl apply -f "$PSScriptRoot/../kubernetes/scaledobject.yaml"

kubectl get all -n smart-parking