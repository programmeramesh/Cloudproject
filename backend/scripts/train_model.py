#!/usr/bin/env python
"""
Script to train the LSTM prediction model
Usage: python train_model.py --data <data_file> --epochs <num_epochs>
"""

import argparse
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.prediction import WorkloadPredictor
from models.database import Database, MetricsModel


def train_from_file(data_file, epochs=50, batch_size=32):
    """Train model from CSV file"""
    print(f"Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Initialize predictor
    predictor = WorkloadPredictor()
    
    # Prepare data
    print("Preparing data...")
    X, y = predictor.prepare_data(df)
    print(f"Training samples: {X.shape[0]}")
    
    # Train model
    print(f"Training model for {epochs} epochs...")
    history = predictor.train(X, y, epochs=epochs, batch_size=batch_size)
    
    # Save model
    print("Saving model...")
    predictor.save_model()
    
    print("Training complete!")
    print(f"Final loss: {history.history['loss'][-1]:.4f}")
    print(f"Final MAE: {history.history['mae'][-1]:.4f}")


def train_from_database(epochs=50, batch_size=32, limit=1000):
    """Train model from database"""
    print("Connecting to database...")
    db = Database()
    metrics_model = MetricsModel(db.db)
    
    print(f"Fetching {limit} metrics from database...")
    metrics = metrics_model.get_recent_metrics(limit=limit)
    
    if len(metrics) < 100:
        print(f"Error: Insufficient data. Found {len(metrics)} records, need at least 100.")
        return
    
    print(f"Found {len(metrics)} metrics")
    
    # Convert to DataFrame
    df = pd.DataFrame(metrics)
    
    # Initialize predictor
    predictor = WorkloadPredictor()
    
    # Prepare data
    print("Preparing data...")
    X, y = predictor.prepare_data(df)
    print(f"Training samples: {X.shape[0]}")
    
    # Train model
    print(f"Training model for {epochs} epochs...")
    history = predictor.train(X, y, epochs=epochs, batch_size=batch_size)
    
    # Save model
    print("Saving model...")
    predictor.save_model()
    
    print("Training complete!")
    print(f"Final loss: {history.history['loss'][-1]:.4f}")
    print(f"Final MAE: {history.history['mae'][-1]:.4f}")
    
    db.close()


def main():
    parser = argparse.ArgumentParser(description='Train LSTM workload prediction model')
    parser.add_argument('--data', type=str, help='Path to CSV data file')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--from-db', action='store_true', help='Train from database instead of file')
    parser.add_argument('--limit', type=int, default=1000, help='Number of records to fetch from database')
    
    args = parser.parse_args()
    
    if args.from_db:
        train_from_database(epochs=args.epochs, batch_size=args.batch_size, limit=args.limit)
    elif args.data:
        train_from_file(args.data, epochs=args.epochs, batch_size=args.batch_size)
    else:
        print("Error: Please specify either --data <file> or --from-db")
        parser.print_help()


if __name__ == '__main__':
    main()
