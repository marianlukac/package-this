# Reset all data tables and re-run seed script
Write-Host "Resetting Dunder Mifflin Package Manager seed data..."

$response = Invoke-RestMethod -Uri "http://localhost:8000/demo/reset" `
    -Method POST `
    -Headers @{ "X-Persona-Id" = "michael-scott"; "Content-Type" = "application/json" }

$response | ConvertTo-Json
Write-Host ""
Write-Host "Seed data reset complete."
