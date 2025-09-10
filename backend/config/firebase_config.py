"""
Firebase Configuration for Smart Home Automation Backend
Handles Firebase Admin SDK initialization, authentication, and database connections
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, db, auth
from firebase_admin.exceptions import FirebaseError, InvalidArgumentError

logger = logging.getLogger(__name__)

@dataclass
class FirebaseConfig:
    """
    Firebase configuration class for managing Firebase Admin SDK
    """
    
    # Firebase project configuration
    project_id: str = field(default_factory=lambda: os.environ.get('FIREBASE_PROJECT_ID', ''))
    database_url: str = field(default_factory=lambda: os.environ.get('FIREBASE_DATABASE_URL', ''))
    storage_bucket: str = field(default_factory=lambda: os.environ.get('FIREBASE_STORAGE_BUCKET', ''))
    
    # Service account configuration
    service_account_key_path: Optional[str] = field(default_factory=lambda: os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH'))
    service_account_json: Optional[str] = field(default_factory=lambda: os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON'))
    
    # Authentication configuration
    api_key: str = field(default_factory=lambda: os.environ.get('FIREBASE_API_KEY', ''))
    auth_domain: str = field(default_factory=lambda: os.environ.get('FIREBASE_AUTH_DOMAIN', ''))
    
    # Connection settings
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # App instance
    _app: Optional[firebase_admin.App] = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)
    
    def __post_init__(self):
        """Post-initialization setup"""
        if not self.project_id:
            self.project_id = self._extract_project_id_from_url()
        
        if not self.database_url and self.project_id:
            self.database_url = f"https://{self.project_id}-default-rtdb.firebaseio.com/"
        
        if not self.storage_bucket and self.project_id:
            self.storage_bucket = f"{self.project_id}.appspot.com"
        
        if not self.auth_domain and self.project_id:
            self.auth_domain = f"{self.project_id}.firebaseapp.com"
    
    def _extract_project_id_from_url(self) -> str:
        """Extract project ID from database URL"""
        if self.database_url:
            try:
                # Extract from URL like: https://project-name-default-rtdb.firebaseio.com/
                url_parts = self.database_url.replace('https://', '').replace('/', '').split('-default-rtdb')
                if url_parts:
                    return url_parts[0]
            except Exception as e:
                logger.warning(f"Could not extract project ID from URL: {e}")
        return ""
    
    def get_credentials(self) -> credentials.Base:
        """
        Get Firebase credentials based on available configuration
        
        Returns:
            Firebase credentials object
            
        Raises:
            ValueError: If no valid credentials configuration found
        """
        try:
            # Method 1: Use service account key file path
            if self.service_account_key_path and os.path.exists(self.service_account_key_path):
                logger.info(f"Using service account key file: {self.service_account_key_path}")
                return credentials.Certificate(self.service_account_key_path)
            
            # Method 2: Use service account JSON string (from environment)
            if self.service_account_json:
                logger.info("Using service account JSON from environment variable")
                try:
                    service_account_dict = json.loads(self.service_account_json)
                    return credentials.Certificate(service_account_dict)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid service account JSON: {e}")
                    raise ValueError("Invalid service account JSON format")
            
            # Method 3: Look for default service account file in project
            default_paths = [
                'service-account-key.json',
                'firebase-service-account.json',
                os.path.join(os.path.dirname(__file__), '..', 'service-account-key.json'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'service-account-key.json'),
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    logger.info(f"Using default service account key file: {path}")
                    return credentials.Certificate(path)
            
            # Method 4: Use Application Default Credentials (for Google Cloud environments)
            try:
                logger.info("Using Application Default Credentials")
                return credentials.ApplicationDefault()
            except Exception as e:
                logger.warning(f"Application Default Credentials not available: {e}")
            
            # If no credentials found, raise error
            raise ValueError(
                "No Firebase credentials found. Please provide either:\n"
                "1. FIREBASE_SERVICE_ACCOUNT_KEY_PATH environment variable\n"
                "2. FIREBASE_SERVICE_ACCOUNT_JSON environment variable\n"
                "3. service-account-key.json file in project directory\n"
                "4. Application Default Credentials (for Google Cloud)"
            )
            
        except Exception as e:
            logger.error(f"Error getting Firebase credentials: {e}")
            raise
    
    def initialize_app(self, app_name: str = '[DEFAULT]') -> firebase_admin.App:
        """
        Initialize Firebase Admin SDK app
        
        Args:
            app_name: Name for the Firebase app instance
            
        Returns:
            Firebase app instance
            
        Raises:
            FirebaseError: If initialization fails
        """
        if self._initialized and self._app:
            logger.info("Firebase app already initialized")
            return self._app
        
        try:
            # Check if app already exists
            try:
                existing_app = firebase_admin.get_app(app_name)
                if existing_app:
                    logger.info(f"Firebase app '{app_name}' already exists")
                    self._app = existing_app
                    self._initialized = True
                    return existing_app
            except ValueError:
                # App doesn't exist, continue with initialization
                pass
            
            # Get credentials
            cred = self.get_credentials()
            
            # Prepare configuration
            config = {
                'databaseURL': self.database_url,
            }
            
            if self.storage_bucket:
                config['storageBucket'] = self.storage_bucket
            
            # Initialize Firebase app
            logger.info(f"Initializing Firebase app '{app_name}' with project: {self.project_id}")
            self._app = firebase_admin.initialize_app(
                cred, 
                config, 
                name=app_name
            )
            
            self._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
            
            # Test connection
            if self._test_connection():
                logger.info("Firebase connection test successful")
            else:
                logger.warning("Firebase connection test failed")
            
            return self._app
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase app: {e}")
            raise FirebaseError(f"Firebase initialization failed: {str(e)}")
    
    def _test_connection(self) -> bool:
        """
        Test Firebase connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self._app:
                return False
            
            # Test database connection
            ref = db.reference('/.info/connected', app=self._app)
            connected = ref.get()
            
            if connected is not None:
                logger.debug("Database connection test successful")
                return True
            
        except Exception as e:
            logger.warning(f"Firebase connection test failed: {e}")
        
        return False
    
    def get_database_reference(self, path: str = '') -> db.Reference:
        """
        Get database reference for specified path
        
        Args:
            path: Database path (e.g., 'home_automation/devices')
            
        Returns:
            Firebase database reference
            
        Raises:
            RuntimeError: If Firebase app not initialized
        """
        if not self._initialized or not self._app:
            raise RuntimeError("Firebase app not initialized. Call initialize_app() first.")
        
        try:
            if path:
                return db.reference(path, app=self._app)
            else:
                return db.reference(app=self._app)
        except Exception as e:
            logger.error(f"Error getting database reference for path '{path}': {e}")
            raise
    
    def get_auth_client(self):
        """
        Get Firebase Auth client
        
        Returns:
            Firebase Auth client
            
        Raises:
            RuntimeError: If Firebase app not initialized
        """
        if not self._initialized or not self._app:
            raise RuntimeError("Firebase app not initialized. Call initialize_app() first.")
        
        return auth
    
    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token to verify
            
        Returns:
            Decoded token data
            
        Raises:
            auth.InvalidIdTokenError: If token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token, app=self._app)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create custom token for user
        
        Args:
            uid: User ID
            additional_claims: Additional claims to include in token
            
        Returns:
            Custom token string
        """
        try:
            token = auth.create_custom_token(
                uid, 
                additional_claims, 
                app=self._app
            )
            return token.decode('utf-8') if isinstance(token, bytes) else token
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            raise
    
    def get_user(self, uid: str):
        """
        Get user by UID
        
        Args:
            uid: User ID
            
        Returns:
            UserRecord object
        """
        try:
            return auth.get_user(uid, app=self._app)
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {e}")
            raise
    
    def set_custom_claims(self, uid: str, claims: Dict[str, Any]) -> None:
        """
        Set custom claims for user
        
        Args:
            uid: User ID
            claims: Custom claims dictionary
        """
        try:
            auth.set_custom_user_claims(uid, claims, app=self._app)
            logger.info(f"Custom claims set for user {uid}")
        except Exception as e:
            logger.error(f"Failed to set custom claims for user {uid}: {e}")
            raise
    
    def validate_configuration(self) -> Dict[str, bool]:
        """
        Validate Firebase configuration
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'project_id': bool(self.project_id),
            'database_url': bool(self.database_url),
            'credentials': False,
            'connection': False
        }
        
        # Check credentials
        try:
            self.get_credentials()
            validation_results['credentials'] = True
        except Exception as e:
            logger.error(f"Credentials validation failed: {e}")
        
        # Check connection (if initialized)
        if self._initialized:
            validation_results['connection'] = self._test_connection()
        
        return validation_results
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get complete Firebase configuration
        
        Returns:
            Configuration dictionary
        """
        return {
            'apiKey': self.api_key,
            'authDomain': self.auth_domain,
            'databaseURL': self.database_url,
            'projectId': self.project_id,
            'storageBucket': self.storage_bucket,
            'timeout': self.timeout,
            'retryCount': self.retry_count,
            'initialized': self._initialized
        }
    
    def cleanup(self) -> None:
        """Clean up Firebase app instance"""
        try:
            if self._app and self._initialized:
                firebase_admin.delete_app(self._app)
                logger.info("Firebase app cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up Firebase app: {e}")
        finally:
            self._app = None
            self._initialized = False
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

class FirebaseManager:
    """
    Firebase manager singleton for handling global Firebase operations
    """
    
    _instance: Optional['FirebaseManager'] = None
    _config: Optional[FirebaseConfig] = None
    
    def __new__(cls) -> 'FirebaseManager':
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = FirebaseConfig()
    
    @property
    def config(self) -> FirebaseConfig:
        """Get Firebase configuration"""
        return self._config
    
    def initialize(self, app_name: str = '[DEFAULT]') -> firebase_admin.App:
        """Initialize Firebase app"""
        return self._config.initialize_app(app_name)
    
    def get_db_ref(self, path: str = '') -> db.Reference:
        """Get database reference"""
        return self._config.get_database_reference(path)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify ID token"""
        return self._config.verify_id_token(token)
    
    def is_initialized(self) -> bool:
        """Check if Firebase is initialized"""
        return self._config._initialized
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration"""
        return self._config.validate_configuration()

# Global Firebase manager instance
firebase_manager = FirebaseManager()

# Utility functions for easy access
def get_firebase_config() -> FirebaseConfig:
    """Get Firebase configuration instance"""
    return firebase_manager.config

def initialize_firebase(app_name: str = '[DEFAULT]') -> firebase_admin.App:
    """Initialize Firebase app"""
    return firebase_manager.initialize(app_name)

def get_db_reference(path: str = '') -> db.Reference:
    """Get database reference for path"""
    return firebase_manager.get_db_ref(path)

def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Verify Firebase ID token"""
    return firebase_manager.verify_token(token)

