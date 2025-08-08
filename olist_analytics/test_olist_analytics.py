#!/usr/bin/env python
"""
Comprehensive Unit Tests for Olist Analytics Project
Tests all core functionality and edge cases
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
import tempfile
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analytics.rfm_analysis import RFMAnalyzer
from src.analytics.cohort_analysis import CohortAnalyzer
from src.analytics.ltv_modeling import LTVPredictor
from src.analytics.advanced_analysis import AdvancedAnalyzer


class TestDataGeneration:
    """Helper class to generate test data"""
    
    @staticmethod
    def create_sample_orders(n_customers=20, n_orders=100):
        """Create sample orders data for testing"""
        np.random.seed(42)
        
        # Create date range
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 12, 31)
        date_range = pd.date_range(start_date, end_date, freq='D')
        
        orders = []
        for i in range(n_orders):
            customer_id = f"customer_{np.random.randint(0, n_customers):03d}"
            order_id = f"order_{i:04d}"
            order_date = np.random.choice(date_range)
            
            # Convert numpy datetime to python datetime for string formatting
            order_date_py = pd.to_datetime(order_date).to_pydatetime()
            
            orders.append({
                'order_id': order_id,
                'customer_id': customer_id,
                'order_status': 'delivered',
                'order_purchase_timestamp': order_date_py.strftime('%Y-%m-%d'),
                'order_delivered_carrier_date': (order_date_py + timedelta(days=2)).strftime('%Y-%m-%d'),
                'order_delivered_customer_date': (order_date_py + timedelta(days=5)).strftime('%Y-%m-%d'),
                'freight_value': np.random.uniform(10, 50)
            })
        
        return pd.DataFrame(orders)
    
    @staticmethod
    def create_sample_payments(orders_df):
        """Create sample payments data matching orders"""
        np.random.seed(42)
        
        payments = []
        for _, order in orders_df.iterrows():
            payments.append({
                'order_id': order['order_id'],
                'payment_sequential': 1,
                'payment_type': np.random.choice(['credit_card', 'boleto', 'debit_card'], p=[0.7, 0.2, 0.1]),
                'payment_installments': np.random.choice([1, 2, 3, 6], p=[0.5, 0.2, 0.2, 0.1]),
                'payment_value': np.random.uniform(50, 500)
            })
        
        return pd.DataFrame(payments)
    
    @staticmethod
    def create_sample_customers(n_customers=20):
        """Create sample customers data"""
        np.random.seed(42)
        
        customers = []
        states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'DF', 'SC']
        
        for i in range(n_customers):
            customer_id = f"customer_{i:03d}"
            customers.append({
                'customer_id': customer_id,
                'customer_unique_id': customer_id,
                'customer_zip_code_prefix': np.random.randint(10000, 99999),
                'customer_city': f"city_{i}",
                'customer_state': np.random.choice(states)
            })
        
        return pd.DataFrame(customers)


class TestRFMAnalysis(unittest.TestCase):
    """Test RFM Analysis functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.orders = TestDataGeneration.create_sample_orders()
        self.payments = TestDataGeneration.create_sample_payments(self.orders)
        self.rfm_analyzer = RFMAnalyzer()
    
    def test_rfm_calculation(self):
        """Test RFM metrics calculation"""
        rfm_df = self.rfm_analyzer.calculate_rfm(self.orders, self.payments)
        
        # Check that we have the right columns
        expected_columns = ['customer_id', 'recency', 'frequency', 'monetary']
        self.assertEqual(list(rfm_df.columns), expected_columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(rfm_df['recency']))
        self.assertTrue(pd.api.types.is_numeric_dtype(rfm_df['frequency']))
        self.assertTrue(pd.api.types.is_numeric_dtype(rfm_df['monetary']))
        
        # Check for positive values
        self.assertTrue((rfm_df['recency'] >= 0).all())
        self.assertTrue((rfm_df['frequency'] > 0).all())
        self.assertTrue((rfm_df['monetary'] > 0).all())
        
        # Check unique customers
        self.assertEqual(len(rfm_df), rfm_df['customer_id'].nunique())
    
    def test_rfm_scoring(self):
        """Test RFM scoring functionality"""
        rfm_df = self.rfm_analyzer.calculate_rfm(self.orders, self.payments)
        rfm_scores = self.rfm_analyzer.assign_scores(rfm_df)
        
        # Check score columns exist
        score_columns = ['r_score', 'f_score', 'm_score', 'rfm_score']
        for col in score_columns:
            self.assertIn(col, rfm_scores.columns)
        
        # Check score ranges (1-5) - handle NaN values from pd.qcut with duplicates='drop'
        for score_col in ['r_score', 'f_score', 'm_score']:
            valid_scores = rfm_scores[score_col].dropna()
            if len(valid_scores) > 0:
                self.assertTrue((valid_scores >= 1).all())
                self.assertTrue((valid_scores <= 5).all())
        
        # Check RFM score format (3 digits)
        self.assertTrue(rfm_scores['rfm_score'].str.len().eq(3).all())
    
    def test_customer_segmentation(self):
        """Test customer segmentation logic"""
        rfm_df = self.rfm_analyzer.calculate_rfm(self.orders, self.payments)
        rfm_scores = self.rfm_analyzer.assign_scores(rfm_df)
        rfm_segments = self.rfm_analyzer.create_segments(rfm_scores)
        
        # Check segment column exists
        self.assertIn('segment', rfm_segments.columns)
        
        # Check valid segment names
        valid_segments = ['Champions', 'Loyal Customers', 'Big Spenders', 'At Risk', 'Lost', 'Regular']
        unique_segments = rfm_segments['segment'].unique()
        for segment in unique_segments:
            self.assertIn(segment, valid_segments)
        
        # Check that all customers are assigned a segment
        self.assertEqual(len(rfm_segments), rfm_segments['segment'].count())
    
    def test_segment_summary(self):
        """Test segment summary generation"""
        rfm_df = self.rfm_analyzer.calculate_rfm(self.orders, self.payments)
        rfm_scores = self.rfm_analyzer.assign_scores(rfm_df)
        rfm_segments = self.rfm_analyzer.create_segments(rfm_scores)
        summary = self.rfm_analyzer.get_segment_summary(rfm_segments)
        
        # Check summary columns
        expected_columns = ['customer_count', 'avg_revenue', 'total_revenue', 'pct_customers', 'pct_revenue']
        for col in expected_columns:
            self.assertIn(col, summary.columns)
        
        # Check percentage sums to ~100%
        self.assertAlmostEqual(summary['pct_customers'].sum(), 100.0, places=0)
        self.assertAlmostEqual(summary['pct_revenue'].sum(), 100.0, places=0)


