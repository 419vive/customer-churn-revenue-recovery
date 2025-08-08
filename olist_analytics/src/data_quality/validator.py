"""Enterprise data validation framework"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import re

from ..core.exceptions import DataValidationError
from ..core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
        
    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
        
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.metrics.update(other.metrics)

class ValidationRule:
    """Base class for validation rules"""
    
    def __init__(self, name: str, description: str, severity: str = 'error'):
        self.name = name
        self.description = description
        self.severity = severity  # 'error' or 'warning'
        
    def validate(self, df: pd.DataFrame, column: str = None) -> ValidationResult:
        """Validate data - to be implemented by subclasses"""
        raise NotImplementedError

class NotNullRule(ValidationRule):
    """Validates that column values are not null"""
    
    def __init__(self, column: str, max_null_percentage: float = 0.0):
        super().__init__(f"not_null_{column}", f"Column {column} should not have null values")
        self.column = column
        self.max_null_percentage = max_null_percentage
        
    def validate(self, df: pd.DataFrame, column: str = None) -> ValidationResult:
        result = ValidationResult(True)
        col = column or self.column
        
        if col not in df.columns:
            result.add_error(f"Column {col} not found in DataFrame")
            return result
            
        null_count = df[col].isnull().sum()
        total_count = len(df)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        result.metrics[f'{col}_null_count'] = null_count
        result.metrics[f'{col}_null_percentage'] = null_percentage
        
        if null_percentage > self.max_null_percentage:
            if self.severity == 'error':
                result.add_error(f"Column {col} has {null_percentage:.2f}% null values (max allowed: {self.max_null_percentage}%)")
            else:
                result.add_warning(f"Column {col} has {null_percentage:.2f}% null values")
                
        return result

class DataTypeRule(ValidationRule):
    """Validates data types"""
    
    def __init__(self, column: str, expected_type: str):
        super().__init__(f"datatype_{column}", f"Column {column} should be of type {expected_type}")
        self.column = column
        self.expected_type = expected_type
        
    def validate(self, df: pd.DataFrame, column: str = None) -> ValidationResult:
        result = ValidationResult(True)
        col = column or self.column
        
        if col not in df.columns:
            result.add_error(f"Column {col} not found in DataFrame")
            return result
            
        actual_type = str(df[col].dtype)
        
        # Type mapping for common cases
        type_mapping = {
            'object': ['string', 'str', 'text'],
            'int64': ['int', 'integer'],
            'float64': ['float', 'numeric', 'decimal'],
            'datetime64[ns]': ['datetime', 'timestamp'],
            'bool': ['boolean']
        }
        
        is_valid_type = False
        for dtype, aliases in type_mapping.items():
            if actual_type.startswith(dtype) and self.expected_type.lower() in [dtype] + aliases:
                is_valid_type = True
                break
                
        if not is_valid_type:
            result.add_error(f"Column {col} has type {actual_type}, expected {self.expected_type}")
            
        result.metrics[f'{col}_actual_type'] = actual_type
        return result

class RangeRule(ValidationRule):
    """Validates numeric values are within range"""
    
    def __init__(self, column: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        super().__init__(f"range_{column}", f"Column {column} values should be within range")
        self.column = column
        self.min_value = min_value
        self.max_value = max_value
        
    def validate(self, df: pd.DataFrame, column: str = None) -> ValidationResult:
        result = ValidationResult(True)
        col = column or self.column
        
        if col not in df.columns:
            result.add_error(f"Column {col} not found in DataFrame")
            return result
            
        numeric_data = pd.to_numeric(df[col], errors='coerce')
        
        if self.min_value is not None:
            below_min = numeric_data < self.min_value
            below_min_count = below_min.sum()
            if below_min_count > 0:
                result.add_error(f"Column {col} has {below_min_count} values below minimum {self.min_value}")
                
        if self.max_value is not None:
            above_max = numeric_data > self.max_value
            above_max_count = above_max.sum()
            if above_max_count > 0:
                result.add_error(f"Column {col} has {above_max_count} values above maximum {self.max_value}")
                
        result.metrics[f'{col}_min'] = numeric_data.min()
        result.metrics[f'{col}_max'] = numeric_data.max()
        result.metrics[f'{col}_mean'] = numeric_data.mean()
        
        return result

class PatternRule(ValidationRule):
    """Validates string patterns using regex"""
    
    def __init__(self, column: str, pattern: str, description: str = None):
        super().__init__(f"pattern_{column}", description or f"Column {column} should match pattern")
        self.column = column
        self.pattern = re.compile(pattern)
        
    def validate(self, df: pd.DataFrame, column: str = None) -> ValidationResult:
        result = ValidationResult(True)
        col = column or self.column
        
        if col not in df.columns:
            result.add_error(f"Column {col} not found in DataFrame")
            return result
            
        string_data = df[col].astype(str)
        matches = string_data.str.match(self.pattern, na=False)
        non_match_count = (~matches).sum()
        
        if non_match_count > 0:
            result.add_error(f"Column {col} has {non_match_count} values that don't match the required pattern")
            
        result.metrics[f'{col}_pattern_matches'] = matches.sum()
        result.metrics[f'{col}_pattern_non_matches'] = non_match_count
        
        return result

class DataValidator:
    """Enterprise data validation framework"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        
    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules.append(rule)
        return self
        
    def add_not_null(self, column: str, max_null_percentage: float = 0.0):
        """Add not null validation rule"""
        return self.add_rule(NotNullRule(column, max_null_percentage))
        
    def add_data_type(self, column: str, expected_type: str):
        """Add data type validation rule"""
        return self.add_rule(DataTypeRule(column, expected_type))
        
    def add_range(self, column: str, min_value: float = None, max_value: float = None):
        """Add range validation rule"""
        return self.add_rule(RangeRule(column, min_value, max_value))
        
    def add_pattern(self, column: str, pattern: str, description: str = None):
        """Add pattern validation rule"""
        return self.add_rule(PatternRule(column, pattern, description))
        
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Run all validation rules on DataFrame"""
        logger.log_analysis_start('data_validation', record_count=len(df))
        start_time = datetime.now()
        
        overall_result = ValidationResult(True)
        
        try:
            for rule in self.rules:
                rule_result = rule.validate(df)
                overall_result.merge(rule_result)
                
                if rule_result.errors:
                    logger.log_data_quality_issue(
                        rule.name,
                        'error' if not rule_result.is_valid else 'warning',
                        {'errors': rule_result.errors, 'warnings': rule_result.warnings}
                    )
                    
            duration = (datetime.now() - start_time).total_seconds()
            logger.log_analysis_complete('data_validation', duration, len(df),
                                       validation_errors=len(overall_result.errors),
                                       validation_warnings=len(overall_result.warnings))
                                       
        except Exception as e:
            logger.logger.error(f"Validation failed: {str(e)}")
            overall_result.add_error(f"Validation process failed: {str(e)}")
            
        return overall_result
    
    def validate_or_raise(self, df: pd.DataFrame) -> ValidationResult:
        """Validate and raise exception if validation fails"""
        result = self.validate(df)
        
        if not result.is_valid:
            error_details = {
                'errors': result.errors,
                'warnings': result.warnings,
                'metrics': result.metrics
            }
            raise DataValidationError(
                f"Data validation failed with {len(result.errors)} errors",
                error_code='VALIDATION_FAILED',
                details=error_details
            )
            
        return result