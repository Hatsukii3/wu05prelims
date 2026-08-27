Write-Host "=== Smart Parking System Status ===" -ForegroundColor Cyan

Write-Host "`n[Pods & Deployments]" -ForegroundColor Yellow
kubectl get all -n smart-parking

Write-Host "`n[KEDA ScaledObjects]" -ForegroundColor Yellow
kubectl get scaledobject -n smart-parking

Write-Host "`n[Persistent Volume Claims]" -ForegroundColor Yellow
kubectl get pvc -n smart-parking