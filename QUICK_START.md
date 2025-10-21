# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ MongoDB installed and running

## Step 1: Start MongoDB

### Option A: Windows Service (Requires Admin)
```powershell
# Run PowerShell as Administrator
net start MongoDB
```

### Option B: Manual Start
```powershell
# Create data directory if it doesn't exist
mkdir C:\data\db

# Start MongoDB manually
mongod --dbpath C:\data\db
```

### Verify MongoDB is Running
```powershell
mongosh
# You should see MongoDB shell prompt
```

## Step 2: Start Backend Server

### Option A: Using Batch File
```powershell
.\start-backend.bat
```

### Option B: Manual Start
```powershell
cd backend
.\venv\Scripts\activate
python app.py
```

The backend will start on **http://localhost:5000**

## Step 3: Start Frontend Dashboard

### Option A: Using Batch File (New Terminal)
```powershell
.\start-frontend.bat
```

### Option B: Manual Start
```powershell
cd frontend
npm start
```

The frontend will open automatically at **http://localhost:3000**

## Step 4: Login

Navigate to http://localhost:3000 and login with:
- **Username**: `admin`
- **Password**: `admin123`

## Troubleshooting

### MongoDB Connection Error
```
Error: MongoServerError: connect ECONNREFUSED
```
**Solution**: Make sure MongoDB is running (see Step 1)

### Port Already in Use
```
Error: Port 5000 is already in use
```
**Solution**: 
```powershell
# Find and kill the process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Reinstall dependencies
```powershell
cd backend
.\venv\Scripts\pip install -r requirements.txt
```

### Frontend Build Errors
```
Error: Cannot find module 'react'
```
**Solution**: Reinstall node modules
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Verify Everything is Running

1. **Backend API**: http://localhost:5000/api/health
   - Should return: `{"status": "healthy"}`

2. **Frontend**: http://localhost:3000
   - Should show login page

3. **MongoDB**: 
   ```powershell
   mongosh
   show dbs
   ```

## Next Steps

1. **Generate Sample Data** (Optional):
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python scripts/generate_sample_data.py --records 500 --to-db
   ```

2. **Train ML Model** (Optional):
   ```powershell
   python scripts/train_model.py --from-db --epochs 50
   ```

3. **Explore the Dashboard**:
   - View real-time metrics
   - Generate predictions
   - Manage resources

## Stopping the Servers

- **Backend**: Press `Ctrl+C` in the backend terminal
- **Frontend**: Press `Ctrl+C` in the frontend terminal
- **MongoDB**: 
  ```powershell
  # If running as service
  net stop MongoDB
  
  # If running manually
  # Press Ctrl+C in MongoDB terminal
  ```

## Quick Commands Reference

```powershell
# Check if ports are in use
netstat -ano | findstr :5000  # Backend
netstat -ano | findstr :3000  # Frontend
netstat -ano | findstr :27017 # MongoDB

# Check Python version
python --version

# Check Node version
node --version

# Check MongoDB version
mongod --version
```

## Need Help?

- Check logs in `backend/logs/app.log`
- Review the full [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
