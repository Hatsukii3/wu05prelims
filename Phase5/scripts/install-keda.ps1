Write-Host "Installing KEDA..." -ForegroundColor Cyan

helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace

Write-Host "Checking KEDA deployment status..." -ForegroundColor Green
kubectl get pods -n keda