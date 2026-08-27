Write-Host "Restarting Smart Parking deployments..." -ForegroundColor Yellow

kubectl rollout restart deployment -n smart-parking

Write-Host "Deployments restarted. Fetching pod status..." -ForegroundColor Green
kubectl get pods -n smart-parking -w