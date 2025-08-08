"""
MVP Cohort Analysis Module
Simple retention and revenue cohort tracking
"""

import pandas as pd
import numpy as np

class CohortAnalyzer:
    """Simple Cohort Analysis - MVP Version"""
    
    def __init__(self):
        pass
    
    def create_cohorts(self, orders_df, payments_df):
        """Create monthly cohorts"""
        # Merge data
        df = orders_df.merge(payments_df, on='order_id')
        df['order_date'] = pd.to_datetime(df['order_purchase_timestamp'])
        
        # Get first purchase date per customer
        df['cohort_month'] = df.groupby('customer_id')['order_date'].transform('min')
        df['cohort_month'] = df['cohort_month'].dt.to_period('M')
        
        # Calculate cohort index (months since first purchase)
        df['order_month'] = df['order_date'].dt.to_period('M')
        df['cohort_index'] = (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)
        
        return df
    
    def calculate_retention(self, cohort_df):
        """Calculate retention rates"""
        # Count unique customers per cohort per month
        cohort_data = cohort_df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
        cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customer_id')
        
        # Calculate retention rate
        cohort_size = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(cohort_size, axis=0) * 100
        
        return retention.round(1)
    
    def calculate_revenue_cohorts(self, cohort_df):
        """Calculate revenue by cohort"""
        # Sum revenue per cohort per month
        revenue_data = cohort_df.groupby(['cohort_month', 'cohort_index'])['payment_value'].sum().reset_index()
        revenue_pivot = revenue_data.pivot(index='cohort_month', columns='cohort_index', values='payment_value')
        
        return revenue_pivot.round(2)
    
    def get_cohort_metrics(self, cohort_df):
        """Quick cohort metrics summary"""
        metrics = cohort_df.groupby('cohort_month').agg({
            'customer_id': 'nunique',
            'order_id': 'count',
            'payment_value': 'sum'
        }).reset_index()
        
        metrics.columns = ['cohort', 'customers', 'orders', 'revenue']
        metrics['avg_order_value'] = (metrics['revenue'] / metrics['orders']).round(2)
        metrics['orders_per_customer'] = (metrics['orders'] / metrics['customers']).round(2)
        
        return metrics