def is_firebase_initialized() -> bool:
    """Check if Firebase is initialized"""
    return firebase_manager.is_initialized()

# Configuration validation on module import
def _validate_environment():
    """Validate environment variables on import"""
    required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

# Environment setup examples for different deployment scenarios
ENVIRONMENT_EXAMPLES = {
    'development': {
        'description': 'Local development with service account key file',
        'env_vars': {
            'FIREBASE_PROJECT_ID': 'your-project-id',
            'FIREBASE_DATABASE_URL': 'https://your-project-default-rtdb.firebaseio.com/',
            'FIREBASE_SERVICE_ACCOUNT_KEY_PATH': './service-account-key.json'
        }
    },
    'production': {
        'description': 'Production with environment-based service account',
        'env_vars': {
            'FIREBASE_PROJECT_ID': 'your-project-id',
            'FIREBASE_DATABASE_URL': 'https://your-project-default-rtdb.firebaseio.com/',
            'FIREBASE_SERVICE_ACCOUNT_JSON': '{"type": "service_account", ...}'
        }
    },
    'cloud_run': {
        'description': 'Google Cloud Run with Application Default Credentials',
        'env_vars': {
            'FIREBASE_PROJECT_ID': 'your-project-id',
            'FIREBASE_DATABASE_URL': 'https://your-project-default-rtdb.firebaseio.com/',
            # No service account needed - uses ADC
        }
    }
}

# Export main components
__all__ = [
    'FirebaseConfig',
    'FirebaseManager',
    'firebase_manager',
    'get_firebase_config',
    'initialize_firebase',
    'get_db_reference',
    'verify_firebase_token',
    'is_firebase_initialized',
    'ENVIRONMENT_EXAMPLES'
]

# Initialize on import if environment is valid
if _validate_environment():
    logger.info("Firebase configuration loaded successfully")
else:
    logger.warning("Firebase configuration incomplete - some features may not work")

logger.info(f"Firebase config module loaded - Environment: {os.environ.get('FLASK_ENV', 'development')}")
