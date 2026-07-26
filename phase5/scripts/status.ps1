Write-Host ""
Write-Host "Pods"
kubectl get pods -n smart-parking

Write-Host ""
Write-Host "Services"
kubectl get svc -n smart-parking

Write-Host ""
Write-Host "Deployments"
kubectl get deployments -n smart-parking

Write-Host ""
Write-Host "ReplicaSets"
kubectl get replicasets -n smart-parking

Write-Host ""
Write-Host "Nodes"
kubectl get nodes