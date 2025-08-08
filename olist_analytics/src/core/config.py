"""Enterprise-grade configuration management for Olist Analytics"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'olist_analytics')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', '')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    @property
    def url(self) -> str:
        """Generate database URL for SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_db: int = int(os.getenv('REDIS_DB', '0'))
    ttl_seconds: int = int(os.getenv('CACHE_TTL', '3600'))
    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    
@dataclass
class AnalyticsConfig:
    """Analytics-specific configuration"""
    rfm_reference_date: Optional[str] = None
    cohort_periods: int = 12
    ltv_prediction_months: int = 12
    segment_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'champion_r_min': 4,
        'champion_f_min': 4,
        'champion_m_min': 4,
        'at_risk_r_max': 2,
        'lost_r_max': 1
    })
    
@dataclass
class DashboardConfig:
    """Dashboard configuration settings"""
    host: str = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    port: int = int(os.getenv('DASHBOARD_PORT', '8050'))
    debug: bool = os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true'
    auto_reload: bool = os.getenv('DASHBOARD_AUTO_RELOAD', 'false').lower() == 'true'
    
@dataclass
class SecurityConfig:
    """Security and authentication settings"""
    secret_key: str = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    jwt_expiry: timedelta = timedelta(hours=24)
    allowed_hosts: list = field(default_factory=lambda: ['localhost', '127.0.0.1'])
    enable_cors: bool = os.getenv('ENABLE_CORS', 'false').lower() == 'true'
    
class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(__file__).parent.parent.parent / 'config.yml'
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file and environment"""
        # Load from YAML file if exists
        file_config = {}
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                file_config = yaml.safe_load(f) or {}
        
        # Initialize configuration objects
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.analytics = AnalyticsConfig()
        self.dashboard = DashboardConfig()
        self.security = SecurityConfig()
        
        # Override with file config
        if 'database' in file_config:
            for key, value in file_config['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
                    
        if 'analytics' in file_config:
            for key, value in file_config['analytics'].items():
                if hasattr(self.analytics, key):
                    setattr(self.analytics, key, value)
        
        # Environment detection
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.is_production = self.environment == 'production'
        self.is_development = self.environment == 'development'
        
        # Data paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / 'data'
        self.outputs_dir = self.project_root / 'outputs'
        self.logs_dir = self.project_root / 'logs'
        
        # Ensure directories exist
        for directory in [self.data_dir, self.outputs_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation"""
        keys = key.split('.')
        value = self
        
        try:
            for k in keys:
                value = getattr(value, k)
            return value
        except AttributeError:
            return default
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Database validation
        if not self.database.name:
            errors.append("Database name is required")
            
        # Security validation
        if self.is_production and self.security.secret_key == 'dev-key-change-in-production':
            errors.append("Secret key must be changed in production")
            
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
            
        return True

# Global configuration instance
config = Config()