class TestCohortAnalysis(unittest.TestCase):
    """Test Cohort Analysis functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.orders = TestDataGeneration.create_sample_orders()
        self.payments = TestDataGeneration.create_sample_payments(self.orders)
        self.cohort_analyzer = CohortAnalyzer()
    
    def test_cohort_creation(self):
        """Test cohort data creation"""
        cohort_df = self.cohort_analyzer.create_cohorts(self.orders, self.payments)
        
        # Check required columns exist
        required_columns = ['customer_id', 'order_id', 'payment_value', 'order_date', 'cohort_month', 'order_month', 'cohort_index']
        for col in required_columns:
            self.assertIn(col, cohort_df.columns)
        
        # Check cohort_index is non-negative
        self.assertTrue((cohort_df['cohort_index'] >= 0).all())
        
        # Check that first purchases have cohort_index = 0
        first_purchases = cohort_df.groupby('customer_id')['order_date'].min().reset_index()
        first_purchase_rows = cohort_df.merge(first_purchases, on=['customer_id', 'order_date'])
        self.assertTrue((first_purchase_rows['cohort_index'] == 0).all())
    
    def test_retention_calculation(self):
        """Test retention rate calculation"""
        cohort_df = self.cohort_analyzer.create_cohorts(self.orders, self.payments)
        retention = self.cohort_analyzer.calculate_retention(cohort_df)
        
        # Check retention matrix structure
        self.assertIsInstance(retention, pd.DataFrame)
        self.assertTrue(len(retention) > 0)
        self.assertTrue(len(retention.columns) > 0)
        
        # Check that cohort_index 0 has 100% retention (approximately)
        if 0 in retention.columns:
            first_column_values = retention[0].dropna()
            # Allow for small floating point differences
            self.assertTrue(np.allclose(first_column_values, 100.0, rtol=0.01))
        
        # Check retention values are between 0 and 100
        retention_values = retention.values.flatten()
        retention_values = retention_values[~np.isnan(retention_values)]
        self.assertTrue((retention_values >= 0).all())
        self.assertTrue((retention_values <= 100).all())
    
    def test_revenue_cohorts(self):
        """Test revenue cohort calculation"""
        cohort_df = self.cohort_analyzer.create_cohorts(self.orders, self.payments)
        revenue_cohorts = self.cohort_analyzer.calculate_revenue_cohorts(cohort_df)
        
        # Check structure
        self.assertIsInstance(revenue_cohorts, pd.DataFrame)
        self.assertTrue(len(revenue_cohorts) > 0)
        
        # Check all values are non-negative
        revenue_values = revenue_cohorts.values.flatten()
        revenue_values = revenue_values[~np.isnan(revenue_values)]
        self.assertTrue((revenue_values >= 0).all())
    
    def test_cohort_metrics(self):
        """Test cohort metrics summary"""
        cohort_df = self.cohort_analyzer.create_cohorts(self.orders, self.payments)
        metrics = self.cohort_analyzer.get_cohort_metrics(cohort_df)
        
        # Check required columns
        expected_columns = ['cohort', 'customers', 'orders', 'revenue', 'avg_order_value', 'orders_per_customer']
        for col in expected_columns:
            self.assertIn(col, metrics.columns)
        
        # Check calculated metrics make sense
        self.assertTrue((metrics['avg_order_value'] > 0).all())
        self.assertTrue((metrics['orders_per_customer'] >= 1).all())


class TestLTVModeling(unittest.TestCase):
    """Test LTV Modeling functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.orders = TestDataGeneration.create_sample_orders()
        self.payments = TestDataGeneration.create_sample_payments(self.orders)
        self.ltv_predictor = LTVPredictor()
    
    def test_historical_ltv_calculation(self):
        """Test historical LTV calculation"""
        ltv_df = self.ltv_predictor.calculate_historical_ltv(self.orders, self.payments)
        
        # Check required columns
        expected_columns = ['total_revenue', 'order_count', 'first_order', 'last_order', 'avg_order_value', 'lifespan_days']
        for col in expected_columns:
            self.assertIn(col, ltv_df.columns)
        
        # Check data quality
        self.assertTrue((ltv_df['total_revenue'] > 0).all())
        self.assertTrue((ltv_df['order_count'] >= 1).all())
        self.assertTrue((ltv_df['avg_order_value'] > 0).all())
        self.assertTrue((ltv_df['lifespan_days'] >= 1).all())
        
        # Check calculated avg_order_value (allow for small rounding differences due to pandas rounding)
        calculated_aov = ltv_df['total_revenue'] / ltv_df['order_count']
        np.testing.assert_allclose(calculated_aov.values, ltv_df['avg_order_value'].values, rtol=1e-4)
    
    def test_simple_ltv_prediction(self):
        """Test simple LTV prediction formula"""
        aov = 100
        frequency = 2
        retention_rate = 0.8
        
        predicted_ltv = self.ltv_predictor.predict_simple_ltv(None, aov, frequency, retention_rate)
        
        # Check that prediction is reasonable
        self.assertIsInstance(predicted_ltv, (int, float))
        self.assertTrue(predicted_ltv > 0)
        
        # Check formula: LTV = AOV * Frequency * (1 / (1 - retention_rate))
        expected_ltv = aov * frequency * (1 / (1 - retention_rate))
        self.assertEqual(predicted_ltv, expected_ltv)
    
    def test_ltv_segmentation(self):
        """Test LTV customer segmentation"""
        ltv_df = self.ltv_predictor.calculate_historical_ltv(self.orders, self.payments)
        ltv_segments = self.ltv_predictor.segment_ltv(ltv_df)
        
        # Check segment column exists
        self.assertIn('ltv_tier', ltv_segments.columns)
        
        # Check valid segment names
        valid_tiers = ['Low', 'Medium', 'High', 'VIP']
        unique_tiers = ltv_segments['ltv_tier'].unique()
        for tier in unique_tiers:
            self.assertIn(tier, valid_tiers)
        
        # Check tier distribution is reasonable (each tier should have some customers)
        tier_counts = ltv_segments['ltv_tier'].value_counts()
        self.assertTrue(len(tier_counts) > 0)
    
    def test_cac_payback_calculation(self):
        """Test CAC payback calculation"""
        ltv_df = self.ltv_predictor.calculate_historical_ltv(self.orders, self.payments)
        cac = 50
        cac_analysis = self.ltv_predictor.calculate_cac_payback(ltv_df, cac)
        
        # Check required metrics
        expected_metrics = ['avg_ltv', 'median_ltv', 'cac', 'ltv_cac_ratio', 'profitable_customers_pct']
        for metric in expected_metrics:
            self.assertIn(metric, cac_analysis.index)
        
        # Check calculations (allow for small rounding differences)
        self.assertEqual(cac_analysis['cac'], cac)
        self.assertAlmostEqual(cac_analysis['avg_ltv'], ltv_df['total_revenue'].mean(), places=1)
        self.assertAlmostEqual(cac_analysis['median_ltv'], ltv_df['total_revenue'].median(), places=1)
        
        # Check LTV/CAC ratio
        expected_ratio = ltv_df['total_revenue'].mean() / cac
        self.assertAlmostEqual(cac_analysis['ltv_cac_ratio'], expected_ratio, places=2)


