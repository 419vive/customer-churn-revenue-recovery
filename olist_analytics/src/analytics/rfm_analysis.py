"""
MVP RFM Analysis Module
Simple and effective customer segmentation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RFMAnalyzer:
    """Simple RFM Analysis - MVP Version"""
    
    def __init__(self, reference_date=None):
        self.reference_date = reference_date or datetime.now()
        
    def calculate_rfm(self, orders_df, payments_df):
        """
        Calculate RFM metrics
        Keep it simple - just the essentials
        """
        # Merge orders with payments
        df = orders_df.merge(payments_df, on='order_id')
        
        # Convert dates
        df['order_date'] = pd.to_datetime(df['order_purchase_timestamp'])
        
        # Calculate RFM
        rfm = df.groupby('customer_id').agg({
            'order_date': lambda x: (self.reference_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency  
            'payment_value': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        return rfm
    
    def assign_scores(self, rfm_df):
        """Simple 1-5 scoring using quantiles"""
        rfm = rfm_df.copy()
        
        # Create bins with error handling for small datasets
        try:
            rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
        except (ValueError, TypeError):
            # Fallback for small datasets - use simple ranking
            rfm['r_score'] = pd.cut(rfm['recency'], bins=5, labels=[5,4,3,2,1], duplicates='drop').fillna(3)
            
        try:
            rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
        except (ValueError, TypeError):
            rfm['f_score'] = pd.cut(rfm['frequency'], bins=5, labels=[1,2,3,4,5], duplicates='drop').fillna(3)
            
        try:
            rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')
        except (ValueError, TypeError):
            rfm['m_score'] = pd.cut(rfm['monetary'], bins=5, labels=[1,2,3,4,5], duplicates='drop').fillna(3)
        
        # Convert categorical scores to numeric and ensure valid range (1-5)
        rfm['r_score'] = pd.to_numeric(rfm['r_score'], errors='coerce').fillna(3).clip(1, 5)
        rfm['f_score'] = pd.to_numeric(rfm['f_score'], errors='coerce').fillna(3).clip(1, 5)
        rfm['m_score'] = pd.to_numeric(rfm['m_score'], errors='coerce').fillna(3).clip(1, 5)
        
        # Combine scores
        r_str = rfm['r_score'].astype(int).astype(str)
        f_str = rfm['f_score'].astype(int).astype(str)
        m_str = rfm['m_score'].astype(int).astype(str)
        rfm['rfm_score'] = r_str + f_str + m_str
        
        return rfm
    
    def create_segments(self, rfm_scores):
        """Simple segmentation logic"""
        rfm = rfm_scores.copy()
        
        # MVP segments - keep it simple
        def segment_customers(row):
            if row['rfm_score'] in ['555', '554', '544', '545', '454', '455', '445']:
                return 'Champions'
            elif row['r_score'] >= 4 and row['f_score'] >= 3:
                return 'Loyal Customers'
            elif row['r_score'] >= 3 and row['m_score'] >= 4:
                return 'Big Spenders'
            elif row['r_score'] <= 2 and row['f_score'] >= 3:
                return 'At Risk'
            elif row['r_score'] <= 2:
                return 'Lost'
            else:
                return 'Regular'
        
        rfm['segment'] = rfm.apply(segment_customers, axis=1)
        
        return rfm
    
    def get_segment_summary(self, rfm_df):
        """Quick segment summary"""
        summary = rfm_df.groupby('segment').agg({
            'customer_id': 'count',
            'monetary': ['mean', 'sum']
        }).round(2)
        
        summary.columns = ['customer_count', 'avg_revenue', 'total_revenue']
        summary['pct_customers'] = (summary['customer_count'] / summary['customer_count'].sum() * 100).round(1)
        summary['pct_revenue'] = (summary['total_revenue'] / summary['total_revenue'].sum() * 100).round(1)
        
        return summary