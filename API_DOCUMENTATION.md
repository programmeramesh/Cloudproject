# API Documentation

Base URL: `http://localhost:5000/api`

## Authentication

### Login

**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "admin"
}
```

## Metrics Endpoints

### Get Metrics

**GET** `/metrics`

Retrieve historical metrics.

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 100)
- `resource_id` (optional): Filter by resource ID

**Response:**
```json
{
  "success": true,
  "count": 100,
  "metrics": [
    {
      "_id": "...",
      "timestamp": "2024-10-21T10:30:00Z",
      "cpu_usage": 65.5,
      "memory_usage": 72.3,
      "network_usage": 45.2,
      "disk_io": 38.7,
      "resource_id": "instance-1"
    }
  ]
}
```

### Get Current Metrics

**GET** `/metrics/current`

Get current system metrics.

**Response:**
```json
{
  "success": true,
  "metrics": {
    "timestamp": "2024-10-21T10:30:00Z",
    "cpu_usage": 65.5,
    "memory_usage": 72.3,
    "network_usage": 45.2,
    "disk_io": 38.7,
    "cpu_count": 4,
    "memory_total_gb": 16.0
  }
}
```

### Submit Metrics

**POST** `/metrics`

Submit new metrics data.

**Request Body:**
```json
{
  "cpu_usage": 65.5,
  "memory_usage": 72.3,
  "network_usage": 45.2,
  "disk_io": 38.7,
  "resource_id": "instance-1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Metrics submitted successfully",
  "id": "..."
}
```

### Get Aggregated Metrics

**GET** `/metrics/aggregated`

Get aggregated metrics by time interval.

**Query Parameters:**
- `interval`: "hour" or "day" (default: "hour")

**Response:**
```json
{
  "success": true,
  "interval": "hour",
  "data": [
    {
      "_id": "2024-10-21-10",
      "avg_cpu": 65.5,
      "avg_memory": 72.3,
      "max_cpu": 85.2,
      "max_memory": 88.1
    }
  ]
}
```

## Predictions Endpoints

### Get Predictions

**GET** `/predictions`

Retrieve prediction history.

**Query Parameters:**
- `limit` (optional): Number of records (default: 50)

**Response:**
```json
{
  "success": true,
  "count": 10,
  "predictions": [
    {
      "_id": "...",
      "timestamp": "2024-10-21T10:30:00Z",
      "predictions": [65.5, 68.2, 70.1, ...],
      "steps": 12,
      "model_type": "LSTM"
    }
  ]
}
```

### Generate Predictions

**POST** `/predictions/generate`

Generate new workload predictions.

**Query Parameters:**
- `steps` (optional): Number of hours to predict (default: 12)

**Response:**
```json
{
  "success": true,
  "predictions": [65.5, 68.2, 70.1, 72.5, ...],
  "steps": 12
}
```

### Train Model

**POST** `/predictions/train`

Train the LSTM prediction model.

**Request Body (optional):**
```json
{
  "epochs": 50,
  "batch_size": 32
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model trained successfully",
  "epochs": 50,
  "final_loss": 0.0234
}
```

## Resource Endpoints

### Get Resources

**GET** `/resources`

Get current resource allocation.

**Response:**
```json
{
  "success": true,
  "allocation": {
    "instance_count": 2,
    "instance_type": "t2.small",
    "instances": [
      {
        "instance_id": "i-1234567890",
        "instance_type": "t2.small",
        "state": "running",
        "launch_time": "2024-10-21T08:00:00Z"
      }
    ]
  }
}
```

### Get Recommendations

**GET** `/resources/recommendations`

Get AI-powered resource allocation recommendations.

**Response:**
```json
{
  "success": true,
  "recommendation": {
    "timestamp": "2024-10-21T10:30:00Z",
    "action": "scale_up",
    "current_instances": 2,
    "recommended_instances": 3,
    "current_instance_type": "t2.small",
    "recommended_instance_type": "t2.small",
    "reason": "High resource usage predicted: CPU=85.5%, Memory=82.3%",
    "predicted_cpu": 85.5,
    "predicted_memory": 82.3,
    "estimated_cost": {
      "hourly": 0.069,
      "daily": 1.66,
      "monthly": 49.68
    }
  }
}
```

### Allocate Resources

**POST** `/resources/allocate`

Execute resource allocation based on recommendation.

**Request Body (optional):**
```json
{
  "recommendation": {
    "action": "scale_up",
    "recommended_instances": 3,
    "recommended_instance_type": "t2.small"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "success": true,
    "message": "Launched 1 new instances",
    "action": "scale_up",
    "new_instances": ["i-0987654321"]
  }
}
```

## Dashboard Endpoints

### Get Dashboard Stats

**GET** `/dashboard/stats`

Get comprehensive dashboard statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "current_metrics": {
      "cpu_usage": 65.5,
      "memory_usage": 72.3,
      "timestamp": "2024-10-21T10:30:00Z"
    },
    "current_allocation": {
      "instance_count": 2,
      "instance_type": "t2.small"
    },
    "recent_allocations_count": 5,
    "cost_trends": {
      "trend": "decreasing",
      "average_daily_cost": 1.50,
      "projected_monthly_cost": 45.00
    },
    "optimization_score": 85.5
  }
}
```

### Get History

**GET** `/dashboard/history`

Get historical data for charts.

**Query Parameters:**
- `days` (optional): Number of days (default: 7)

**Response:**
```json
{
  "success": true,
  "metrics": [...],
  "allocations": [...],
  "period_days": 7
}
```

## System Endpoints

### Get System Info

**GET** `/system/info`

Get system information.

**Response:**
```json
{
  "success": true,
  "system_info": {
    "hostname": "server-01",
    "platform": "Linux",
    "cpu_count_physical": 4,
    "cpu_count_logical": 8,
    "memory_total_gb": 16.0
  }
}
```

### Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-21T10:30:00Z"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "success": false,
  "message": "Error description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are rate-limited to 100 requests per hour per IP address.

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Pagination

Endpoints that return lists support pagination through the `limit` parameter.

## Timestamps

All timestamps are in ISO 8601 format (UTC):
```
2024-10-21T10:30:00Z
```

## Example Usage

### Python

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']

# Get metrics with authentication
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/metrics', headers=headers)
metrics = response.json()['metrics']
```

### JavaScript

```javascript
// Login
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await response.json();

// Get metrics
const metricsResponse = await fetch('http://localhost:5000/api/metrics', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const { metrics } = await metricsResponse.json();
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Get metrics
curl http://localhost:5000/api/metrics \
  -H "Authorization: Bearer $TOKEN"
```
