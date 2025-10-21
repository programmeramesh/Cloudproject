#!/usr/bin/env python
"""
Generate sample workload data for testing
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import Database, MetricsModel


def generate_sample_data(num_records=1000):
    """Generate sample workload data with realistic patterns"""
    
    print(f"Generating {num_records} sample records...")
    
    # Start time
    start_time = datetime.utcnow() - timedelta(hours=num_records)
    
    data = []
    
    for i in range(num_records):
        timestamp = start_time + timedelta(hours=i)
        hour = timestamp.hour
        
        # Simulate daily patterns
        # Higher usage during business hours (9-17)
        if 9 <= hour <= 17:
            base_cpu = 60 + np.random.normal(0, 10)
            base_memory = 65 + np.random.normal(0, 8)
        else:
            base_cpu = 30 + np.random.normal(0, 8)
            base_memory = 40 + np.random.normal(0, 6)
        
        # Add some random spikes
        if np.random.random() < 0.05:  # 5% chance of spike
            base_cpu += np.random.uniform(20, 30)
            base_memory += np.random.uniform(15, 25)
        
        # Clip values to valid range
        cpu_usage = np.clip(base_cpu, 0, 100)
        memory_usage = np.clip(base_memory, 0, 100)
        
        # Network and disk usage (correlated with CPU)
        network_usage = np.clip(cpu_usage * 0.7 + np.random.normal(0, 5), 0, 100)
        disk_io = np.clip(cpu_usage * 0.5 + np.random.normal(0, 8), 0, 100)
        
        record = {
            'timestamp': timestamp,
            'cpu_usage': round(cpu_usage, 2),
            'memory_usage': round(memory_usage, 2),
            'network_usage': round(network_usage, 2),
            'disk_io': round(disk_io, 2),
            'resource_id': 'sample-instance-1'
        }
        
        data.append(record)
    
    return data


def save_to_csv(data, filename='sample_workload_data.csv'):
    """Save data to CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved {len(data)} records to {filename}")


def save_to_database(data):
    """Save data to MongoDB"""
    print("Connecting to database...")
    db = Database()
    metrics_model = MetricsModel(db.db)
    
    print(f"Inserting {len(data)} records...")
    for record in data:
        metrics_model.insert_metric(record)
    
    print("Data inserted successfully!")
    db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample workload data')
    parser.add_argument('--records', type=int, default=1000, help='Number of records to generate')
    parser.add_argument('--output', type=str, default='sample_workload_data.csv', help='Output CSV file')
    parser.add_argument('--to-db', action='store_true', help='Save to database instead of CSV')
    
    args = parser.parse_args()
    
    # Generate data
    data = generate_sample_data(args.records)
    
    # Save data
    if args.to_db:
        save_to_database(data)
    else:
        save_to_csv(data, args.output)


if __name__ == '__main__':
    main()
