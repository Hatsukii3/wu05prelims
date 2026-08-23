Write-Host "Installing KEDA..."

kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.17.2/keda-2.17.2.yaml

kubectl get pods -n keda