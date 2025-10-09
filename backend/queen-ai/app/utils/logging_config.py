"""
Advanced Logging Configuration

Structured logging with rotation, formatting, and cloud integration.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import structlog
from structlog.stdlib import LoggerFactory
from typing import Optional

from app.config.settings import settings


def configure_logging(
    log_level: str = None,
    log_dir: str = "./logs",
    enable_json: bool = False,
    enable_cloud: bool = False
):
    """
    Configure structured logging for the entire application
    
    Features:
    - Structured logging with structlog
    - Automatic log rotation
    - Different formats for console vs file
    - Cloud logging integration (GCP)
    - Performance-optimized
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_json: Enable JSON formatting
        enable_cloud: Enable cloud logging (GCP)
    """
    log_level = log_level or settings.LOG_LEVEL
    
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)
    
    # Determine log format based on environment
    is_production = settings.ENVIRONMENT == "production"
    is_cloud = settings.ENVIRONMENT in ["staging", "production"] or enable_cloud
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # JSON for production/cloud, KeyValue for development
            structlog.processors.JSONRenderer() if (is_production or enable_json)
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Setup file handlers with rotation
    _setup_file_handlers(log_path, log_level)
    
    # Setup cloud logging if enabled
    if is_cloud and enable_cloud:
        _setup_cloud_logging()
    
    # Log initial startup
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured",
        log_level=log_level,
        log_dir=str(log_path),
        environment=settings.ENVIRONMENT,
        json_format=is_production or enable_json,
        cloud_logging=is_cloud and enable_cloud
    )


def _setup_file_handlers(log_path: Path, log_level: str):
    """Setup rotating file handlers"""
    from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
    
    # Main application log (daily rotation)
    main_log = log_path / "queen.log"
    main_handler = TimedRotatingFileHandler(
        filename=str(main_log),
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding='utf-8'
    )
    main_handler.setLevel(getattr(logging, log_level.upper()))
    main_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Error log (size-based rotation)
    error_log = log_path / "errors.log"
    error_handler = RotatingFileHandler(
        filename=str(error_log),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    ))
    
    # Access log for API requests
    access_log = log_path / "access.log"
    access_handler = TimedRotatingFileHandler(
        filename=str(access_log),
        when='midnight',
        interval=1,
        backupCount=7,  # Keep 7 days
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    
    # Performance log
    perf_log = log_path / "performance.log"
    perf_handler = RotatingFileHandler(
        filename=str(perf_log),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.DEBUG)
    
    # Add handlers to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    
    # Add specific loggers
    logging.getLogger('access').addHandler(access_handler)
    logging.getLogger('performance').addHandler(perf_handler)


def _setup_cloud_logging():
    """Setup Google Cloud Logging"""
    try:
        import google.cloud.logging
        from google.cloud.logging.handlers import CloudLoggingHandler
        
        # Initialize Cloud Logging client
        client = google.cloud.logging.Client()
        
        # Create handler
        cloud_handler = CloudLoggingHandler(
            client,
            name="omk-hive-queen"
        )
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(cloud_handler)
        
        logger = structlog.get_logger(__name__)
        logger.info("Cloud Logging enabled", service="omk-hive-queen")
        
    except ImportError:
        logger = structlog.get_logger(__name__)
        logger.warning("google-cloud-logging not installed - cloud logging disabled")
    except Exception as e:
        logger = structlog.get_logger(__name__)
        logger.error(f"Failed to setup cloud logging: {str(e)}")


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Message", key="value")
    """
    return structlog.get_logger(name)


def log_performance(func_name: str, duration_ms: float, **kwargs):
    """Log performance metrics"""
    logger = logging.getLogger('performance')
    logger.debug(
        f"Performance: {func_name}",
        extra={
            'function': func_name,
            'duration_ms': duration_ms,
            **kwargs
        }
    )


def log_api_request(method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """Log API requests"""
    logger = logging.getLogger('access')
    logger.info(
        f"{method} {path} {status_code} {duration_ms:.2f}ms",
        extra={
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms,
            **kwargs
        }
    )


def log_security_event(event_type: str, severity: str, **kwargs):
    """Log security events"""
    logger = structlog.get_logger('security')
    
    log_func = getattr(logger, severity.lower(), logger.warning)
    log_func(
        f"Security: {event_type}",
        event_type=event_type,
        severity=severity,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )


def log_llm_interaction(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost: float,
    duration_ms: float,
    **kwargs
):
    """Log LLM interactions"""
    logger = structlog.get_logger('llm')
    logger.info(
        f"LLM: {provider}/{model}",
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost=cost,
        duration_ms=duration_ms,
        **kwargs
    )


def log_bee_action(
    bee_name: str,
    action: str,
    success: bool,
    duration_ms: Optional[float] = None,
    **kwargs
):
    """Log bee actions"""
    logger = structlog.get_logger('bees')
    
    log_func = logger.info if success else logger.warning
    log_func(
        f"Bee: {bee_name} - {action}",
        bee=bee_name,
        action=action,
        success=success,
        duration_ms=duration_ms,
        **kwargs
    )


def log_decision(
    decision_type: str,
    decision: dict,
    confidence: float,
    reasoning: Optional[str] = None,
    **kwargs
):
    """Log Queen AI decisions"""
    logger = structlog.get_logger('decisions')
    logger.info(
        f"Decision: {decision_type}",
        type=decision_type,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )


def log_blockchain_transaction(
    tx_type: str,
    tx_hash: Optional[str] = None,
    status: str = "pending",
    gas_used: Optional[int] = None,
    **kwargs
):
    """Log blockchain transactions"""
    logger = structlog.get_logger('blockchain')
    logger.info(
        f"Transaction: {tx_type}",
        type=tx_type,
        tx_hash=tx_hash,
        status=status,
        gas_used=gas_used,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )


# Decorator for automatic function logging
def log_function_call(logger_name: Optional[str] = None):
    """
    Decorator to automatically log function calls
    
    Usage:
        @log_function_call()
        async def my_function(arg1, arg2):
            ...
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                
                logger.debug(
                    f"Function call: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    success=True
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                
                logger.error(
                    f"Function error: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e),
                    success=False,
                    exc_info=True
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                
                logger.debug(
                    f"Function call: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    success=True
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                
                logger.error(
                    f"Function error: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e),
                    success=False,
                    exc_info=True
                )
                
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
