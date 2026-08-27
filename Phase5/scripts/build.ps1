Write-Host "Building Docker image..."

docker build -t inference-program "$PSScriptRoot/../docker"

docker images