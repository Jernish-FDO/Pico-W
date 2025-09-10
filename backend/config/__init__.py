"""
Configuration package for Smart Home Automation Backend
Handles environment-specific settings, Firebase configuration, and application constants
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Import configuration modules
from .firebase_config import FirebaseConfig
from .app_config import AppConfig, DevelopmentConfig, ProductionConfig, TestingConfig

# Package version
__version__ = "1.0.0"

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> AppConfig:
    """
    Get configuration object based on environment
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration object instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_map.get(config_name.lower(), DevelopmentConfig)
    return config_class()

def get_firebase_config() -> Dict[str, Any]:
    """
    Get Firebase configuration dictionary
    
    Returns:
        Firebase configuration dictionary
    """
    firebase_config = FirebaseConfig()
    return firebase_config.get_config()

def get_database_url() -> str:
    """
    Get Firebase Realtime Database URL
    
    Returns:
        Database URL string
    """
    firebase_config = FirebaseConfig()
    return firebase_config.database_url

def get_project_root() -> Path:
    """
    Get project root directory path
    
    Returns:
        Path object pointing to project root
    """
    return Path(__file__).parent.parent.parent

def get_static_folder() -> str:
    """
    Get static files folder path
    
    Returns:
        Static folder path string
    """
    return os.path.join(get_project_root(), 'frontend')

def get_upload_folder() -> str:
    """
    Get upload folder path for file uploads
    
    Returns:
        Upload folder path string
    """
    upload_path = os.path.join(get_project_root(), 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def get_logs_folder() -> str:
    """
    Get logs folder path
    
    Returns:
        Logs folder path string
    """
    logs_path = os.path.join(get_project_root(), 'logs')
    os.makedirs(logs_path, exist_ok=True)
    return logs_path

def validate_environment() -> bool:
    """
    Validate that all required environment variables are set
    
    Returns:
        True if all required variables are set, False otherwise
    """
    required_vars = [
        'SECRET_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def setup_logging(config: AppConfig) -> None:
    """
    Setup application logging configuration
    
    Args:
        config: Configuration object
    """
    import logging
    import logging.handlers
    from datetime import datetime
    
    # Create logs directory
    logs_dir = get_logs_folder()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                filename=os.path.join(logs_dir, 'app.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Create separate loggers for different components
    loggers = {
        'app': logging.getLogger('smart_home.app'),
        'auth': logging.getLogger('smart_home.auth'),
        'devices': logging.getLogger('smart_home.devices'),
        'relays': logging.getLogger('smart_home.relays'),
        'firebase': logging.getLogger('smart_home.firebase'),
    }
    
    # Set levels for different loggers if needed
    if config.DEBUG:
        for logger in loggers.values():
            logger.setLevel(logging.DEBUG)

@dataclass
class APIConstants:
    """API constants and configuration values"""
    
    # API Version
    VERSION: str = "v1"
    
    # Rate limiting
    DEFAULT_RATE_LIMIT: str = "1000/hour"
    AUTH_RATE_LIMIT: str = "5/minute"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Device limits
    MAX_DEVICES_PER_USER: int = 10
    MAX_RELAYS_PER_DEVICE: int = 16
    
    # File upload limits
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {'json', 'csv', 'txt', 'log'}
    
    # Cache settings
    CACHE_TIMEOUT: int = 300  # 5 minutes
    
    # Security
    JWT_EXPIRATION: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRATION: int = 30 * 24 * 3600  # 30 days
    
    # Firebase specific
    FIREBASE_TIMEOUT: int = 30  # seconds
    FIREBASE_RETRY_COUNT: int = 3
    
    # Device communication
    DEVICE_HEARTBEAT_TIMEOUT: int = 60  # seconds
    DEVICE_OFFLINE_THRESHOLD: int = 300  # 5 minutes

@dataclass 
class ErrorCodes:
    """Standard error codes for the application"""
    
    # Authentication errors (1000-1099)
    AUTH_TOKEN_MISSING = 1000
    AUTH_TOKEN_INVALID = 1001
    AUTH_TOKEN_EXPIRED = 1002
    AUTH_INSUFFICIENT_PERMISSIONS = 1003
    AUTH_USER_NOT_FOUND = 1004
    
    # Device errors (1100-1199)
    DEVICE_NOT_FOUND = 1100
    DEVICE_OFFLINE = 1101
    DEVICE_PERMISSION_DENIED = 1102
    DEVICE_LIMIT_EXCEEDED = 1103
    DEVICE_CONFIGURATION_ERROR = 1104
    
    # Relay errors (1200-1299)
    RELAY_NOT_FOUND = 1200
    RELAY_CONTROL_FAILED = 1201
    RELAY_SAFETY_VIOLATION = 1202
    RELAY_BULK_OPERATION_FAILED = 1203
    
    # Firebase errors (1300-1399)
    FIREBASE_CONNECTION_ERROR = 1300
    FIREBASE_PERMISSION_DENIED = 1301
    FIREBASE_QUOTA_EXCEEDED = 1302
    FIREBASE_INVALID_DATA = 1303
    
    # General errors (1400-1499)
    INVALID_REQUEST_DATA = 1400
    RATE_LIMIT_EXCEEDED = 1401
    INTERNAL_SERVER_ERROR = 1500

class ConfigManager:
    """
    Configuration manager singleton for handling runtime configuration
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = get_config()
            self.firebase_config = FirebaseConfig()
            self.api_constants = APIConstants()
            self.error_codes = ErrorCodes()
    
    @property
    def config(self) -> AppConfig:
        """Get current application configuration"""
        return self._config
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return isinstance(self._config, DevelopmentConfig)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return isinstance(self._config, ProductionConfig)
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return isinstance(self._config, TestingConfig)
    
    def get_database_ref(self, path: str = '') -> str:
        """
        Get full database reference path
        
        Args:
            path: Database path (e.g., 'devices/pico_w_001')
        
        Returns:
            Full database URL with path
        """
        base_url = self.firebase_config.database_url.rstrip('/')
        if path:
            return f"{base_url}/{path.lstrip('/')}"
        return base_url
    
    def get_cors_origins(self) -> list:
        """Get CORS allowed origins based on environment"""
        if self.is_development:
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080"
            ]
        elif self.is_production:
            return [
                "https://yourdomain.com",
                "https://www.yourdomain.com",
                "https://app.yourdomain.com"
            ]
        return ["*"]  # Testing allows all origins

# Create global configuration manager instance
config_manager = ConfigManager()

# Export commonly used objects
__all__ = [
    'get_config',
    'get_firebase_config', 
    'get_database_url',
    'get_project_root',
    'get_static_folder',
    'get_upload_folder',
    'get_logs_folder',
    'validate_environment',
    'setup_logging',
    'FirebaseConfig',
    'AppConfig',
    'DevelopmentConfig',
    'ProductionConfig', 
    'TestingConfig',
    'APIConstants',
    'ErrorCodes',
    'ConfigManager',
    'config_manager'
]

# Environment validation on import
if not validate_environment():
    print("Warning: Some environment variables are missing. Check your configuration.")

# Initialize logging if not in testing mode
if os.environ.get('FLASK_ENV') != 'testing':
    setup_logging(config_manager.config)

print(f"Smart Home Automation Backend Config v{__version__} loaded")
print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
print(f"Debug mode: {config_manager.config.DEBUG}")
