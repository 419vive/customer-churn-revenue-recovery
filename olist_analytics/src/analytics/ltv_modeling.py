"""
MVP LTV Modeling
Simple customer lifetime value calculations
"""

import pandas as pd
import numpy as np

class LTVPredictor:
    """Simple LTV Calculator - MVP Version"""
    
    def __init__(self):
        pass
    
    def calculate_historical_ltv(self, orders_df, payments_df, days=365):
        """Calculate historical LTV per customer"""
        df = orders_df.merge(payments_df, on='order_id')
        
        ltv = df.groupby('customer_id').agg({
            'payment_value': 'sum',
            'order_id': 'count',
            'order_purchase_timestamp': ['min', 'max']
        })
        
        ltv.columns = ['total_revenue', 'order_count', 'first_order', 'last_order']
        ltv['avg_order_value'] = ltv['total_revenue'] / ltv['order_count']
        
        # Calculate customer lifespan
        ltv['first_order'] = pd.to_datetime(ltv['first_order'])
        ltv['last_order'] = pd.to_datetime(ltv['last_order'])
        ltv['lifespan_days'] = (ltv['last_order'] - ltv['first_order']).dt.days + 1
        
        return ltv.round(2)
    
    def predict_simple_ltv(self, rfm_df, avg_order_value, purchase_frequency, retention_rate=0.8):
        """
        Simple LTV prediction
        LTV = AOV × Purchase Frequency × Customer Lifespan
        """
        # Simple formula-based LTV
        customer_lifespan = 1 / (1 - retention_rate)  # in periods
        ltv = avg_order_value * purchase_frequency * customer_lifespan
        
        return ltv
    
    def segment_ltv(self, ltv_df):
        """Segment customers by LTV"""
        ltv = ltv_df.copy()
        
        # Simple tiers
        ltv['ltv_tier'] = pd.qcut(ltv['total_revenue'], 
                                   q=[0, 0.25, 0.5, 0.75, 1.0],
                                   labels=['Low', 'Medium', 'High', 'VIP'])
        
        return ltv
    
    def calculate_cac_payback(self, ltv_df, cac=50):
        """Calculate CAC payback period"""
        summary = {
            'avg_ltv': ltv_df['total_revenue'].mean(),
            'median_ltv': ltv_df['total_revenue'].median(),
            'cac': cac,
            'ltv_cac_ratio': ltv_df['total_revenue'].mean() / cac,
            'profitable_customers_pct': (ltv_df['total_revenue'] > cac).mean() * 100
        }
        
        return pd.Series(summary).round(2)