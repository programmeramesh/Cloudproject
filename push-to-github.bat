@echo off
echo Pushing Cloud Resource Optimizer to GitHub...
echo.

REM Configure Git user (update with your details)
git config user.name "programmeramesh"
git config user.email "your-email@example.com"

REM Check Git status
echo Checking Git status...
git status

REM Commit changes
echo.
echo Committing changes...
git commit -m "Initial commit: AI-Based Cloud Resource Optimizer with modern UI"

REM Push to GitHub
echo.
echo Pushing to GitHub repository...
git branch -M main
git push -u origin main

echo.
echo Done! Check https://github.com/programmeramesh/Cloudproject
pause
