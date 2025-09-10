"""
Configuration settings for Home Automation Controller
"""

class Config:
    # Device identification
    DEVICE_ID = 'pico_w_001'
    FIRMWARE_VERSION = '2.0.0'
    
    # WiFi credentials
    WIFI_SSID = 'Your_WiFi_SSID'
    WIFI_PASSWORD = 'Your_WiFi_Password'
    
    # Firebase configuration
    FIREBASE_CONFIG = {
        'apiKey': 'your-api-key',
        'databaseURL': 'https://your-project-default-rtdb.firebaseio.com',
        'deviceEmail': 'device@yourdomain.com',
        'devicePassword': 'secure-device-password'
    }
    
    # GPIO pin assignments for 16 relays
    RELAY_PINS = [
        0, 1, 2, 3, 4, 5, 6, 7,        # Relays 1-8
        8, 9, 10, 11, 12, 13, 14, 15   # Relays 9-16
    ]
    
    # Timing configuration (milliseconds)
    SYNC_INTERVAL = 3000        # 3 seconds
    HEARTBEAT_INTERVAL = 30000  # 30 seconds
    
    # Error handling
    MAX_ERRORS = 10
    
    # Safety settings
    MAX_ACTIVE_RELAYS = 12
    MIN_SWITCH_INTERVAL = 1000  # 1 second minimum between switches