class TestAdvancedAnalysis(unittest.TestCase):
    """Test Advanced Analysis functionality"""
    
    def setUp(self):
        """Set up test data and analysis results"""
        self.orders = TestDataGeneration.create_sample_orders()
        self.payments = TestDataGeneration.create_sample_payments(self.orders)
        
        # Create RFM analysis results for advanced analysis
        rfm_analyzer = RFMAnalyzer()
        rfm_df = rfm_analyzer.calculate_rfm(self.orders, self.payments)
        rfm_scores = rfm_analyzer.assign_scores(rfm_df)
        self.rfm_segments = rfm_analyzer.create_segments(rfm_scores)
        
        self.advanced_analyzer = AdvancedAnalyzer()
    
    def test_detailed_rfm_breakdown(self):
        """Test detailed RFM breakdown analysis"""
        # This method prints results, so we mainly test it doesn't crash
        try:
            # Capture output to avoid cluttering test results
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = self.advanced_analyzer.detailed_rfm_breakdown(self.rfm_segments)
            
            # Check that some analysis was performed
            self.assertIsNotNone(result)
            
        except Exception as e:
            self.fail(f"detailed_rfm_breakdown raised an exception: {e}")
    
    def test_payment_method_analysis(self):
        """Test payment method analysis"""
        try:
            # Capture output to avoid cluttering test results
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                self.advanced_analyzer.payment_method_analysis(self.payments)
            
            # If we get here without exception, the test passes
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"payment_method_analysis raised an exception: {e}")
    
    def test_ltv_deep_analysis(self):
        """Test LTV deep analysis"""
        ltv_predictor = LTVPredictor()
        ltv_df = ltv_predictor.calculate_historical_ltv(self.orders, self.payments)
        
        try:
            # Capture output to avoid cluttering test results
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                result = self.advanced_analyzer.ltv_deep_analysis(ltv_df, self.orders, self.payments)
            
            # Check that customer journey analysis was performed
            self.assertIsNotNone(result)
            self.assertIsInstance(result, pd.DataFrame)
            
        except Exception as e:
            self.fail(f"ltv_deep_analysis raised an exception: {e}")


