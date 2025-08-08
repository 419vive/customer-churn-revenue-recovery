"""
Advanced Breakdown Analysis Module
Deeper dive into customer behavior patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class AdvancedAnalyzer:
    """Deep dive analysis - detailed breakdowns"""
    
    def __init__(self):
        pass
    
    def detailed_rfm_breakdown(self, rfm_df):
        """Detailed RFM segment analysis with actionable insights"""
        print("=" * 80)
        print("🔍 DETAILED RFM SEGMENT BREAKDOWN")
        print("=" * 80)
        
        # Overall distribution
        segment_stats = rfm_df.groupby('segment').agg({
            'customer_id': 'count',
            'recency': ['mean', 'median', 'std'],
            'frequency': ['mean', 'median', 'std'],
            'monetary': ['mean', 'median', 'std', 'sum']
        }).round(2)
        
        # Flatten column names
        segment_stats.columns = ['_'.join(col).strip() for col in segment_stats.columns]
        
        print("\n📊 Segment Performance Matrix:")
        print("-" * 80)
        for segment in rfm_df['segment'].unique():
            data = rfm_df[rfm_df['segment'] == segment]
            count = len(data)
            pct = count / len(rfm_df) * 100
            
            print(f"\n🏷️  {segment.upper()} ({count} customers, {pct:.1f}%)")
            print(f"   Recency: {data['recency'].mean():.0f} days (median: {data['recency'].median():.0f})")
            print(f"   Frequency: {data['frequency'].mean():.1f} orders (median: {data['frequency'].median():.1f})")
            print(f"   Monetary: ${data['monetary'].mean():.2f} (median: ${data['monetary'].median():.2f})")
            print(f"   Total Revenue: ${data['monetary'].sum():.2f}")
            print(f"   Revenue %: {data['monetary'].sum() / rfm_df['monetary'].sum() * 100:.1f}%")
            
            # Segment-specific insights
            self._generate_segment_insights(segment, data)
        
        return segment_stats
    
    def _generate_segment_insights(self, segment, data):
        """Generate specific insights for each segment"""
        if segment == 'Champions':
            print("   💡 ACTION: Reward loyalty, ask for referrals, offer premium products")
        elif segment == 'Loyal Customers':
            print("   💡 ACTION: Upsell/cross-sell, loyalty programs, exclusive access")
        elif segment == 'Big Spenders':
            print("   💡 ACTION: Focus on retention, personalized offers, VIP treatment")
        elif segment == 'At Risk':
            print("   💡 ACTION: Win-back campaigns, special discounts, feedback surveys")
        elif segment == 'Lost':
            print("   💡 ACTION: Aggressive win-back, deep discounts, understand churn reasons")
        else:
            print("   💡 ACTION: Nurture growth, educational content, engagement campaigns")
    
    def cohort_deep_dive(self, cohort_df, retention_matrix):
        """Detailed cohort analysis with patterns"""
        print("\n" + "=" * 80)
        print("📅 DETAILED COHORT BEHAVIOR ANALYSIS")
        print("=" * 80)
        
        # Cohort size analysis
        cohort_sizes = cohort_df[cohort_df['cohort_index'] == 0].groupby('cohort_month').size()
        
        print("\n📈 Cohort Size Trends:")
        print("-" * 40)
        for month, size in cohort_sizes.items():
            print(f"   {month}: {size} new customers")
        
        # Retention pattern analysis
        print("\n🔄 Retention Pattern Analysis:")
        print("-" * 40)
        
        # Calculate average retention by period
        avg_retention = retention_matrix.mean()
        
        for period in range(min(4, len(avg_retention))):
            if not pd.isna(avg_retention.iloc[period]):
                retention_rate = avg_retention.iloc[period]
                print(f"   Month {period}: {retention_rate:.1f}% average retention")
                
                if period == 1:
                    if retention_rate > 30:
                        print("     ✅ Good month-1 retention")
                    else:
                        print("     ⚠️  Month-1 retention needs improvement")
                elif period == 2:
                    if retention_rate > 20:
                        print("     ✅ Solid month-2 retention")
                    else:
                        print("     ⚠️  Month-2 retention opportunity")
        
        # Cohort revenue analysis
        revenue_cohorts = self._calculate_cohort_revenue(cohort_df)
        
        print("\n💰 Revenue Cohort Insights:")
        print("-" * 40)
        for cohort in revenue_cohorts.head(5).index:
            total_revenue = revenue_cohorts.loc[cohort].sum()
            month_0_revenue = revenue_cohorts.loc[cohort, 0] if 0 in revenue_cohorts.columns else 0
            
            print(f"   {cohort}: ${total_revenue:.0f} total (${month_0_revenue:.0f} in month 0)")
        
        return avg_retention
    
    def _calculate_cohort_revenue(self, cohort_df):
        """Calculate revenue by cohort and period"""
        revenue_data = cohort_df.groupby(['cohort_month', 'cohort_index'])['payment_value'].sum().reset_index()
        revenue_pivot = revenue_data.pivot(index='cohort_month', columns='cohort_index', values='payment_value')
        return revenue_pivot.fillna(0)
    
    def ltv_deep_analysis(self, ltv_df, orders_df, payments_df):
        """Advanced LTV analysis with customer journey insights"""
        print("\n" + "=" * 80)
        print("💰 ADVANCED CUSTOMER LIFETIME VALUE ANALYSIS")
        print("=" * 80)
        
        # Customer journey analysis
        df = orders_df.merge(payments_df, on='order_id')
        
        # Calculate customer metrics
        customer_journey = df.groupby('customer_id').agg({
            'order_id': 'count',
            'payment_value': ['sum', 'mean', 'std'],
            'order_purchase_timestamp': ['min', 'max']
        })
        
        customer_journey.columns = ['total_orders', 'total_spent', 'avg_order_value', 'order_value_std', 'first_order', 'last_order']
        
        # Calculate customer lifespan
        customer_journey['first_order'] = pd.to_datetime(customer_journey['first_order'])
        customer_journey['last_order'] = pd.to_datetime(customer_journey['last_order'])
        customer_journey['lifespan_days'] = (customer_journey['last_order'] - customer_journey['first_order']).dt.days + 1
        
        print("\n📊 Customer Journey Metrics:")
        print("-" * 50)
        print(f"   Average orders per customer: {customer_journey['total_orders'].mean():.2f}")
        print(f"   Average customer lifespan: {customer_journey['lifespan_days'].mean():.0f} days")
        print(f"   Average order value: ${customer_journey['avg_order_value'].mean():.2f}")
        print(f"   Order value consistency (std): ${customer_journey['order_value_std'].mean():.2f}")
        
        # LTV distribution analysis
        print("\n💵 LTV Distribution Breakdown:")
        print("-" * 50)
        
        ltv_percentiles = [10, 25, 50, 75, 90, 95, 99]
        ltv_values = customer_journey['total_spent']
        
        for p in ltv_percentiles:
            value = np.percentile(ltv_values, p)
            print(f"   {p}th percentile: ${value:.2f}")
        
        # Customer value tiers with detailed analysis
        self._analyze_customer_tiers(customer_journey)
        
        # Purchase behavior patterns
        self._analyze_purchase_patterns(customer_journey)
        
        return customer_journey
    
    def _analyze_customer_tiers(self, customer_journey):
        """Analyze different customer value tiers"""
        # Create detailed tiers
        customer_journey['value_tier'] = pd.qcut(
            customer_journey['total_spent'], 
            q=[0, 0.2, 0.5, 0.8, 0.95, 1.0],
            labels=['Bottom 20%', 'Low Value', 'Medium Value', 'High Value', 'Top 5%']
        )
        
        print("\n🏆 Customer Value Tier Analysis:")
        print("-" * 50)
        
        for tier in customer_journey['value_tier'].cat.categories:
            tier_data = customer_journey[customer_journey['value_tier'] == tier]
            count = len(tier_data)
            pct = count / len(customer_journey) * 100
            
            print(f"\n   {tier} ({count} customers, {pct:.1f}%):")
            print(f"     Avg LTV: ${tier_data['total_spent'].mean():.2f}")
            print(f"     Avg Orders: {tier_data['total_orders'].mean():.2f}")
            print(f"     Avg AOV: ${tier_data['avg_order_value'].mean():.2f}")
            print(f"     Total Revenue: ${tier_data['total_spent'].sum():.2f}")
            print(f"     Revenue Share: {tier_data['total_spent'].sum() / customer_journey['total_spent'].sum() * 100:.1f}%")
    
    def _analyze_purchase_patterns(self, customer_journey):
        """Analyze purchase behavior patterns"""
        print("\n🛒 Purchase Behavior Pattern Analysis:")
        print("-" * 50)
        
        # Single purchase vs repeat customers
        single_purchase = customer_journey[customer_journey['total_orders'] == 1]
        repeat_customers = customer_journey[customer_journey['total_orders'] > 1]
        
        print(f"\n   One-time buyers: {len(single_purchase)} ({len(single_purchase)/len(customer_journey)*100:.1f}%)")
        print(f"     Avg spend: ${single_purchase['total_spent'].mean():.2f}")
        print(f"     Total revenue: ${single_purchase['total_spent'].sum():.2f}")
        
        print(f"\n   Repeat customers: {len(repeat_customers)} ({len(repeat_customers)/len(customer_journey)*100:.1f}%)")
        print(f"     Avg orders: {repeat_customers['total_orders'].mean():.2f}")
        print(f"     Avg LTV: ${repeat_customers['total_spent'].mean():.2f}")
        print(f"     Total revenue: ${repeat_customers['total_spent'].sum():.2f}")
        print(f"     Revenue share: {repeat_customers['total_spent'].sum() / customer_journey['total_spent'].sum() * 100:.1f}%")
        
        # High-frequency customers (4+ orders)
        high_freq = customer_journey[customer_journey['total_orders'] >= 4]
        if len(high_freq) > 0:
            print(f"\n   High-frequency customers (4+ orders): {len(high_freq)} ({len(high_freq)/len(customer_journey)*100:.1f}%)")
            print(f"     Avg orders: {high_freq['total_orders'].mean():.2f}")
            print(f"     Avg LTV: ${high_freq['total_spent'].mean():.2f}")
            print(f"     Revenue share: {high_freq['total_spent'].sum() / customer_journey['total_spent'].sum() * 100:.1f}%")
    
    def payment_method_analysis(self, payments_df):
        """Detailed payment method and behavior analysis"""
        print("\n" + "=" * 80)
        print("💳 PAYMENT METHOD & BEHAVIOR ANALYSIS")
        print("=" * 80)
        
        # Payment type analysis
        payment_analysis = payments_df.groupby('payment_type').agg({
            'payment_value': ['count', 'sum', 'mean', 'median', 'std'],
            'payment_installments': ['mean', 'median']
        }).round(2)
        
        print("\n💰 Payment Method Breakdown:")
        print("-" * 60)
        
        total_revenue = payments_df['payment_value'].sum()
        total_orders = len(payments_df)
        
        for payment_type in payments_df['payment_type'].unique():
            data = payments_df[payments_df['payment_type'] == payment_type]
            count = len(data)
            revenue = data['payment_value'].sum()
            avg_value = data['payment_value'].mean()
            
            print(f"\n   {payment_type.upper()}:")
            print(f"     Orders: {count} ({count/total_orders*100:.1f}%)")
            print(f"     Revenue: ${revenue:.2f} ({revenue/total_revenue*100:.1f}%)")
            print(f"     Avg Order Value: ${avg_value:.2f}")
            
            if 'payment_installments' in data.columns:
                avg_installments = data['payment_installments'].mean()
                print(f"     Avg Installments: {avg_installments:.1f}")
        
        # Installment analysis
        if 'payment_installments' in payments_df.columns:
            self._analyze_installment_patterns(payments_df)
    
    def _analyze_installment_patterns(self, payments_df):
        """Analyze installment payment patterns"""
        print("\n📊 Installment Pattern Analysis:")
        print("-" * 50)
        
        installment_analysis = payments_df.groupby('payment_installments').agg({
            'payment_value': ['count', 'sum', 'mean']
        }).round(2)
        
        for installments in sorted(payments_df['payment_installments'].unique())[:10]:  # Top 10
            data = payments_df[payments_df['payment_installments'] == installments]
            count = len(data)
            revenue = data['payment_value'].sum()
            avg_value = data['payment_value'].mean()
            
            print(f"   {installments} installments: {count} orders, ${revenue:.0f} revenue, ${avg_value:.2f} AOV")
    
    def generate_comprehensive_insights(self, rfm_df, cohort_df, ltv_df, payments_df):
        """Generate comprehensive business insights with actionable recommendations"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BUSINESS INSIGHTS & RECOMMENDATIONS")
        print("=" * 80)
        
        # Key findings
        print("\n📈 KEY FINDINGS:")
        print("-" * 40)
        
        # Revenue concentration
        champions_revenue = rfm_df[rfm_df['segment'] == 'Champions']['monetary'].sum()
        total_revenue = rfm_df['monetary'].sum()
        champions_pct = len(rfm_df[rfm_df['segment'] == 'Champions']) / len(rfm_df) * 100
        
        print(f"1. Revenue Concentration:")
        print(f"   • {champions_pct:.1f}% of customers (Champions) generate {champions_revenue/total_revenue*100:.1f}% of revenue")
        print(f"   • Top-heavy customer base indicates strong brand loyalty among high-value segments")
        
        # Retention opportunities
        at_risk_count = len(rfm_df[rfm_df['segment'] == 'At Risk'])
        lost_count = len(rfm_df[rfm_df['segment'] == 'Lost'])
        
        print(f"\n2. Customer Retention:")
        print(f"   • {at_risk_count + lost_count} customers ({(at_risk_count + lost_count)/len(rfm_df)*100:.1f}%) are at risk or lost")
        print(f"   • Significant win-back opportunity worth ${rfm_df[rfm_df['segment'].isin(['At Risk', 'Lost'])]['monetary'].sum():.0f}")
        
        # Growth opportunities
        regular_count = len(rfm_df[rfm_df['segment'] == 'Regular'])
        print(f"\n3. Growth Potential:")
        print(f"   • {regular_count} Regular customers ({regular_count/len(rfm_df)*100:.1f}%) can be upgraded")
        print(f"   • Average uplift potential: ${rfm_df[rfm_df['segment'] == 'Champions']['monetary'].mean() - rfm_df[rfm_df['segment'] == 'Regular']['monetary'].mean():.2f} per customer")
        
        # Strategic recommendations
        print("\n🎯 STRATEGIC RECOMMENDATIONS:")
        print("-" * 40)
        print("1. IMMEDIATE ACTIONS (Next 30 days):")
        print("   • Launch win-back campaign for At Risk customers")
        print("   • Implement loyalty program for Champions")
        print("   • A/B test retention strategies for month-2 cohorts")
        
        print("\n2. MEDIUM-TERM INITIATIVES (Next 90 days):")
        print("   • Develop customer upgrade paths from Regular to Loyal")
        print("   • Implement predictive churn models")
        print("   • Optimize payment methods and installment options")
        
        print("\n3. LONG-TERM STRATEGY (Next 12 months):")
        print("   • Build customer success program")
        print("   • Develop personalization engine")
        print("   • Implement advanced attribution modeling")
        
        # ROI projections
        print("\n💰 PROJECTED ROI IMPACT:")
        print("-" * 40)
        at_risk_value = rfm_df[rfm_df['segment'] == 'At Risk']['monetary'].sum()
        print(f"   • Win-back 25% of At Risk customers: +${at_risk_value * 0.25:.0f} revenue")
        print(f"   • Upgrade 10% of Regular customers: +${(rfm_df[rfm_df['segment'] == 'Champions']['monetary'].mean() - rfm_df[rfm_df['segment'] == 'Regular']['monetary'].mean()) * regular_count * 0.1:.0f} revenue")
        print(f"   • Improve retention by 5%: +${total_revenue * 0.05:.0f} revenue")
        
        total_opportunity = (at_risk_value * 0.25 + 
                           (rfm_df[rfm_df['segment'] == 'Champions']['monetary'].mean() - 
                            rfm_df[rfm_df['segment'] == 'Regular']['monetary'].mean()) * regular_count * 0.1 + 
                           total_revenue * 0.05)
        
        print(f"\n   📊 TOTAL REVENUE OPPORTUNITY: ${total_opportunity:.0f}")
        print(f"   📈 Potential Revenue Increase: {total_opportunity/total_revenue*100:.1f}%")

def run_advanced_analysis():
    """Run comprehensive advanced analysis"""
    # Load data
    orders = pd.read_csv('../data/sample_orders.csv')
    payments = pd.read_csv('../data/sample_payments.csv')
    
    # Load previous analysis results
    rfm_segments = pd.read_csv('../outputs/rfm_segments.csv')
    
    # Create cohort data
    from cohort_analysis import CohortAnalyzer
    cohort = CohortAnalyzer()
    cohort_df = cohort.create_cohorts(orders, payments)
    retention = cohort.calculate_retention(cohort_df)
    
    # Run advanced analysis
    analyzer = AdvancedAnalyzer()
    
    # Detailed breakdowns
    analyzer.detailed_rfm_breakdown(rfm_segments)
    analyzer.cohort_deep_dive(cohort_df, retention)
    ltv_analysis = analyzer.ltv_deep_analysis(rfm_segments, orders, payments)
    analyzer.payment_method_analysis(payments)
    
    # Comprehensive insights
    analyzer.generate_comprehensive_insights(rfm_segments, cohort_df, rfm_segments, payments)
    
    return analyzer

if __name__ == "__main__":
    run_advanced_analysis()