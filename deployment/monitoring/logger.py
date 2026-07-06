"""
Structured Logging Module for SkinGuard Platform
Provides consistent logging across the application with context enrichment
"""

import logging
import logging.config
import yaml
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import time

# Load logging configuration
def setup_logging(config_path: str = None, environment: str = None):
    """
    Setup logging configuration from YAML file
    
    Args:
        config_path: Path to logging config file
        environment: Environment name (development, production)
    """
    
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "logging.config.yaml"
        )
    
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Use environment-specific config if available
        if environment in config:
            config = config[environment]
        
        logging.config.dictConfig(config)
        logging.info(f"Logging configured for environment: {environment}")
    
    except Exception as e:
        # Fallback to basic config
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Failed to load logging config: {e}")


class StructuredLogger:
    """
    Structured logger with context enrichment
    
    Automatically adds:
    - Timestamp
    - Request ID
    - User ID
    - Environment
    - Service name
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context that will be included in all log messages"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self.context = {}
    
    def _enrich_message(self, message: str, extra: Optional[Dict] = None) -> tuple:
        """Enrich message with context"""
        enriched_extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            **self.context
        }
        
        if extra:
            enriched_extra.update(extra)
        
        return message, enriched_extra
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        msg, extra = self._enrich_message(message, kwargs)
        self.logger.debug(msg, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        msg, extra = self._enrich_message(message, kwargs)
        self.logger.info(msg, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        msg, extra = self._enrich_message(message, kwargs)
        self.logger.warning(msg, extra=extra)
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message"""
        msg, extra = self._enrich_message(message, kwargs)
        self.logger.error(msg, extra=extra, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=None, **kwargs):
        """Log critical message"""
        msg, extra = self._enrich_message(message, kwargs)
        self.logger.critical(msg, extra=extra, exc_info=exc_info)


# Specialized loggers for different components
class APILogger(StructuredLogger):
    """Logger for API requests and responses"""
    
    def log_request(self, method: str, path: str, user_id: Optional[str] = None, **kwargs):
        """Log API request"""
        self.info(
            f"API Request: {method} {path}",
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )
    
    def log_response(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Log API response"""
        level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
        
        getattr(self, level)(
            f"API Response: {method} {path} - {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )


class AILogger(StructuredLogger):
    """Logger for AI processing"""
    
    def log_analysis_start(self, report_id: str, image_size: tuple, **kwargs):
        """Log start of AI analysis"""
        self.info(
            f"AI Analysis Started: {report_id}",
            report_id=report_id,
            image_width=image_size[0],
            image_height=image_size[1],
            **kwargs
        )
    
    def log_analysis_complete(self, report_id: str, duration_ms: float, predictions: Dict, **kwargs):
        """Log completion of AI analysis"""
        self.info(
            f"AI Analysis Complete: {report_id}",
            report_id=report_id,
            duration_ms=duration_ms,
            prediction_count=len(predictions),
            **kwargs
        )
    
    def log_nsfw_rejection(self, report_id: str, nsfw_score: float, non_skin_score: float, **kwargs):
        """Log NSFW content rejection"""
        self.warning(
            f"NSFW Content Rejected: {report_id}",
            report_id=report_id,
            nsfw_score=nsfw_score,
            non_skin_score=non_skin_score,
            **kwargs
        )


class SecurityLogger(StructuredLogger):
    """Logger for security events"""
    
    def log_auth_success(self, user_id: str, method: str, **kwargs):
        """Log successful authentication"""
        self.info(
            f"Authentication Success: {user_id}",
            user_id=user_id,
            auth_method=method,
            **kwargs
        )
    
    def log_auth_failure(self, email: str, reason: str, **kwargs):
        """Log failed authentication"""
        self.warning(
            f"Authentication Failed: {email}",
            email=email,
            reason=reason,
            **kwargs
        )
    
    def log_access_denied(self, user_id: str, resource: str, action: str, **kwargs):
        """Log access denied"""
        self.warning(
            f"Access Denied: {user_id} - {resource}",
            user_id=user_id,
            resource=resource,
            action=action,
            **kwargs
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, **kwargs):
        """Log suspicious activity"""
        self.critical(
            f"Suspicious Activity: {user_id} - {activity}",
            user_id=user_id,
            activity=activity,
            **kwargs
        )


# Decorator for logging function execution
def log_execution(logger: StructuredLogger):
    """
    Decorator to log function execution time and errors
    
    Usage:
        @log_execution(api_logger)
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            try:
                logger.debug(f"Executing: {func_name}")
                result = func(*args, **kwargs)
                
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"Completed: {func_name}",
                    function=func_name,
                    duration_ms=duration_ms
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Failed: {func_name} - {str(e)}",
                    function=func_name,
                    duration_ms=duration_ms,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# Create logger instances
def get_logger(name: str, logger_type: str = "standard") -> StructuredLogger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        logger_type: Type of logger (standard, api, ai, security)
    
    Returns:
        StructuredLogger instance
    """
    
    logger_classes = {
        "standard": StructuredLogger,
        "api": APILogger,
        "ai": AILogger,
        "security": SecurityLogger
    }
    
    logger_class = logger_classes.get(logger_type, StructuredLogger)
    return logger_class(name)


# Initialize logging on module import
setup_logging()