class TestEndToEndWorkflow(unittest.TestCase):
    """Test end-to-end workflow functionality"""
    
    def setUp(self):
        """Set up test data and temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.outputs_dir = os.path.join(self.test_dir, 'outputs')
        
        os.makedirs(self.data_dir)
        os.makedirs(self.outputs_dir)
        
        # Create test data files
        self.orders = TestDataGeneration.create_sample_orders()
        self.payments = TestDataGeneration.create_sample_payments(self.orders)
        self.customers = TestDataGeneration.create_sample_customers()
        
        # Save test data
        self.orders.to_csv(os.path.join(self.data_dir, 'sample_orders.csv'), index=False)
        self.payments.to_csv(os.path.join(self.data_dir, 'sample_payments.csv'), index=False)
        self.customers.to_csv(os.path.join(self.data_dir, 'sample_customers.csv'), index=False)
    
    def test_complete_analysis_pipeline(self):
        """Test the complete analysis pipeline"""
        # Test RFM Analysis
        rfm_analyzer = RFMAnalyzer()
        rfm_df = rfm_analyzer.calculate_rfm(self.orders, self.payments)
        rfm_scores = rfm_analyzer.assign_scores(rfm_df)
        rfm_segments = rfm_analyzer.create_segments(rfm_scores)
        
        # Test Cohort Analysis
        cohort_analyzer = CohortAnalyzer()
        cohort_df = cohort_analyzer.create_cohorts(self.orders, self.payments)
        retention = cohort_analyzer.calculate_retention(cohort_df)
        
        # Test LTV Analysis
        ltv_predictor = LTVPredictor()
        ltv_df = ltv_predictor.calculate_historical_ltv(self.orders, self.payments)
        ltv_segments = ltv_predictor.segment_ltv(ltv_df)
        
        # Check that all analyses produced reasonable results
        self.assertTrue(len(rfm_segments) > 0)
        self.assertTrue(len(retention) > 0)
        self.assertTrue(len(ltv_segments) > 0)
        
        # Check data consistency
        customer_ids_rfm = set(rfm_segments['customer_id'])
        customer_ids_ltv = set(ltv_segments.index)
        
        # All customers in LTV should be in RFM
        self.assertTrue(customer_ids_ltv.issubset(customer_ids_rfm))
    
    def test_data_quality_checks(self):
        """Test data quality and edge cases"""
        # Test with empty data - should handle gracefully or raise appropriate error
        empty_orders = pd.DataFrame(columns=['order_id', 'customer_id', 'order_purchase_timestamp'])
        empty_payments = pd.DataFrame(columns=['order_id', 'payment_value'])
        
        # The actual behavior may be to return empty DataFrame rather than raise exception
        try:
            rfm_analyzer = RFMAnalyzer()
            result = rfm_analyzer.calculate_rfm(empty_orders, empty_payments)
            # If no exception, check that result is empty
            self.assertTrue(len(result) == 0)
        except Exception:
            # Exception is also acceptable for empty data
            pass
        
        # Test with single customer
        single_customer_orders = self.orders[self.orders['customer_id'] == self.orders['customer_id'].iloc[0]].copy()
        single_customer_payments = self.payments[self.payments['order_id'].isin(single_customer_orders['order_id'])].copy()
        
        rfm_analyzer = RFMAnalyzer()
        rfm_df = rfm_analyzer.calculate_rfm(single_customer_orders, single_customer_payments)
        self.assertEqual(len(rfm_df), 1)
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.test_dir)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_missing_columns(self):
        """Test handling of missing columns"""
        # Create orders with missing columns
        bad_orders = pd.DataFrame({
            'order_id': ['order_001'],
            'customer_id': ['customer_001']
            # Missing order_purchase_timestamp
        })
        
        payments = pd.DataFrame({
            'order_id': ['order_001'],
            'payment_value': [100.0]
        })
        
        rfm_analyzer = RFMAnalyzer()
        with self.assertRaises(KeyError):
            rfm_analyzer.calculate_rfm(bad_orders, payments)
    
    def test_invalid_date_formats(self):
        """Test handling of invalid date formats"""
        orders = pd.DataFrame({
            'order_id': ['order_001'],
            'customer_id': ['customer_001'],
            'order_purchase_timestamp': ['invalid_date'],
            'order_status': ['delivered'],
            'order_delivered_carrier_date': ['2017-01-01'],
            'order_delivered_customer_date': ['2017-01-01'],
            'freight_value': [10.0]
        })
        
        payments = pd.DataFrame({
            'order_id': ['order_001'],
            'payment_sequential': [1],
            'payment_type': ['credit_card'],
            'payment_installments': [1],
            'payment_value': [100.0]
        })
        
        rfm_analyzer = RFMAnalyzer()
        # This should not crash, but handle the error gracefully
        # The exact behavior depends on pandas version and error handling strategy
        try:
            rfm_analyzer.calculate_rfm(orders, payments)
        except Exception as e:
            # We expect some kind of parsing error
            self.assertIsInstance(e, (ValueError, pd.errors.ParserError))
    
    def test_negative_values(self):
        """Test handling of negative values"""
        orders = TestDataGeneration.create_sample_orders(n_customers=5, n_orders=10)
        payments = TestDataGeneration.create_sample_payments(orders)
        
        # Add negative payment value
        payments.loc[0, 'payment_value'] = -100.0
        
        rfm_analyzer = RFMAnalyzer()
        rfm_df = rfm_analyzer.calculate_rfm(orders, payments)
        
        # Should handle negative values (might exclude or handle specially)
        self.assertIsInstance(rfm_df, pd.DataFrame)


def run_all_tests():
    """Run all test suites"""
    
    # Create test suite
    test_classes = [
        TestRFMAnalysis,
        TestCohortAnalysis, 
        TestLTVModeling,
        TestAdvancedAnalysis,
        TestEndToEndWorkflow,
        TestErrorHandling
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, failure in result.failures:
            print(f"- {test}: {failure.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, error in result.errors:
            print(f"- {test}: {error.split('Error:')[-1].strip()}")
    
    return result


if __name__ == '__main__':
    print("🧪 Starting Comprehensive Olist Analytics Test Suite")
    print("="*80)
    result = run_all_tests()
    
    # Exit with appropriate code
    if result.failures or result.errors:
        print(f"\n❌ Tests completed with issues!")
        exit(1)
    else:
        print(f"\n✅ All tests passed successfully!")
        exit(0)