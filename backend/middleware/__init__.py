"""
Middleware Package for Smart Home Automation Backend
Provides authentication, error handling, logging, and security middleware
"""

import os
import logging
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from flask import Flask, request, jsonify, g, current_app
from datetime import datetime
import time

# Package version
__version__ = "1.0.0"

# Import middleware components
try:
    from .firebase_auth import (
        require_auth,
        require_admin,
        token_required,
        init_firebase_admin,
        get_current_user,
        check_user_permissions,
        verify_firebase_token,
        FirebaseAuthMiddleware
    )
except ImportError as e:
    logging.warning(f"Firebase auth middleware not available: {e}")
    # Provide fallback functions
    def require_auth(f): return f
    def require_admin(f): return f  
    def token_required(f): return f
    def init_firebase_admin(): pass
    def get_current_user(): return None
    def check_user_permissions(permission): return True
    def verify_firebase_token(token): return None
    FirebaseAuthMiddleware = None

try:
    from .error_handling import (
        register_error_handlers,
        handle_api_error,
        handle_validation_error,
        handle_not_found,
        handle_unauthorized,
        handle_forbidden,
        handle_internal_error,
        APIError,
        ValidationError
    )
except ImportError as e:
    logging.warning(f"Error handling middleware not available: {e}")
    def register_error_handlers(app): pass
    def handle_api_error(e): return jsonify({'error': str(e)}), 500
    def handle_validation_error(e): return jsonify({'error': str(e)}), 400
    def handle_not_found(e): return jsonify({'error': 'Not found'}), 404
    def handle_unauthorized(e): return jsonify({'error': 'Unauthorized'}), 401
    def handle_forbidden(e): return jsonify({'error': 'Forbidden'}), 403
    def handle_internal_error(e): return jsonify({'error': 'Internal server error'}), 500
    class APIError(Exception): pass
    class ValidationError(Exception): pass

try:
    from .logging_middleware import (
        setup_logging,
        LoggingMiddleware,
        request_logger,
        response_logger,
        error_logger,
        audit_logger
    )
except ImportError as e:
    logging.warning(f"Logging middleware not available: {e}")
    def setup_logging(app): pass
    def request_logger(f): return f
    def response_logger(f): return f
    def error_logger(f): return f
    def audit_logger(action, resource, details=None): pass
    LoggingMiddleware = None

try:
    from .rate_limiting import (
        RateLimitMiddleware,
        rate_limit,
        get_rate_limit_key,
        check_rate_limit,
        reset_rate_limit
    )
except ImportError as e:
    logging.warning(f"Rate limiting middleware not available: {e}")
    def rate_limit(limit): return lambda f: f
    def get_rate_limit_key(): return None
    def check_rate_limit(key, limit): return True
    def reset_rate_limit(key): pass
    RateLimitMiddleware = None

try:
    from .cors_middleware import (
        setup_cors,
        CORSMiddleware,
        cors_preflight_handler
    )
except ImportError as e:
    logging.warning(f"CORS middleware not available: {e}")
    def setup_cors(app): pass
    def cors_preflight_handler(): return '', 200
    CORSMiddleware = None

# Logger for this module
logger = logging.getLogger(__name__)

