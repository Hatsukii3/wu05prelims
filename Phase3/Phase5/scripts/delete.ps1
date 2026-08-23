Write-Host "Deleting Smart Parking deployment..."

kubectl delete -f ../kubernetes/scaledobject.yaml --ignore-not-found

kubectl delete -f ../kubernetes/deployment.yaml --ignore-not-found

kubectl delete -f ../kubernetes/mongodb-service.yaml --ignore-not-found
kubectl delete -f ../kubernetes/mongodb.yaml --ignore-not-found

kubectl delete -f ../kubernetes/redis-service.yaml --ignore-not-found
kubectl delete -f ../kubernetes/redis.yaml --ignore-not-found

kubectl delete -f ../kubernetes/rabbitmq-service.yaml --ignore-not-found
kubectl delete -f ../kubernetes/rabbitmq.yaml --ignore-not-found

kubectl delete -f ../kubernetes/namespace.yaml --ignore-not-found