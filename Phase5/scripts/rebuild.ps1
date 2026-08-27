Write-Host "Rebuilding Docker image and re-deploying..." -ForegroundColor Cyan

& "$PSScriptRoot/build.ps1"

Write-Host "Rolling restart of the deployment..." -ForegroundColor Yellow
kubectl rollout restart deployment/smart-parking -n smart-parking

Write-Host "Rebuild process finished." -ForegroundColor Green