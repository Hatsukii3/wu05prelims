Write-Host "Deploying Smart Parking System..."

kubectl apply -f ../kubernetes/namespace.yaml

kubectl apply -f ../kubernetes/rabbitmq.yaml
kubectl apply -f ../kubernetes/rabbitmq-service.yaml

kubectl apply -f ../kubernetes/redis.yaml
kubectl apply -f ../kubernetes/redis-service.yaml

kubectl apply -f ../kubernetes/mongodb.yaml
kubectl apply -f ../kubernetes/mongodb-service.yaml

kubectl apply -f ../kubernetes/deployment.yaml

kubectl apply -f ../kubernetes/scaledobject.yaml

kubectl get all -n smart-parking