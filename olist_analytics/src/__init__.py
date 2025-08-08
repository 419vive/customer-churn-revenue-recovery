"""
Olist E-Commerce Analytics Package
Advanced analytics solution for Brazilian e-commerce data
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .analytics.rfm_analysis import RFMAnalyzer
from .analytics.cohort_analysis import CohortAnalyzer
from .analytics.ltv_modeling import LTVPredictor

__all__ = [
    "RFMAnalyzer",
    "CohortAnalyzer", 
    "LTVPredictor"
]