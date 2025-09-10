"""
Firebase Authentication Middleware
Handles JWT token verification and user authentication
"""

import firebase_admin
from firebase_admin import credentials, auth, db
from flask import request, jsonify, g
from functools import wraps
import os
import logging

logger = logging.getLogger(__name__)

def init_firebase_admin():
    """Initialize Firebase Admin SDK"""
    try:
        # Initialize Firebase Admin with service account
        if not firebase_admin._apps:
            # For development, use service account key file
            if os.path.exists('service-account-key.json'):
                cred = credentials.Certificate('service-account-key.json')
            else:
                # For production, use environment variables
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 
                    'https://your-project-default-rtdb.firebaseio.com')
            })
        
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise

def get_auth_token():
    """Extract Firebase auth token from request headers"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        return token
    except IndexError:
        return None

def verify_firebase_token(token):
    """Verify Firebase ID token and return user info"""
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        
        # Get additional user info
        user_record = auth.get_user(decoded_token['uid'])
        
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'email_verified': decoded_token.get('email_verified', False),
            'name': decoded_token.get('name'),
            'picture': decoded_token.get('picture'),
            'custom_claims': user_record.custom_claims or {},
            'provider_id': decoded_token.get('firebase', {}).get('sign_in_provider'),
            'auth_time': decoded_token.get('auth_time'),
            'exp': decoded_token.get('exp')
        }
    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase ID token")
        return None
    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase ID token")
        return None
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        return None

def require_auth(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_token()
        
        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'No authentication token provided'
            }), 401
        
        user_info = verify_firebase_token(token)
        
        if not user_info:
            return jsonify({
                'error': 'Invalid token',
                'message': 'Authentication token is invalid or expired'
            }), 401
        
        # Store user info in Flask's g object for use in route handlers
        g.current_user = user_info
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({
                'error': 'Authentication required',
                'message': 'No authentication token provided'
            }), 401
        
        user_role = g.current_user.get('custom_claims', {}).get('role', 'user')
        
        if user_role != 'admin':
            return jsonify({
                'error': 'Insufficient permissions',
                'message': 'Admin role required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def check_device_permissions(device_id):
    """Check if current user has permissions for the specified device"""
    if not hasattr(g, 'current_user'):
        return False
    
    user_role = g.current_user.get('custom_claims', {}).get('role', 'user')
    
    # Admins have access to all devices
    if user_role == 'admin':
        return True
    
    # Check user-specific device permissions
    user_devices = g.current_user.get('custom_claims', {}).get('devices', [])
    return device_id in user_devices

def get_user_devices():
    """Get list of devices current user has access to"""
    if not hasattr(g, 'current_user'):
        return []
    
    user_role = g.current_user.get('custom_claims', {}).get('role', 'user')
    
    # Admins have access to all devices
    if user_role == 'admin':
        return ['*']  # Wildcard for all devices
    
    # Return user-specific device list
    return g.current_user.get('custom_claims', {}).get('devices', [])

def log_user_action(action, resource, details=None):
    """Log user actions for audit trail"""
    if hasattr(g, 'current_user'):
        log_entry = {
            'timestamp': firebase_admin.firestore.SERVER_TIMESTAMP,
            'user_id': g.current_user['uid'],
            'user_email': g.current_user.get('email'),
            'action': action,
            'resource': resource,
            'details': details or {},
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        try:
            # Log to Firebase Realtime Database
            log_ref = db.reference('audit_logs').push()
            log_ref.set(log_entry)
        except Exception as e:
            logger.error(f"Failed to log user action: {e}")
