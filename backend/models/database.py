from datetime import datetime
from pymongo import MongoClient, DESCENDING
from config import Config


class Database:
    """Database connection and operations"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.MONGODB_DB]
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        # Metrics collection indexes
        self.db.metrics.create_index([('timestamp', DESCENDING)])
        self.db.metrics.create_index([('resource_id', 1), ('timestamp', DESCENDING)])
        
        # Predictions collection indexes
        self.db.predictions.create_index([('timestamp', DESCENDING)])
        
        # Allocations collection indexes
        self.db.allocations.create_index([('timestamp', DESCENDING)])
    
    def close(self):
        """Close database connection"""
        self.client.close()


class MetricsModel:
    """Model for workload metrics"""
    
    def __init__(self, db):
        self.collection = db.metrics
    
    def insert_metric(self, metric_data):
        """Insert a new metric record"""
        metric_data['timestamp'] = datetime.utcnow()
        return self.collection.insert_one(metric_data)
    
    def get_recent_metrics(self, limit=100, resource_id=None):
        """Get recent metrics"""
        query = {}
        if resource_id:
            query['resource_id'] = resource_id
        
        return list(self.collection.find(query)
                   .sort('timestamp', DESCENDING)
                   .limit(limit))
    
    def get_metrics_by_timerange(self, start_time, end_time, resource_id=None):
        """Get metrics within a time range"""
        query = {
            'timestamp': {
                '$gte': start_time,
                '$lte': end_time
            }
        }
        if resource_id:
            query['resource_id'] = resource_id
        
        return list(self.collection.find(query).sort('timestamp', 1))
    
    def get_aggregated_metrics(self, interval='hour'):
        """Get aggregated metrics by interval"""
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d-%H' if interval == 'hour' else '%Y-%m-%d',
                            'date': '$timestamp'
                        }
                    },
                    'avg_cpu': {'$avg': '$cpu_usage'},
                    'avg_memory': {'$avg': '$memory_usage'},
                    'avg_network': {'$avg': '$network_usage'},
                    'max_cpu': {'$max': '$cpu_usage'},
                    'max_memory': {'$max': '$memory_usage'}
                }
            },
            {'$sort': {'_id': -1}},
            {'$limit': 100}
        ]
        return list(self.collection.aggregate(pipeline))


class PredictionsModel:
    """Model for workload predictions"""
    
    def __init__(self, db):
        self.collection = db.predictions
    
    def insert_prediction(self, prediction_data):
        """Insert a new prediction"""
        prediction_data['timestamp'] = datetime.utcnow()
        return self.collection.insert_one(prediction_data)
    
    def get_latest_predictions(self, limit=50):
        """Get latest predictions"""
        return list(self.collection.find()
                   .sort('timestamp', DESCENDING)
                   .limit(limit))
    
    def get_predictions_by_timerange(self, start_time, end_time):
        """Get predictions within a time range"""
        query = {
            'timestamp': {
                '$gte': start_time,
                '$lte': end_time
            }
        }
        return list(self.collection.find(query).sort('timestamp', 1))


class AllocationsModel:
    """Model for resource allocations"""
    
    def __init__(self, db):
        self.collection = db.allocations
    
    def insert_allocation(self, allocation_data):
        """Insert a new allocation record"""
        allocation_data['timestamp'] = datetime.utcnow()
        return self.collection.insert_one(allocation_data)
    
    def get_recent_allocations(self, limit=50):
        """Get recent allocations"""
        return list(self.collection.find()
                   .sort('timestamp', DESCENDING)
                   .limit(limit))
    
    def get_current_allocation(self):
        """Get the most recent allocation"""
        return self.collection.find_one(sort=[('timestamp', DESCENDING)])
    
    def get_allocation_history(self, days=7):
        """Get allocation history for specified days"""
        start_time = datetime.utcnow() - timedelta(days=days)
        query = {'timestamp': {'$gte': start_time}}
        return list(self.collection.find(query).sort('timestamp', 1))


class CostModel:
    """Model for cost tracking"""
    
    def __init__(self, db):
        self.collection = db.costs
    
    def insert_cost_record(self, cost_data):
        """Insert a cost record"""
        cost_data['timestamp'] = datetime.utcnow()
        return self.collection.insert_one(cost_data)
    
    def get_total_cost(self, start_time, end_time):
        """Calculate total cost for a time period"""
        pipeline = [
            {
                '$match': {
                    'timestamp': {
                        '$gte': start_time,
                        '$lte': end_time
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_cost': {'$sum': '$cost'}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        return result[0]['total_cost'] if result else 0
    
    def get_cost_breakdown(self, days=30):
        """Get daily cost breakdown"""
        start_time = datetime.utcnow() - timedelta(days=days)
        pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': start_time}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$timestamp'
                        }
                    },
                    'daily_cost': {'$sum': '$cost'},
                    'resource_type': {'$first': '$resource_type'}
                }
            },
            {'$sort': {'_id': -1}}
        ]
        return list(self.collection.aggregate(pipeline))


# Import timedelta for date calculations
from datetime import timedelta
