import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os
from datetime import datetime, timedelta


class WorkloadPredictor:
    """LSTM-based workload prediction model"""
    
    def __init__(self, sequence_length=24, model_path='models/saved_models/'):
        self.sequence_length = sequence_length
        self.model_path = model_path
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_columns = ['cpu_usage', 'memory_usage', 'network_usage', 'disk_io']
        
        # Create model directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_data(self, data, target_column='cpu_usage'):
        """Prepare data for LSTM training"""
        # Convert to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Select features
        features = df[self.feature_columns].values
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:i + self.sequence_length])
            y.append(scaled_data[i + self.sequence_length, 0])  # Predict CPU usage
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        model = Sequential([
            LSTM(128, activation='relu', return_sequences=True, 
                 input_shape=input_shape),
            Dropout(0.2),
            LSTM(64, activation='relu', return_sequences=True),
            Dropout(0.2),
            LSTM(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
        """Train the LSTM model"""
        # Build model
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        checkpoint = ModelCheckpoint(
            os.path.join(self.model_path, 'best_model.h5'),
            monitor='val_loss',
            save_best_only=True
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stopping, checkpoint],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        predictions = self.model.predict(X)
        return predictions
    
    def predict_future(self, recent_data, steps=12):
        """Predict future workload for specified steps"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        # Prepare recent data
        if isinstance(recent_data, list):
            df = pd.DataFrame(recent_data)
        else:
            df = recent_data.copy()
        
        # Get last sequence
        features = df[self.feature_columns].tail(self.sequence_length).values
        scaled_data = self.scaler.transform(features)
        
        predictions = []
        current_sequence = scaled_data.copy()
        
        for _ in range(steps):
            # Reshape for prediction
            X = current_sequence.reshape(1, self.sequence_length, len(self.feature_columns))
            
            # Predict next value
            pred = self.model.predict(X, verbose=0)[0][0]
            predictions.append(pred)
            
            # Update sequence (shift and add prediction)
            new_row = current_sequence[-1].copy()
            new_row[0] = pred  # Update CPU usage
            current_sequence = np.vstack([current_sequence[1:], new_row])
        
        # Inverse transform predictions
        predictions_array = np.array(predictions).reshape(-1, 1)
        dummy = np.zeros((len(predictions), len(self.feature_columns)))
        dummy[:, 0] = predictions_array.flatten()
        predictions_original = self.scaler.inverse_transform(dummy)[:, 0]
        
        return predictions_original.tolist()
    
    def save_model(self, filename='lstm_model.h5'):
        """Save trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        model_file = os.path.join(self.model_path, filename)
        scaler_file = os.path.join(self.model_path, 'scaler.pkl')
        
        self.model.save(model_file)
        joblib.dump(self.scaler, scaler_file)
        
        print(f"Model saved to {model_file}")
    
    def load_model(self, filename='lstm_model.h5'):
        """Load trained model"""
        model_file = os.path.join(self.model_path, filename)
        scaler_file = os.path.join(self.model_path, 'scaler.pkl')
        
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        self.model = load_model(model_file)
        self.scaler = joblib.load(scaler_file)
        
        print(f"Model loaded from {model_file}")
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        loss, mae, mse = self.model.evaluate(X_test, y_test, verbose=0)
        
        return {
            'loss': loss,
            'mae': mae,
            'mse': mse,
            'rmse': np.sqrt(mse)
        }


class RandomForestPredictor:
    """Alternative: Random Forest-based predictor for smaller datasets"""
    
    def __init__(self, model_path='models/saved_models/'):
        self.model_path = model_path
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = MinMaxScaler()
        self.feature_columns = ['cpu_usage', 'memory_usage', 'network_usage', 'disk_io']
        
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_features(self, data):
        """Prepare features for Random Forest"""
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Add time-based features
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        
        # Add lag features
        for col in self.feature_columns:
            df[f'{col}_lag1'] = df[col].shift(1)
            df[f'{col}_lag2'] = df[col].shift(2)
        
        df = df.dropna()
        
        return df
    
    def train(self, X_train, y_train):
        """Train Random Forest model"""
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        
        return self.model
    
    def predict(self, X):
        """Make predictions"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def save_model(self, filename='rf_model.pkl'):
        """Save model"""
        model_file = os.path.join(self.model_path, filename)
        scaler_file = os.path.join(self.model_path, 'rf_scaler.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
    
    def load_model(self, filename='rf_model.pkl'):
        """Load model"""
        model_file = os.path.join(self.model_path, filename)
        scaler_file = os.path.join(self.model_path, 'rf_scaler.pkl')
        
        self.model = joblib.load(model_file)
        self.scaler = joblib.load(scaler_file)
