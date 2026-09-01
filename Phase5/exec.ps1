Start-Process powershell -ArgumentList "kubectl port-forward svc/mongodb 27017:27017 -n smart-parking"
Start-Process powershell -ArgumentList "kubectl port-forward svc/redis 6379:6379 -n smart-parking"
Start-Process powershell -ArgumentList "kubectl port-forward svc/rabbitmq 5673:5672 15672:15672 -n smart-parking"
#kubectl port-forward svc/rabbitmq 5672:5672 -n smart-parking