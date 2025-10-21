# Complete the push after resolving conflicts
Write-Host "Completing GitHub push..." -ForegroundColor Cyan

# Commit the merge
git commit -m "Merge remote changes"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "View your project at: https://github.com/programmeramesh/Cloudproject" -ForegroundColor Cyan
