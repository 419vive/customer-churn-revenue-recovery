"""Enterprise logging configuration for Olist Analytics"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for production logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage',
                          'extra']:
                log_entry[key] = value
                
        return json.dumps(log_entry)

class AnalyticsLogger:
    """Custom logger for analytics operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._metrics = []
        
    def log_analysis_start(self, analysis_type: str, **kwargs):
        """Log start of analysis with metadata"""
        self.logger.info(
            "Analysis started",
            extra={
                'analysis_type': analysis_type,
                'event_type': 'analysis_start',
                **kwargs
            }
        )
        
    def log_analysis_complete(self, analysis_type: str, duration: float, record_count: int, **kwargs):
        """Log completion of analysis with metrics"""
        self.logger.info(
            "Analysis completed",
            extra={
                'analysis_type': analysis_type,
                'event_type': 'analysis_complete',
                'duration_seconds': duration,
                'record_count': record_count,
                **kwargs
            }
        )
        
    def log_data_quality_issue(self, issue_type: str, severity: str, details: dict):
        """Log data quality issues"""
        self.logger.warning(
            f"Data quality issue: {issue_type}",
            extra={
                'event_type': 'data_quality_issue',
                'issue_type': issue_type,
                'severity': severity,
                'details': details
            }
        )
        
    def log_performance_metric(self, metric_name: str, value: float, unit: str = None):
        """Log performance metrics"""
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'metric_name': metric_name,
            'value': value,
            'unit': unit
        }
        self._metrics.append(metric)
        
        self.logger.debug(
            f"Performance metric: {metric_name} = {value} {unit or ''}",
            extra={
                'event_type': 'performance_metric',
                'metric_name': metric_name,
                'value': value,
                'unit': unit
            }
        )

def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    structured: bool = False,
    enable_file_logging: bool = True
) -> None:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if structured:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))
    
    root_logger.addHandler(console_handler)
    
    if enable_file_logging:
        # Application log file (rotating)
        app_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'olist_analytics.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        if structured:
            app_handler.setFormatter(StructuredFormatter())
        else:
            file_format = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
            app_handler.setFormatter(logging.Formatter(file_format))
        
        root_logger.addHandler(app_handler)
        
        # Error log file (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'errors.log',
            maxBytes=10*1024*1024,
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter() if structured else 
                                 logging.Formatter(file_format))
        root_logger.addHandler(error_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('plotly').setLevel(logging.WARNING)
    
def get_logger(name: str) -> AnalyticsLogger:
    """Get a configured analytics logger instance"""
    return AnalyticsLogger(name)

# Initialize logging on import
setup_logging()