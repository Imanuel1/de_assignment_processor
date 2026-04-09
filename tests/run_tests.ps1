Write-Host "Setting up test environment (Success Rate = 0)..." -ForegroundColor Cyan
$env:WEBHOOK_SUCCESS_RATE=0
$env:RABBITMQ_CONSTANT_DELAY=1
docker-compose up -d --force-recreate processor_service

Start-Sleep -Seconds 2

Write-Host "Running API Tests..." -ForegroundColor Yellow
docker-compose exec api_service pytest tests/

Write-Host "Cleaning up: Resetting environment to default..." -ForegroundColor Cyan
docker-compose up -d --force-recreate processor_service

exit