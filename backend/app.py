from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
import os

from config import config
from models.database import Database, MetricsModel, PredictionsModel, AllocationsModel, CostModel
from models.prediction import WorkloadPredictor
from models.allocator import ResourceAllocator
from services.monitoring import WorkloadMonitor
from services.cloud_provider import get_cloud_provider, MockProvider
from services.optimizer import CostOptimizer

# Initialize Flask app
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# Setup logging
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()
metrics_model = MetricsModel(db.db)
predictions_model = PredictionsModel(db.db)
allocations_model = AllocationsModel(db.db)
cost_model = CostModel(db.db)

# Initialize services
monitor = WorkloadMonitor(interval=app.config['MONITORING_INTERVAL'])
predictor = WorkloadPredictor(
    sequence_length=app.config['LSTM_SEQUENCE_LENGTH'],
    model_path=app.config['MODEL_PATH']
)
optimizer = CostOptimizer()

# Initialize cloud provider (using mock for demo)
cloud_provider = MockProvider()
allocator = ResourceAllocator(cloud_provider)


# ============= Authentication Routes =============

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simplified authentication (use proper auth in production)
        if username == 'admin' and password == 'admin123':
            access_token = create_access_token(identity=username)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'username': username
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= Metrics Routes =============

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get recent metrics"""
    try:
        limit = request.args.get('limit', 100, type=int)
        resource_id = request.args.get('resource_id')
        
        metrics = metrics_model.get_recent_metrics(limit=limit, resource_id=resource_id)
        
        # Convert ObjectId to string for JSON serialization
        for metric in metrics:
            metric['_id'] = str(metric['_id'])
            if 'timestamp' in metric:
                metric['timestamp'] = metric['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(metrics),
            'metrics': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/metrics/current', methods=['GET'])
def get_current_metrics():
    """Get current system metrics"""
    try:
        current_metrics = monitor.get_current_metrics()
        
        if current_metrics:
            # Make a copy for database
            metrics_copy = current_metrics.copy()
            
            # Save to database
            metrics_model.insert_metric(metrics_copy)
            
            # Convert timestamp for JSON (original dict)
            current_metrics['timestamp'] = current_metrics['timestamp'].isoformat()
            
            return jsonify({
                'success': True,
                'metrics': current_metrics
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to collect metrics'
            }), 500
            
    except Exception as e:
        logger.error(f"Error getting current metrics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/metrics', methods=['POST'])
def submit_metrics():
    """Submit new metrics"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['cpu_usage', 'memory_usage', 'network_usage', 'disk_io']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Insert metric
        result = metrics_model.insert_metric(data)
        
        return jsonify({
            'success': True,
            'message': 'Metrics submitted successfully',
            'id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting metrics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/metrics/aggregated', methods=['GET'])
def get_aggregated_metrics():
    """Get aggregated metrics"""
    try:
        interval = request.args.get('interval', 'hour')
        
        aggregated = metrics_model.get_aggregated_metrics(interval=interval)
        
        return jsonify({
            'success': True,
            'interval': interval,
            'data': aggregated
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting aggregated metrics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= Predictions Routes =============

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get workload predictions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        predictions = predictions_model.get_latest_predictions(limit=limit)
        
        # Convert for JSON
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if 'timestamp' in pred:
                pred['timestamp'] = pred['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/predictions/generate', methods=['POST'])
def generate_predictions():
    """Generate new predictions"""
    try:
        steps = request.args.get('steps', 12, type=int)
        
        # Get recent metrics
        recent_metrics = metrics_model.get_recent_metrics(limit=100)
        
        if len(recent_metrics) < 24:
            return jsonify({
                'success': False,
                'message': 'Insufficient historical data for prediction. Need at least 24 data points. Please wait for more metrics to be collected or generate sample data.'
            }), 400
        
        # Try to load model, if not available, return message
        try:
            predictor.load_model()
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'message': 'Model not trained yet. Please train the model first.'
            }), 400
        
        # Generate predictions
        predictions = predictor.predict_future(recent_metrics, steps=steps)
        
        # Save predictions
        prediction_data = {
            'predictions': predictions,
            'steps': steps,
            'model_type': 'LSTM'
        }
        predictions_model.insert_prediction(prediction_data)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'steps': steps
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/predictions/train', methods=['POST'])
def train_model():
    """Train prediction model"""
    try:
        # Get training parameters
        data = request.get_json() or {}
        epochs = data.get('epochs', app.config['LSTM_EPOCHS'])
        batch_size = data.get('batch_size', app.config['LSTM_BATCH_SIZE'])
        
        # Get historical metrics
        metrics = metrics_model.get_recent_metrics(limit=1000)
        
        if len(metrics) < 100:
            return jsonify({
                'success': False,
                'message': 'Insufficient data for training. Need at least 100 records.'
            }), 400
        
        # Prepare data
        X, y = predictor.prepare_data(metrics)
        
        # Train model
        history = predictor.train(X, y, epochs=epochs, batch_size=batch_size)
        
        # Save model
        predictor.save_model()
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'epochs': epochs,
            'final_loss': float(history.history['loss'][-1])
        }), 200
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= Resource Allocation Routes =============

