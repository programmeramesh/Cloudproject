# Generate sample data for testing
Write-Host "Generating sample workload data..." -ForegroundColor Cyan

cd backend
.\venv\Scripts\activate

Write-Host "Creating 100 sample metrics..." -ForegroundColor Yellow
python scripts/generate_sample_data.py --records 100 --to-db

Write-Host ""
Write-Host "✅ Sample data generated!" -ForegroundColor Green
Write-Host "You can now use the Predictions feature in the dashboard." -ForegroundColor Cyan
