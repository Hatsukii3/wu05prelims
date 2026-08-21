Write-Host "Building Docker image..."

docker build -t inference-program ../docker

docker images