class MiddlewareManager:
    """
    Central middleware manager for the Smart Home Automation backend
    Handles initialization and coordination of all middleware components
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.middleware_stack: List[Callable] = []
        self.config: Dict[str, Any] = {}
        self.initialized = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize middleware with Flask app
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.config = self._load_config(app)
        
        # Initialize middleware components in order
        self._init_logging_middleware(app)
        self._init_cors_middleware(app)
        self._init_firebase_auth_middleware(app)
        self._init_error_handling_middleware(app)
        self._init_rate_limiting_middleware(app)
        self._init_request_response_middleware(app)
        
        self.initialized = True
        logger.info("Middleware manager initialized successfully")
    
    def _load_config(self, app: Flask) -> Dict[str, Any]:
        """Load middleware configuration from app config"""
        return {
            'LOGGING_ENABLED': app.config.get('LOGGING_ENABLED', True),
            'CORS_ENABLED': app.config.get('CORS_ENABLED', True),
            'AUTH_ENABLED': app.config.get('AUTH_ENABLED', True),
            'RATE_LIMITING_ENABLED': app.config.get('RATE_LIMITING_ENABLED', True),
            'ERROR_HANDLING_ENABLED': app.config.get('ERROR_HANDLING_ENABLED', True),
            'REQUEST_LOGGING': app.config.get('REQUEST_LOGGING', True),
            'AUDIT_LOGGING': app.config.get('AUDIT_LOGGING', True),
            'PERFORMANCE_MONITORING': app.config.get('PERFORMANCE_MONITORING', True)
        }
    
    def _init_logging_middleware(self, app: Flask) -> None:
        """Initialize logging middleware"""
        if self.config.get('LOGGING_ENABLED', True):
            try:
                setup_logging(app)
                
                # Add request/response logging if enabled
                if self.config.get('REQUEST_LOGGING', True):
                    @app.before_request
                    def log_request_info():
                        g.start_time = time.time()
                        if current_app.debug:
                            logger.debug(f"Request: {request.method} {request.url}")
                            logger.debug(f"Headers: {dict(request.headers)}")
                    
                    @app.after_request
                    def log_response_info(response):
                        if hasattr(g, 'start_time'):
                            duration = time.time() - g.start_time
                            logger.info(f"Response: {response.status_code} - {duration:.3f}s")
                        return response
                
                logger.info("Logging middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize logging middleware: {e}")
    
    def _init_cors_middleware(self, app: Flask) -> None:
        """Initialize CORS middleware"""
        if self.config.get('CORS_ENABLED', True):
            try:
                setup_cors(app)
                logger.info("CORS middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize CORS middleware: {e}")
    
    def _init_firebase_auth_middleware(self, app: Flask) -> None:
        """Initialize Firebase authentication middleware"""
        if self.config.get('AUTH_ENABLED', True):
            try:
                init_firebase_admin()
                
                # Add authentication context to Flask g
                @app.before_request
                def load_user_context():
                    g.current_user = None
                    g.user_permissions = []
                    g.is_authenticated = False
                    
                    # Skip auth for certain routes
                    skip_auth_routes = ['/api/status', '/api/health', '/']
                    if request.endpoint in skip_auth_routes or request.path in skip_auth_routes:
                        return
                    
                    # Check for auth token
                    auth_header = request.headers.get('Authorization')
                    if auth_header and auth_header.startswith('Bearer '):
                        token = auth_header.split(' ')[1]
                        try:
                            user_info = verify_firebase_token(token)
                            if user_info:
                                g.current_user = user_info
                                g.is_authenticated = True
                                g.user_permissions = user_info.get('custom_claims', {}).get('permissions', [])
                        except Exception as e:
                            logger.warning(f"Token verification failed: {e}")
                
                logger.info("Firebase auth middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase auth middleware: {e}")
    
    def _init_error_handling_middleware(self, app: Flask) -> None:
        """Initialize error handling middleware"""
        if self.config.get('ERROR_HANDLING_ENABLED', True):
            try:
                register_error_handlers(app)
                logger.info("Error handling middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize error handling middleware: {e}")
    
    def _init_rate_limiting_middleware(self, app: Flask) -> None:
        """Initialize rate limiting middleware"""
        if self.config.get('RATE_LIMITING_ENABLED', True):
            try:
                # Basic rate limiting setup
                @app.before_request
                def check_rate_limits():
                    # Skip rate limiting for static files and health checks
                    skip_paths = ['/static/', '/api/status', '/api/health']
                    if any(request.path.startswith(path) for path in skip_paths):
                        return
                    
                    # Basic rate limiting logic would go here
                    # For now, just log the request
                    if self.config.get('PERFORMANCE_MONITORING', True):
                        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                        logger.debug(f"Rate limit check for {client_ip}: {request.method} {request.path}")
                
                logger.info("Rate limiting middleware initialized")
            except Exception as e:
                logger.error(f"Failed to initialize rate limiting middleware: {e}")
    
    def _init_request_response_middleware(self, app: Flask) -> None:
        """Initialize general request/response middleware"""
        try:
            @app.before_request
            def before_request_handler():
                # Add request ID for tracing
                import uuid
                g.request_id = str(uuid.uuid4())
                
                # Add timestamp
                g.request_timestamp = datetime.utcnow()
                
                # Security headers preparation
                g.security_headers = {
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block',
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
                }
            
            @app.after_request
            def after_request_handler(response):
                # Add security headers
                if hasattr(g, 'security_headers'):
                    for header, value in g.security_headers.items():
                        response.headers[header] = value
                
                # Add request ID to response
                if hasattr(g, 'request_id'):
                    response.headers['X-Request-ID'] = g.request_id
                
                # Add CORS headers if needed
                if request.method == 'OPTIONS':
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                    response.headers['Access-Control-Max-Age'] = '86400'
                
                return response
            
            logger.info("Request/response middleware initialized")
        except Exception as e:
            logger.error(f"Failed to initialize request/response middleware: {e}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """
        Add custom middleware to the stack
        
        Args:
            middleware: Middleware function or class
        """
        self.middleware_stack.append(middleware)
        logger.info(f"Added custom middleware: {middleware.__name__}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get middleware status information"""
        return {
            'initialized': self.initialized,
            'middleware_count': len(self.middleware_stack),
            'config': self.config,
            'components': {
                'logging': self.config.get('LOGGING_ENABLED', False),
                'cors': self.config.get('CORS_ENABLED', False),
                'auth': self.config.get('AUTH_ENABLED', False),
                'rate_limiting': self.config.get('RATE_LIMITING_ENABLED', False),
                'error_handling': self.config.get('ERROR_HANDLING_ENABLED', False)
            }
        }

