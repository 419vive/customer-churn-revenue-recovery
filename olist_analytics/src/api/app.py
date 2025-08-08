"""FastAPI application for Olist Analytics"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import pandas as pd
from typing import Dict, Any, Optional, List
import time
import traceback
from datetime import datetime

from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import OlistAnalyticsError, AnalysisError, DataValidationError
from ..analytics.enhanced_rfm import EnterpriseRFMAnalyzer
from ..analytics.cohort_analysis import CohortAnalyzer
from ..analytics.ltv_modeling import LTVPredictor
from .models import (
    AnalysisRequest, AnalysisResponse, RFMRequest, CohortRequest,
    HealthCheckResponse, MetricsResponse
)
from .auth import authenticate, get_current_user
from .rate_limit import RateLimiter

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)
rate_limiter = RateLimiter()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Olist Analytics API",
        description="Enterprise analytics API for Brazilian e-commerce data",
        version=config.get('api.version', 'v1'),
        docs_url=config.get('api.docs_path', '/docs') if config.get('api.docs_enabled', True) else None,
        redoc_url=config.get('api.redoc_path', '/redoc') if config.get('api.docs_enabled', True) else None,
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Add routes
    setup_routes(app)
    
    # Add startup/shutdown events
    setup_events(app)
    
    return app

def setup_middleware(app: FastAPI):
    """Setup application middleware"""
    
    # CORS middleware
    if config.security.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.security.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.security.allowed_hosts
    )
    
    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > config.get('monitoring.thresholds.analysis_duration_warning_seconds', 30):
            logger.logger.warning(
                f"Slow request: {request.method} {request.url.path}",
                extra={
                    'method': request.method,
                    'path': str(request.url.path),
                    'duration': process_time,
                    'event_type': 'slow_request'
                }
            )
        
        return response

def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(OlistAnalyticsError)
    async def olist_analytics_exception_handler(request: Request, exc: OlistAnalyticsError):
        logger.logger.error(
            f"Analytics error: {exc.message}",
            extra={
                'error_code': exc.error_code,
                'details': exc.details,
                'path': str(request.url.path),
                'method': request.method
            }
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        error_id = int(time.time())
        
        logger.logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                'error_id': error_id,
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'path': str(request.url.path),
                'method': request.method
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred",
                    "error_id": error_id
                }
            }
        )

def setup_routes(app: FastAPI):
    """Setup API routes"""
    
    @app.get("/health", response_model=HealthCheckResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version=config.get('api.version', 'v1')
        )
    
    @app.get("/metrics", response_model=MetricsResponse)
    async def get_metrics():
        """Metrics endpoint for monitoring"""
        # This would integrate with your metrics collection system
        return MetricsResponse(
            active_analyses=0,  # Would come from actual metrics
            total_requests=1000,
            avg_response_time=0.25,
            error_rate=0.02
        )
    
    @app.post("/api/v1/analysis/rfm", response_model=AnalysisResponse)
    async def run_rfm_analysis(
        request: RFMRequest,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user),
        _rate_limit: None = Depends(rate_limiter.check_rate_limit)
    ):
        """Run RFM analysis on provided data"""
        
        analysis_id = f"rfm_{int(time.time())}"
        logger.log_analysis_start('rfm_api_request', user_id=current_user.get('user_id'))
        
        try:
            # Convert request data to DataFrames
            orders_df = pd.DataFrame(request.orders_data)
            payments_df = pd.DataFrame(request.payments_data)
            
            # Initialize analyzer
            analyzer = EnterpriseRFMAnalyzer(
                reference_date=request.reference_date
            )
            
            # Run analysis
            results = analyzer.analyze(
                orders_df=orders_df,
                payments_df=payments_df,
                validate_data=request.validate_data
            )
            
            # Convert results to response format
            response_data = {
                "segments": results.segments.to_dict('records'),
                "summary": results.summary.to_dict('records'),
                "metadata": results.analysis_metadata,
                "data_quality": results.data_quality_report
            }
            
            # Generate recommendations if requested
            if request.include_recommendations:
                recommendations = analyzer.generate_recommendations(results)
                response_data["recommendations"] = recommendations
            
            logger.log_analysis_complete(
                'rfm_api_request', 
                results.analysis_metadata['duration_seconds'],
                results.analysis_metadata['total_customers'],
                user_id=current_user.get('user_id')
            )
            
            return AnalysisResponse(
                analysis_id=analysis_id,
                analysis_type="rfm",
                status="completed",
                data=response_data,
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.logger.error(f"RFM analysis failed: {str(e)}", exc_info=True)
            raise AnalysisError(
                f"RFM analysis failed: {str(e)}",
                error_code="RFM_ANALYSIS_FAILED"
            )
    
    @app.post("/api/v1/analysis/cohort")
    async def run_cohort_analysis(
        request: CohortRequest,
        current_user: dict = Depends(get_current_user),
        _rate_limit: None = Depends(rate_limiter.check_rate_limit)
    ):
        """Run cohort analysis"""
        
        analysis_id = f"cohort_{int(time.time())}"
        logger.log_analysis_start('cohort_api_request', user_id=current_user.get('user_id'))
        
        try:
            orders_df = pd.DataFrame(request.orders_data)
            payments_df = pd.DataFrame(request.payments_data)
            
            analyzer = CohortAnalyzer()
            cohort_df = analyzer.create_cohorts(orders_df, payments_df)
            retention_df = analyzer.calculate_retention(cohort_df)
            
            response_data = {
                "retention_matrix": retention_df.to_dict(),
                "cohort_data": cohort_df.to_dict('records')
            }
            
            return AnalysisResponse(
                analysis_id=analysis_id,
                analysis_type="cohort",
                status="completed",
                data=response_data,
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.logger.error(f"Cohort analysis failed: {str(e)}", exc_info=True)
            raise AnalysisError(
                f"Cohort analysis failed: {str(e)}",
                error_code="COHORT_ANALYSIS_FAILED"
            )
    
    @app.get("/api/v1/analysis/{analysis_id}")
    async def get_analysis_status(
        analysis_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        """Get analysis status and results"""
        # This would integrate with a job tracking system
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }

def setup_events(app: FastAPI):
    """Setup startup and shutdown events"""
    
    @app.on_event("startup")
    async def startup_event():
        logger.logger.info("Olist Analytics API starting up")
        # Initialize any required resources
        
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.logger.info("Olist Analytics API shutting down")
        # Cleanup resources

# Create application instance
app = create_app() if config.get('api.enabled', False) else None