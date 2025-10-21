import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/cloud_optimizer')
    MONGODB_DB = os.getenv('MONGODB_DB', 'cloud_optimizer')
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Azure Configuration
    AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', '')
    AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID', '')
    AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', '')
    AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID', '')
    
    # GCP Configuration
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
    GCP_CREDENTIALS_PATH = os.getenv('GCP_CREDENTIALS_PATH', '')
    
    # ML Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/saved_models/')
    LSTM_SEQUENCE_LENGTH = int(os.getenv('LSTM_SEQUENCE_LENGTH', '24'))
    LSTM_EPOCHS = int(os.getenv('LSTM_EPOCHS', '50'))
    LSTM_BATCH_SIZE = int(os.getenv('LSTM_BATCH_SIZE', '32'))
    
    # Resource Allocation Thresholds
    CPU_THRESHOLD_HIGH = float(os.getenv('CPU_THRESHOLD_HIGH', '80.0'))
    CPU_THRESHOLD_LOW = float(os.getenv('CPU_THRESHOLD_LOW', '30.0'))
    MEMORY_THRESHOLD_HIGH = float(os.getenv('MEMORY_THRESHOLD_HIGH', '85.0'))
    MEMORY_THRESHOLD_LOW = float(os.getenv('MEMORY_THRESHOLD_LOW', '35.0'))
    
    # Monitoring Configuration
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # seconds
    PREDICTION_INTERVAL = int(os.getenv('PREDICTION_INTERVAL', '300'))  # seconds
    ALLOCATION_INTERVAL = int(os.getenv('ALLOCATION_INTERVAL', '600'))  # seconds
    
    # Cost Optimization
    COST_WEIGHT = float(os.getenv('COST_WEIGHT', '0.5'))
    PERFORMANCE_WEIGHT = float(os.getenv('PERFORMANCE_WEIGHT', '0.5'))
    
    # API Configuration
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100 per hour')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_DB = 'cloud_optimizer_test'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
