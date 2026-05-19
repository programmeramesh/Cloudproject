# Push latest updates to GitHub
Write-Host "Pushing latest updates to GitHub..." -ForegroundColor Cyan

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Fix: Resolved monitoring errors, added favicon, improved error handling for predictions and recommendations"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push

Write-Host ""
Write-Host "✅ Updates pushed successfully!" -ForegroundColor Green
Write-Host "View at: https://github.com/programmeramesh/Cloudproject" -ForegroundColor Cyan