@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get current resource allocation"""
    try:
        current_allocation = cloud_provider.get_current_resources()
        
        return jsonify({
            'success': True,
            'allocation': current_allocation
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting resources: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/resources/recommendations', methods=['GET'])
def get_recommendations():
    """Get resource allocation recommendations"""
    try:
        # Get recent predictions
        recent_predictions = predictions_model.get_latest_predictions(limit=1)
        
        # Use predictions if available, otherwise use current metrics
        if recent_predictions and recent_predictions[0].get('predictions'):
            latest_prediction = recent_predictions[0]
            predictions_data = {
                'cpu_usage': latest_prediction['predictions'][0] if latest_prediction['predictions'] else 50,
                'memory_usage': 60,  # Simplified
                'network_usage': 40
            }
        else:
            # Use current metrics as fallback
            current_metrics = monitor.get_current_metrics()
            if current_metrics:
                predictions_data = {
                    'cpu_usage': current_metrics.get('cpu_usage', 50),
                    'memory_usage': current_metrics.get('memory_usage', 60),
                    'network_usage': current_metrics.get('network_usage', 40)
                }
            else:
                predictions_data = {
                    'cpu_usage': 50,
                    'memory_usage': 60,
                    'network_usage': 40
                }
        
        # Get current allocation
        current_allocation = cloud_provider.get_current_resources()
        
        # Calculate recommendations
        recommendation = allocator.calculate_required_resources(
            predictions_data,
            current_allocation
        )
        
        if recommendation:
            recommendation['timestamp'] = recommendation['timestamp'].isoformat()
            
            return jsonify({
                'success': True,
                'recommendation': recommendation
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate recommendation'
            }), 500
            
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/resources/allocate', methods=['POST'])
def allocate_resources():
    """Execute resource allocation"""
    try:
        data = request.get_json()
        
        # Get recommendation or use provided data
        if 'recommendation' in data:
            recommendation = data['recommendation']
        else:
            # Generate recommendation
            recent_predictions = predictions_model.get_latest_predictions(limit=1)
            if not recent_predictions:
                return jsonify({
                    'success': False,
                    'message': 'No predictions available'
                }), 400
            
            latest_prediction = recent_predictions[0]
            predictions_data = {
                'cpu_usage': latest_prediction['predictions'][0] if latest_prediction['predictions'] else 50,
                'memory_usage': 60,
                'network_usage': 40
            }
            
            current_allocation = cloud_provider.get_current_resources()
            recommendation = allocator.calculate_required_resources(
                predictions_data,
                current_allocation
            )
        
        # Execute allocation
        result = allocator.execute_allocation(recommendation)
        
        # Save allocation record
        allocation_record = {
            'recommendation': recommendation,
            'result': result,
            'executed_at': datetime.utcnow()
        }
        allocations_model.insert_allocation(allocation_record)
        
        return jsonify({
            'success': result['success'],
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error allocating resources: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= Dashboard Routes =============

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Current metrics
        current_metrics = monitor.get_current_metrics()
        
        # Current allocation
        current_allocation = cloud_provider.get_current_resources()
        
        # Recent allocations
        recent_allocations = allocations_model.get_recent_allocations(limit=10)
        
        # Cost analysis
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        cost_history = list(cost_model.collection.find({
            'timestamp': {'$gte': start_time, '$lte': end_time}
        }))
        
        cost_trends = optimizer.analyze_cost_trends(cost_history)
        
        # Optimization score
        optimization_score = optimizer.calculate_optimization_score(
            current_allocation,
            current_metrics or {}
        )
        
        stats = {
            'current_metrics': current_metrics,
            'current_allocation': current_allocation,
            'recent_allocations_count': len(recent_allocations),
            'cost_trends': cost_trends,
            'optimization_score': optimization_score,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Convert timestamps
        if stats['current_metrics'] and 'timestamp' in stats['current_metrics']:
            stats['current_metrics']['timestamp'] = stats['current_metrics']['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/dashboard/history', methods=['GET'])
def get_history():
    """Get historical data"""
    try:
        days = request.args.get('days', 7, type=int)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Get metrics history
        metrics_history = metrics_model.get_metrics_by_timerange(start_time, end_time)
        
        # Get allocation history
        allocation_history = allocations_model.get_allocation_history(days=days)
        
        # Convert timestamps
        for metric in metrics_history:
            metric['_id'] = str(metric['_id'])
            metric['timestamp'] = metric['timestamp'].isoformat()
        
        for allocation in allocation_history:
            allocation['_id'] = str(allocation['_id'])
            allocation['timestamp'] = allocation['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'metrics': metrics_history,
            'allocations': allocation_history,
            'period_days': days
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= System Routes =============

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        system_info = monitor.get_system_info()
        
        return jsonify({
            'success': True,
            'system_info': system_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============= Error Handlers =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


# ============= Startup =============

if __name__ == '__main__':
    logger.info("Starting Cloud Resource Optimizer API")
    logger.info(f"Environment: {env}")
    
    # Start monitoring in background
    def metrics_callback(metrics):
        """Callback to save metrics"""
        try:
            metrics_model.insert_metric(metrics)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
    
    monitor.start_monitoring(callback=metrics_callback)
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(env == 'development')
    )