# Utility functions for easy access
def init_middleware(app: Flask) -> MiddlewareManager:
    """
    Initialize all middleware for the Flask app
    
    Args:
        app: Flask application instance
        
    Returns:
        MiddlewareManager instance
    """
    manager = MiddlewareManager(app)
    return manager

def get_current_user_info() -> Optional[Dict[str, Any]]:
    """Get current authenticated user information"""
    return getattr(g, 'current_user', None)

def is_user_authenticated() -> bool:
    """Check if current user is authenticated"""
    return getattr(g, 'is_authenticated', False)

def has_permission(permission: str) -> bool:
    """Check if current user has specific permission"""
    if not is_user_authenticated():
        return False
    
    user_permissions = getattr(g, 'user_permissions', [])
    return permission in user_permissions or 'admin' in user_permissions

def get_request_id() -> Optional[str]:
    """Get current request ID for tracing"""
    return getattr(g, 'request_id', None)

def log_audit_event(action: str, resource: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log audit event
    
    Args:
        action: Action performed
        resource: Resource affected
        details: Additional details
    """
    try:
        audit_logger(action, resource, details)
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

# Convenience decorators
def authenticated_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_user_authenticated():
            return jsonify({
                'error': 'Authentication required',
                'message': 'You must be logged in to access this resource'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission: str):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(permission):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Permission "{permission}" required'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission('admin'):
            return jsonify({
                'error': 'Admin access required',
                'message': 'Administrator privileges required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# Global middleware manager instance
middleware_manager: Optional[MiddlewareManager] = None

def get_middleware_manager() -> Optional[MiddlewareManager]:
    """Get global middleware manager instance"""
    return middleware_manager

def set_middleware_manager(manager: MiddlewareManager) -> None:
    """Set global middleware manager instance"""
    global middleware_manager
    middleware_manager = manager

# Export all public components
__all__ = [
    # Core middleware functions
    'require_auth',
    'require_admin', 
    'token_required',
    'authenticated_required',
    'permission_required',
    'admin_required',
    
    # Error handling
    'register_error_handlers',
    'handle_api_error',
    'handle_validation_error',
    'handle_not_found',
    'handle_unauthorized',
    'handle_forbidden',
    'handle_internal_error',
    'APIError',
    'ValidationError',
    
    # Logging
    'setup_logging',
    'request_logger',
    'response_logger',
    'error_logger',
    'audit_logger',
    'log_audit_event',
    
    # Rate limiting
    'rate_limit',
    'check_rate_limit',
    'reset_rate_limit',
    
    # CORS
    'setup_cors',
    'cors_preflight_handler',
    
    # Utilities
    'init_middleware',
    'get_current_user_info',
    'is_user_authenticated',
    'has_permission',
    'get_request_id',
    
    # Manager
    'MiddlewareManager',
    'get_middleware_manager',
    'set_middleware_manager',
    
    # Middleware classes
    'FirebaseAuthMiddleware',
    'LoggingMiddleware',
    'RateLimitMiddleware',
    'CORSMiddleware'
]

# Configuration examples for different environments
MIDDLEWARE_CONFIG_EXAMPLES = {
    'development': {
        'LOGGING_ENABLED': True,
        'CORS_ENABLED': True,
        'AUTH_ENABLED': True,
        'RATE_LIMITING_ENABLED': False,
        'ERROR_HANDLING_ENABLED': True,
        'REQUEST_LOGGING': True,
        'AUDIT_LOGGING': True,
        'PERFORMANCE_MONITORING': True
    },
    'production': {
        'LOGGING_ENABLED': True,
        'CORS_ENABLED': True,
        'AUTH_ENABLED': True,
        'RATE_LIMITING_ENABLED': True,
        'ERROR_HANDLING_ENABLED': True,
        'REQUEST_LOGGING': False,
        'AUDIT_LOGGING': True,
        'PERFORMANCE_MONITORING': True
    },
    'testing': {
        'LOGGING_ENABLED': False,
        'CORS_ENABLED': False,
        'AUTH_ENABLED': False,
        'RATE_LIMITING_ENABLED': False,
        'ERROR_HANDLING_ENABLED': True,
        'REQUEST_LOGGING': False,
        'AUDIT_LOGGING': False,
        'PERFORMANCE_MONITORING': False
    }
}

# Initialize logging for this module
logger.info(f"Smart Home Automation Middleware Package v{__version__} loaded")
logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
