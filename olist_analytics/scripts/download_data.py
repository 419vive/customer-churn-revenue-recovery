#!/usr/bin/env python
"""
Script to download Olist dataset from Kaggle
Note: Requires Kaggle API credentials to be configured
"""

import os
import zipfile
import pandas as pd
from pathlib import Path

def download_olist_data():
    """
    Downloads and extracts Olist dataset
    Manual download instructions if Kaggle API not configured
    """
    
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("OLIST DATASET DOWNLOAD INSTRUCTIONS")
    print("=" * 60)
    print("\nOption 1: Manual Download")
    print("-" * 30)
    print("1. Visit: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
    print("2. Download the dataset (brazilian-ecommerce.zip)")
    print(f"3. Extract files to: {data_dir}")
    print("\nRequired files:")
    print("  - olist_orders_dataset.csv")
    print("  - olist_order_payments_dataset.csv")
    print("  - olist_customers_dataset.csv")
    print("  - olist_products_dataset.csv")
    print("  - olist_sellers_dataset.csv")
    print("  - olist_order_reviews_dataset.csv")
    print("  - olist_order_items_dataset.csv")
    print("  - olist_geolocation_dataset.csv")
    
    print("\n" + "=" * 60)
    print("Option 2: Kaggle API (if configured)")
    print("-" * 30)
    print("Run: kaggle datasets download -d olistbr/brazilian-ecommerce")
    print(f"Then extract to: {data_dir}")
    
    print("\n" + "=" * 60)
    print("\nOnce downloaded, run the data validation script:")
    print("python scripts/validate_data.py")
    print("=" * 60)
    
    # Create placeholder for sample data
    sample_data_path = data_dir / "sample_orders.csv"
    if not sample_data_path.exists():
        print("\n📝 Creating sample data for testing...")
        create_sample_data(data_dir)
        print(f"✅ Sample data created at: {sample_data_path}")

def create_sample_data(data_dir):
    """Create sample data for testing without full dataset"""
    import numpy as np
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    n_orders = 1000
    n_customers = 300
    
    # Generate sample orders
    base_date = datetime(2017, 1, 1)
    dates = [base_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_orders)]
    
    sample_orders = pd.DataFrame({
        'order_id': [f'order_{i:04d}' for i in range(n_orders)],
        'customer_id': [f'customer_{np.random.randint(0, n_customers):04d}' for _ in range(n_orders)],
        'order_status': np.random.choice(['delivered', 'shipped', 'processing'], n_orders, p=[0.9, 0.07, 0.03]),
        'order_purchase_timestamp': dates,
        'order_delivered_carrier_date': [d + timedelta(days=np.random.randint(1, 3)) for d in dates],
        'order_delivered_customer_date': [d + timedelta(days=np.random.randint(3, 10)) for d in dates],
        'freight_value': np.random.uniform(10, 50, n_orders)
    })
    
    # Generate sample payments
    sample_payments = pd.DataFrame({
        'order_id': sample_orders['order_id'],
        'payment_sequential': 1,
        'payment_type': np.random.choice(['credit_card', 'boleto', 'debit_card'], n_orders, p=[0.7, 0.2, 0.1]),
        'payment_installments': np.random.choice([1, 2, 3, 6], n_orders, p=[0.5, 0.2, 0.2, 0.1]),
        'payment_value': np.random.uniform(50, 500, n_orders)
    })
    
    # Generate sample customers
    states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'DF']
    unique_customers = sample_orders['customer_id'].unique()
    
    sample_customers = pd.DataFrame({
        'customer_id': unique_customers,
        'customer_unique_id': unique_customers,
        'customer_zip_code_prefix': np.random.randint(10000, 99999, len(unique_customers)),
        'customer_city': [f'city_{i%50}' for i in range(len(unique_customers))],
        'customer_state': np.random.choice(states, len(unique_customers))
    })
    
    # Save sample data
    sample_orders.to_csv(data_dir / 'sample_orders.csv', index=False)
    sample_payments.to_csv(data_dir / 'sample_payments.csv', index=False)
    sample_customers.to_csv(data_dir / 'sample_customers.csv', index=False)
    
    print(f"📊 Created {n_orders} sample orders")
    print(f"👥 Created {len(unique_customers)} sample customers")
    print(f"💳 Created {n_orders} sample payments")

if __name__ == "__main__":
    download_olist_data()