# PowerShell script to push to GitHub
Write-Host "Pushing Cloud Resource Optimizer to GitHub..." -ForegroundColor Cyan
Write-Host ""

# Configure Git user
Write-Host "Configuring Git user..." -ForegroundColor Yellow
git config user.name "programmeramesh"
git config user.email "your-email@example.com"  # UPDATE THIS!

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Initial commit: AI-Based Cloud Resource Optimizer with modern UI"

# Set main branch
Write-Host "Setting main branch..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for credentials:" -ForegroundColor Green
Write-Host "  Username: programmeramesh" -ForegroundColor Green
Write-Host "  Password: Use your GitHub Personal Access Token" -ForegroundColor Green
Write-Host ""

git push -u origin main

Write-Host ""
Write-Host "Done! Check your repository at:" -ForegroundColor Green
Write-Host "https://github.com/programmeramesh/Cloudproject" -ForegroundColor Cyan
