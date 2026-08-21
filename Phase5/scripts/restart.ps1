Write-Host "Restarting Deployment..."

kubectl rollout restart deployment inference -n smart-parking

kubectl rollout status deployment inference -n smart-parking