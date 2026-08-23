Write-Host "Rebuilding Docker Image..."

docker build -t inference-program ../docker

kubectl rollout restart deployment inference -n smart-parking

kubectl rollout status deployment inference -n smart-parking