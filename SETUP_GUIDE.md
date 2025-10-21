# Setup Guide - Cloud Resource Optimizer

This guide will help you set up and run the AI-Based Cloud Resource Allocation system.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **MongoDB 4.4+** - [Download](https://www.mongodb.com/try/download/community)
- **Git** - [Download](https://git-scm.com/downloads)
- **Docker** (Optional) - [Download](https://www.docker.com/products/docker-desktop)

## Quick Start with Docker

The easiest way to run the entire stack:

```bash
# Clone the repository
git clone <repository-url>
cd cloud-resource-optimizer

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27017

## Manual Setup

### 1. Database Setup

#### Install and Start MongoDB

**Windows:**
```powershell
# Download MongoDB Community Server
# Install and start MongoDB service
net start MongoDB
```

**Linux/Mac:**
```bash
# Install MongoDB
sudo apt-get install mongodb  # Ubuntu/Debian
brew install mongodb-community  # macOS

# Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

#### Verify MongoDB is Running

```bash
mongo --eval "db.version()"
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Edit .env with your configuration
# Set MONGODB_URI, cloud credentials, etc.

# Create necessary directories
mkdir -p logs models/saved_models

# Generate sample data (optional)
python scripts/generate_sample_data.py --records 500 --to-db

# Train the ML model (optional, requires sample data)
python scripts/train_model.py --from-db --epochs 50

# Run the backend server
python app.py
```

The backend API will be available at http://localhost:5000

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Start development server
npm start
```

The frontend will open automatically at http://localhost:3000

## Configuration

### Environment Variables

Edit the `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
MONGODB_URI=mongodb://localhost:27017/cloud_optimizer

# AWS Configuration (if using AWS)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Azure Configuration (if using Azure)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# GCP Configuration (if using GCP)
GCP_PROJECT_ID=your-project-id
GCP_CREDENTIALS_PATH=/path/to/credentials.json

# ML Model Configuration
LSTM_SEQUENCE_LENGTH=24
LSTM_EPOCHS=50
LSTM_BATCH_SIZE=32

# Resource Thresholds
CPU_THRESHOLD_HIGH=80.0
CPU_THRESHOLD_LOW=30.0
MEMORY_THRESHOLD_HIGH=85.0
MEMORY_THRESHOLD_LOW=35.0
```

### Cloud Provider Setup

#### AWS Setup

1. Create IAM user with EC2 permissions
2. Generate access keys
3. Add credentials to `.env` file
4. Update `backend/services/cloud_provider.py` with your AMI ID

#### Azure Setup

1. Create Azure AD application
2. Grant permissions to manage VMs
3. Add credentials to `.env` file

#### GCP Setup

1. Create service account
2. Download JSON credentials
3. Add project ID and credentials path to `.env`

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

### API Testing

Use the provided API endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get current metrics
curl http://localhost:5000/api/metrics/current
```

## Usage

### 1. Login

- Navigate to http://localhost:3000
- Use credentials: `admin` / `admin123`

### 2. View Dashboard

- Monitor real-time resource usage
- View cost trends
- Check optimization score

### 3. Generate Predictions

- Go to Predictions page
- Click "Generate Predictions"
- View AI-powered workload forecasts

### 4. Manage Resources

- Go to Resources page
- View current allocation
- Review AI recommendations
- Apply resource changes

## Training the Model

### Using Sample Data

```bash
# Generate sample data
cd backend
python scripts/generate_sample_data.py --records 1000 --to-db

# Train model
python scripts/train_model.py --from-db --epochs 50
```

### Using Your Own Data

```bash
# Prepare CSV with columns: timestamp, cpu_usage, memory_usage, network_usage, disk_io
python scripts/train_model.py --data your_data.csv --epochs 50
```

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
mongosh --eval "db.version()"

# Check connection string in .env
MONGODB_URI=mongodb://localhost:27017/cloud_optimizer
```

### Port Already in Use

```bash
# Backend (5000)
# Windows:
netstat -ano | findstr :5000
# Linux/Mac:
lsof -i :5000

# Frontend (3000)
# Change port in package.json or use:
PORT=3001 npm start
```

### Module Not Found Errors

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

Ensure `CORS(app)` is enabled in `backend/app.py` and the API URL is correct in frontend `.env`

## Production Deployment

### Using Docker

```bash
# Build and start services
docker-compose -f docker-compose.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Manual Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Build frontend for production:
   ```bash
   cd frontend
   npm run build
   ```
4. Serve frontend with nginx or Apache
5. Use a process manager (PM2, systemd)
6. Set up SSL certificates
7. Configure firewall rules

## Monitoring

### Application Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
```

### Database Monitoring

```bash
# Connect to MongoDB
mongosh cloud_optimizer

# Check collections
show collections

# View metrics
db.metrics.find().limit(5)
```

## Support

For issues and questions:
- Check the [README.md](README.md)
- Review logs in `backend/logs/`
- Open an issue on GitHub

## Next Steps

1. Configure cloud provider credentials
2. Generate or import historical data
3. Train the prediction model
4. Set up monitoring and alerts
5. Configure auto-scaling policies
6. Implement backup strategies
