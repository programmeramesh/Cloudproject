# System Architecture

## Overview

The Cloud Resource Optimizer is a full-stack application that uses AI/ML to predict workload patterns and automatically allocate cloud resources for optimal performance and cost efficiency.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (React Dashboard - Port 3000)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Server                         │
│                     (Flask - Port 5000)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Routes     │  │  Services    │  │   Models     │        │
│  │  - Metrics   │  │ - Monitoring │  │ - Prediction │        │
│  │  - Predict   │  │ - Optimizer  │  │ - Allocator  │        │
│  │  - Resources │  │ - Cloud API  │  │ - Database   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│   MongoDB Database        │  │   Cloud Provider API     │
│   (Port 27017)           │  │   (AWS/Azure/GCP)        │
│  - Metrics Collection    │  │  - EC2/VM Management     │
│  - Predictions           │  │  - Auto Scaling          │
│  - Allocations           │  │  - Cost Monitoring       │
│  - Cost Data             │  │                          │
└───────────────────────────┘  └──────────────────────────┘
```

## Components

### 1. Frontend (React)
- **Dashboard**: Real-time metrics visualization
- **Metrics Page**: Historical data and charts
- **Predictions Page**: AI forecasts and model training
- **Resources Page**: Allocation management

### 2. Backend (Flask)
- **API Layer**: RESTful endpoints
- **Business Logic**: Resource allocation algorithms
- **ML Engine**: LSTM prediction model
- **Monitoring**: System metrics collection

### 3. Database (MongoDB)
- **Collections**: metrics, predictions, allocations, costs
- **Indexes**: Optimized for time-series queries

### 4. Cloud Integration
- **AWS**: EC2 instance management
- **Azure**: VM management
- **GCP**: Compute Engine management

## Data Flow

1. **Monitoring** → Collect metrics → Store in DB
2. **Prediction** → Analyze historical data → Generate forecasts
3. **Optimization** → Calculate recommendations → Estimate costs
4. **Allocation** → Execute scaling → Update resources
5. **Visualization** → Fetch data → Display on dashboard
