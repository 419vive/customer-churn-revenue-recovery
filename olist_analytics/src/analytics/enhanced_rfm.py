"""Enterprise-grade RFM Analysis with advanced features"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import warnings

from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import AnalysisError, DataValidationError
from ..core.cache import cache_dataframe
from ..data_quality.validator import DataValidator

logger = get_logger(__name__)

@dataclass
class RFMMetrics:
    """RFM analysis results with metadata"""
    segments: pd.DataFrame
    summary: pd.DataFrame
    segment_stats: Dict[str, Any]
    analysis_metadata: Dict[str, Any]
    data_quality_report: Dict[str, Any]

class EnterpriseRFMAnalyzer:
    """Production-ready RFM analyzer with enterprise features"""
    
    def __init__(self, reference_date: Optional[datetime] = None):
        self.reference_date = reference_date or datetime.now()
        self.segment_thresholds = config.analytics.segment_thresholds
        self.validator = self._setup_validator()
        
    def _setup_validator(self) -> DataValidator:
        """Setup data validation rules for RFM analysis"""
        validator = DataValidator()
        
        # Orders validation
        validator.add_not_null('customer_id', max_null_percentage=0.0)
        validator.add_not_null('order_id', max_null_percentage=0.0)
        validator.add_not_null('order_purchase_timestamp', max_null_percentage=0.0)
        validator.add_data_type('customer_id', 'string')
        validator.add_data_type('order_id', 'string')
        
        return validator
    
    @cache_dataframe(ttl=1800)  # Cache for 30 minutes
    def analyze(self, orders_df: pd.DataFrame, payments_df: pd.DataFrame, 
                validate_data: bool = True) -> RFMMetrics:
        """Complete RFM analysis with validation and error handling"""
        
        analysis_start = datetime.now()
        logger.log_analysis_start('rfm_analysis', 
                                orders_count=len(orders_df),
                                payments_count=len(payments_df),
                                reference_date=self.reference_date.isoformat())
        
        try:
            # Data validation
            data_quality_report = {}
            if validate_data:
                data_quality_report = self._validate_input_data(orders_df, payments_df)
            
            # Data preparation
            prepared_data = self._prepare_data(orders_df, payments_df)
            
            # Calculate RFM metrics
            rfm_data = self._calculate_rfm_metrics(prepared_data)
            
            # Assign scores with advanced quantile handling
            rfm_scores = self._assign_rfm_scores(rfm_data)
            
            # Create segments with business logic
            segments_df = self._create_segments(rfm_scores)
            
            # Generate summary statistics
            summary_df = self._generate_summary(segments_df)
            
            # Advanced segment analysis
            segment_stats = self._analyze_segments(segments_df)
            
            # Analysis metadata
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            metadata = {
                'analysis_date': datetime.now().isoformat(),
                'reference_date': self.reference_date.isoformat(),
                'duration_seconds': analysis_duration,
                'total_customers': len(segments_df),
                'total_revenue': segments_df['monetary'].sum(),
                'avg_recency_days': segments_df['recency'].mean(),
                'avg_frequency': segments_df['frequency'].mean(),
                'version': '2.0.0'
            }
            
            logger.log_analysis_complete('rfm_analysis', analysis_duration, len(segments_df),
                                      segments=len(segments_df['segment'].unique()),
                                      total_revenue=segments_df['monetary'].sum())
            
            return RFMMetrics(
                segments=segments_df,
                summary=summary_df,
                segment_stats=segment_stats,
                analysis_metadata=metadata,
                data_quality_report=data_quality_report
            )
            
        except Exception as e:
            logger.logger.error(f"RFM analysis failed: {str(e)}", exc_info=True)
            raise AnalysisError(
                f"RFM analysis failed: {str(e)}",
                error_code='RFM_ANALYSIS_FAILED',
                details={
                    'orders_shape': orders_df.shape,
                    'payments_shape': payments_df.shape,
                    'reference_date': self.reference_date.isoformat()
                }
            )
    
    def _validate_input_data(self, orders_df: pd.DataFrame, payments_df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data validation"""
        logger.logger.info("Starting data validation for RFM analysis")
        
        validation_results = {
            'orders_validation': self.validator.validate(orders_df),
            'payments_validation': self.validator.validate(payments_df)
        }
        
        # Additional business logic validations
        business_checks = {
            'orders_payments_join': self._validate_join_integrity(orders_df, payments_df),
            'date_range_check': self._validate_date_ranges(orders_df),
            'monetary_values': self._validate_monetary_values(payments_df)
        }
        
        return {
            'validation_results': validation_results,
            'business_checks': business_checks,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _validate_join_integrity(self, orders_df: pd.DataFrame, payments_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate orders and payments can be joined properly"""
        orders_ids = set(orders_df['order_id'].unique())
        payments_ids = set(payments_df['order_id'].unique())
        
        intersection = orders_ids & payments_ids
        orders_only = orders_ids - payments_ids
        payments_only = payments_ids - orders_ids
        
        join_ratio = len(intersection) / len(orders_ids) if orders_ids else 0
        
        return {
            'orders_with_payments': len(intersection),
            'orders_without_payments': len(orders_only),
            'payments_without_orders': len(payments_only),
            'join_success_ratio': join_ratio,
            'is_acceptable': join_ratio >= 0.95  # 95% join success threshold
        }
    
    def _validate_date_ranges(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate order date ranges make business sense"""
        orders_df = orders_df.copy()
        orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
        
        min_date = orders_df['order_purchase_timestamp'].min()
        max_date = orders_df['order_purchase_timestamp'].max()
        date_span_days = (max_date - min_date).days
        
        future_orders = orders_df['order_purchase_timestamp'] > datetime.now()
        
        return {
            'min_order_date': min_date.isoformat(),
            'max_order_date': max_date.isoformat(),
            'date_span_days': date_span_days,
            'future_orders_count': future_orders.sum(),
            'is_reasonable_span': 1 <= date_span_days <= 3650  # 1 day to 10 years
        }
    
    def _validate_monetary_values(self, payments_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate payment amounts are reasonable"""
        negative_payments = payments_df['payment_value'] < 0
        zero_payments = payments_df['payment_value'] == 0
        extreme_payments = payments_df['payment_value'] > 100000  # $100k threshold
        
        return {
            'negative_payments': negative_payments.sum(),
            'zero_payments': zero_payments.sum(),
            'extreme_payments': extreme_payments.sum(),
            'min_payment': payments_df['payment_value'].min(),
            'max_payment': payments_df['payment_value'].max(),
            'avg_payment': payments_df['payment_value'].mean()
        }
    
    def _prepare_data(self, orders_df: pd.DataFrame, payments_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean data for RFM analysis"""
        logger.logger.info("Preparing data for RFM analysis")
        
        # Merge orders and payments
        merged_df = orders_df.merge(payments_df, on='order_id', how='inner')
        
        # Convert and validate dates
        merged_df['order_date'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
        
        # Remove future orders (data quality issue)
        future_mask = merged_df['order_date'] > datetime.now()
        if future_mask.any():
            logger.log_data_quality_issue(
                'future_orders',
                'warning',
                {'count': future_mask.sum()}
            )
            merged_df = merged_df[~future_mask]
        
        # Remove negative or zero payments (business logic)
        invalid_payments = merged_df['payment_value'] <= 0
        if invalid_payments.any():
            logger.log_data_quality_issue(
                'invalid_payments',
                'warning',
                {'count': invalid_payments.sum()}
            )
            merged_df = merged_df[~invalid_payments]
        
        logger.logger.info(f"Data prepared: {len(merged_df)} records")
        return merged_df
    
    def _calculate_rfm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM metrics with robust handling"""
        logger.logger.info("Calculating RFM metrics")
        
        rfm = df.groupby('customer_id').agg({
            'order_date': lambda x: (self.reference_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency  
            'payment_value': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Add additional metrics
        customer_details = df.groupby('customer_id').agg({
            'order_date': ['min', 'max'],
            'payment_value': ['mean', 'std'],
            'order_id': 'nunique'
        }).reset_index()
        
        customer_details.columns = ['customer_id', 'first_order', 'last_order', 
                                  'avg_order_value', 'order_value_std', 'unique_orders']
        
        # Calculate customer lifetime span
        customer_details['lifetime_days'] = (
            customer_details['last_order'] - customer_details['first_order']
        ).dt.days + 1
        
        # Merge additional metrics
        rfm = rfm.merge(customer_details[['customer_id', 'first_order', 'last_order', 
                                        'avg_order_value', 'lifetime_days']], 
                       on='customer_id')
        
        return rfm
    
    def _assign_rfm_scores(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """Advanced RFM scoring with quantile-based approach"""
        logger.logger.info("Assigning RFM scores")
        
        rfm = rfm_df.copy()
        
        # Handle edge cases for small datasets
        n_customers = len(rfm)
        n_bins = min(5, max(2, n_customers // 20))  # Adaptive binning
        
        try:
            # Recency scoring (lower recency = higher score)
            rfm['r_score'] = pd.qcut(
                rfm['recency'], 
                q=n_bins, 
                labels=list(range(n_bins, 0, -1)), 
                duplicates='drop'
            )
            
            # Frequency scoring (higher frequency = higher score)
            rfm['f_score'] = pd.qcut(
                rfm['frequency'].rank(method='first'), 
                q=n_bins, 
                labels=list(range(1, n_bins + 1)), 
                duplicates='drop'
            )
            
            # Monetary scoring (higher monetary = higher score)
            rfm['m_score'] = pd.qcut(
                rfm['monetary'], 
                q=n_bins, 
                labels=list(range(1, n_bins + 1)), 
                duplicates='drop'
            )
            
        except ValueError as e:
            # Fallback to simple binning for difficult distributions
            logger.logger.warning(f"Quantile-based scoring failed, using rank-based approach: {str(e)}")
            
            rfm['r_score'] = pd.cut(
                rfm['recency'].rank(method='first'), 
                bins=n_bins, 
                labels=list(range(n_bins, 0, -1))
            ).fillna(3)
            
            rfm['f_score'] = pd.cut(
                rfm['frequency'].rank(method='first'), 
                bins=n_bins, 
                labels=list(range(1, n_bins + 1))
            ).fillna(3)
            
            rfm['m_score'] = pd.cut(
                rfm['monetary'].rank(method='first'), 
                bins=n_bins, 
                labels=list(range(1, n_bins + 1))
            ).fillna(3)
        
        # Convert to numeric and ensure valid range
        for score_col in ['r_score', 'f_score', 'm_score']:
            rfm[score_col] = pd.to_numeric(rfm[score_col], errors='coerce').fillna(3).clip(1, n_bins)
        
        # Create composite RFM score
        rfm['rfm_score'] = (
            rfm['r_score'].astype(int).astype(str) + 
            rfm['f_score'].astype(int).astype(str) + 
            rfm['m_score'].astype(int).astype(str)
        )
        
        return rfm
    
    def _create_segments(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """Create customer segments with advanced business logic"""
        logger.logger.info("Creating customer segments")
        
        rfm = rfm_df.copy()
        
        def segment_customers(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            
            # Champions: High R, F, M
            if r >= self.segment_thresholds.get('champion_r_min', 4) and \
               f >= self.segment_thresholds.get('champion_f_min', 4) and \
               m >= self.segment_thresholds.get('champion_m_min', 4):
                return 'Champions'
            
            # Loyal Customers: High R, F but lower M
            elif r >= 4 and f >= 4:
                return 'Loyal Customers'
            
            # Potential Loyalists: High R, lower F
            elif r >= 4 and f >= 2:
                return 'Potential Loyalists'
            
            # New Customers: High R, low F
            elif r >= 4 and f == 1:
                return 'New Customers'
            
            # Promising: Medium R, F
            elif r >= 3 and f >= 2:
                return 'Promising'
            
            # Need Attention: Medium R, low F, high M
            elif r >= 3 and f == 1 and m >= 4:
                return 'Need Attention'
            
            # At Risk: Low R, high F, M (used to be good)
            elif r <= self.segment_thresholds.get('at_risk_r_max', 2) and f >= 3:
                return 'At Risk'
            
            # Cannot Lose Them: Very low R but high F, M
            elif r == 1 and f >= 4 and m >= 4:
                return 'Cannot Lose Them'
            
            # Lost: Very low R
            elif r <= self.segment_thresholds.get('lost_r_max', 1):
                return 'Lost'
            
            # Others
            else:
                return 'Others'
        
        rfm['segment'] = rfm.apply(segment_customers, axis=1)
        
        # Add segment priority for business actions
        segment_priority = {
            'Champions': 1,
            'Loyal Customers': 2,
            'Cannot Lose Them': 3,
            'At Risk': 4,
            'New Customers': 5,
            'Potential Loyalists': 6,
            'Need Attention': 7,
            'Promising': 8,
            'Others': 9,
            'Lost': 10
        }
        
        rfm['segment_priority'] = rfm['segment'].map(segment_priority)
        
        return rfm
    
    def _generate_summary(self, segments_df: pd.DataFrame) -> pd.DataFrame:
        """Generate comprehensive segment summary"""
        logger.logger.info("Generating segment summary")
        
        summary = segments_df.groupby('segment').agg({
            'customer_id': 'count',
            'recency': ['mean', 'median'],
            'frequency': ['mean', 'median'],
            'monetary': ['mean', 'median', 'sum'],
            'avg_order_value': 'mean',
            'lifetime_days': 'mean'
        }).round(2)
        
        # Flatten column names
        summary.columns = [
            'customer_count', 'avg_recency', 'median_recency',
            'avg_frequency', 'median_frequency', 'avg_monetary', 'median_monetary',
            'total_revenue', 'avg_order_value', 'avg_lifetime_days'
        ]
        
        # Add percentages
        total_customers = summary['customer_count'].sum()
        total_revenue = summary['total_revenue'].sum()
        
        summary['customer_percentage'] = (summary['customer_count'] / total_customers * 100).round(1)
        summary['revenue_percentage'] = (summary['total_revenue'] / total_revenue * 100).round(1)
        
        # Add business value metrics
        summary['revenue_per_customer'] = (summary['total_revenue'] / summary['customer_count']).round(2)
        summary['value_concentration'] = (summary['revenue_percentage'] / summary['customer_percentage']).round(2)
        
        return summary.reset_index()
    
    def _analyze_segments(self, segments_df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced segment analysis with business insights"""
        logger.logger.info("Analyzing segments for business insights")
        
        segment_stats = {
            'total_customers': len(segments_df),
            'total_revenue': segments_df['monetary'].sum(),
            'segments': {}
        }
        
        for segment in segments_df['segment'].unique():
            segment_data = segments_df[segments_df['segment'] == segment]
            
            segment_stats['segments'][segment] = {
                'count': len(segment_data),
                'percentage': len(segment_data) / len(segments_df) * 100,
                'revenue': segment_data['monetary'].sum(),
                'revenue_percentage': segment_data['monetary'].sum() / segments_df['monetary'].sum() * 100,
                'avg_ltv': segment_data['monetary'].mean(),
                'avg_recency': segment_data['recency'].mean(),
                'avg_frequency': segment_data['frequency'].mean(),
                'top_percentile_ltv': np.percentile(segment_data['monetary'], 90),
                'churn_risk': 'High' if segment in ['At Risk', 'Cannot Lose Them', 'Lost'] else 'Low'
            }
        
        # Calculate concentration metrics
        segment_stats['pareto_analysis'] = self._calculate_pareto_distribution(segments_df)
        
        return segment_stats
    
    def _calculate_pareto_distribution(self, segments_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Pareto distribution (80/20 rule) metrics"""
        sorted_customers = segments_df.sort_values('monetary', ascending=False)
        cumulative_revenue = sorted_customers['monetary'].cumsum()
        total_revenue = sorted_customers['monetary'].sum()
        
        # Find percentage of customers that generate 80% of revenue
        customers_for_80_revenue = (cumulative_revenue <= total_revenue * 0.8).sum()
        percentage_for_80_revenue = customers_for_80_revenue / len(sorted_customers) * 100
        
        # Find revenue generated by top 20% of customers
        top_20_customers = int(len(sorted_customers) * 0.2)
        revenue_from_top_20 = cumulative_revenue.iloc[top_20_customers - 1] / total_revenue * 100
        
        return {
            'customers_for_80_revenue_pct': percentage_for_80_revenue,
            'revenue_from_top_20_customers_pct': revenue_from_top_20,
            'pareto_efficiency': revenue_from_top_20 / 20  # Should be > 4 for good concentration
        }
    
    def generate_recommendations(self, rfm_metrics: RFMMetrics) -> Dict[str, List[str]]:
        """Generate actionable business recommendations based on RFM analysis"""
        recommendations = {}
        
        for segment, stats in rfm_metrics.segment_stats['segments'].items():
            segment_recommendations = []
            
            if segment == 'Champions':
                segment_recommendations.extend([
                    "Reward with loyalty programs and exclusive offers",
                    "Use for referral programs and testimonials",
                    "Provide excellent customer service to retain",
                    "Offer early access to new products"
                ])
            elif segment == 'At Risk':
                segment_recommendations.extend([
                    "Launch win-back campaigns with personalized offers",
                    "Conduct satisfaction surveys to identify issues",
                    "Provide limited-time discounts to re-engage",
                    "Implement retention campaigns"
                ])
            elif segment == 'Lost':
                segment_recommendations.extend([
                    "Run aggressive win-back campaigns",
                    "Offer significant discounts or incentives",
                    "Research reasons for churn",
                    "Consider remarketing campaigns"
                ])
            elif segment == 'New Customers':
                segment_recommendations.extend([
                    "Focus on onboarding and education",
                    "Provide excellent first experience",
                    "Implement nurture campaigns",
                    "Offer second-purchase incentives"
                ])
            
            if segment_recommendations:
                recommendations[segment] = segment_recommendations
        
        return recommendations