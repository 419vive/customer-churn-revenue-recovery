#!/usr/bin/env python
"""
MVP Main Analysis Script
Run all core analytics in one go
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from analytics.rfm_analysis import RFMAnalyzer
from analytics.cohort_analysis import CohortAnalyzer
from analytics.ltv_modeling import LTVPredictor

def load_data():
    """Load sample data"""
    print("📊 Loading data...")
    orders = pd.read_csv('../data/sample_orders.csv')
    payments = pd.read_csv('../data/sample_payments.csv')
    customers = pd.read_csv('../data/sample_customers.csv')
    return orders, payments, customers

def run_rfm_analysis(orders, payments):
    """Run RFM Analysis"""
    print("\n🎯 Running RFM Analysis...")
    
    # Get reference date (day after last order)
    last_order_date = pd.to_datetime(orders['order_purchase_timestamp']).max()
    reference_date = last_order_date + pd.Timedelta(days=1)
    
    rfm = RFMAnalyzer(reference_date)
    rfm_df = rfm.calculate_rfm(orders, payments)
    rfm_scores = rfm.assign_scores(rfm_df)
    rfm_segments = rfm.create_segments(rfm_scores)
    
    print("\n📈 RFM Segments:")
    print(rfm.get_segment_summary(rfm_segments))
    
    return rfm_segments

def run_cohort_analysis(orders, payments):
    """Run Cohort Analysis"""
    print("\n📅 Running Cohort Analysis...")
    
    cohort = CohortAnalyzer()
    cohort_df = cohort.create_cohorts(orders, payments)
    retention = cohort.calculate_retention(cohort_df)
    
    print("\n📊 Retention Rates (first 3 months):")
    print(retention.iloc[:, :4])
    
    return cohort_df, retention

def run_ltv_analysis(orders, payments):
    """Run LTV Analysis"""
    print("\n💰 Running LTV Analysis...")
    
    ltv = LTVPredictor()
    ltv_df = ltv.calculate_historical_ltv(orders, payments)
    ltv_segments = ltv.segment_ltv(ltv_df)
    
    print("\n💵 LTV Summary:")
    print(ltv.calculate_cac_payback(ltv_df))
    
    return ltv_segments

def generate_insights(rfm_segments, retention, ltv_df):
    """Generate key insights"""
    print("\n" + "="*60)
    print("🔍 KEY INSIGHTS")
    print("="*60)
    
    # RFM insights
    champion_pct = (rfm_segments['segment'] == 'Champions').mean() * 100
    at_risk_pct = (rfm_segments['segment'] == 'At Risk').mean() * 100
    
    print(f"\n1. Customer Segmentation:")
    print(f"   - Champions: {champion_pct:.1f}% of customers")
    print(f"   - At Risk: {at_risk_pct:.1f}% need attention")
    
    # Retention insights
    month_1_retention = retention.iloc[0, 1] if len(retention) > 0 else 0
    print(f"\n2. Retention:")
    print(f"   - Month 1 retention: {month_1_retention:.1f}%")
    
    # LTV insights
    avg_ltv = ltv_df['total_revenue'].mean()
    print(f"\n3. Customer Value:")
    print(f"   - Average LTV: ${avg_ltv:.2f}")
    
    print("\n" + "="*60)

def main():
    """Run complete MVP analysis"""
    print("🚀 Starting Olist Analytics MVP")
    print("="*60)
    
    # Load data
    orders, payments, customers = load_data()
    
    # Run analyses
    rfm_segments = run_rfm_analysis(orders, payments)
    cohort_df, retention = run_cohort_analysis(orders, payments)
    ltv_df = run_ltv_analysis(orders, payments)
    
    # Generate insights
    generate_insights(rfm_segments, retention, ltv_df)
    
    # Save results
    print("\n💾 Saving results...")
    rfm_segments.to_csv('../outputs/rfm_segments.csv', index=False)
    retention.to_csv('../outputs/retention_matrix.csv')
    ltv_df.to_csv('../outputs/customer_ltv.csv')
    
    print("✅ Analysis complete! Check outputs/ folder for results.")

if __name__ == "__main__":
    main()