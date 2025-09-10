"""
Firebase client for Raspberry Pi Pico W
Handles authentication and data operations with Firebase
"""

import urequests
import json
import time
import gc

class FirebaseClient:
    def __init__(self, config):
        self.api_key = config['apiKey']
        self.database_url = config['databaseURL']
        self.auth_email = config.get('deviceEmail')
        self.auth_password = config.get('devicePassword')
        self.auth_token = None
        self.token_expires = 0
        
    def authenticate(self):
        """Authenticate with Firebase using email/password"""
        if self.auth_token and time.time() < self.token_expires:
            return True
            
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        
        payload = {
            "email": self.auth_email,
            "password": self.auth_password,
            "returnSecureToken": True
        }
        
        try:
            print("Authenticating with Firebase...")
            response = urequests.post(
                auth_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data['idToken']
                expires_in = int(auth_data.get('expiresIn', 3600))
                self.token_expires = time.time() + expires_in - 300  # Refresh 5 min early
                
                print("Firebase authentication successful")
                response.close()
                return True
            else:
                print(f"Authentication failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    pass
                response.close()
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def _make_authenticated_request(self, method, path, data=None):
        """Make authenticated request to Firebase"""
        if not self.authenticate():
            return None
            
        url = f"{self.database_url}{path}.json?auth={self.auth_token}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = urequests.get(url, headers=headers)
            elif method == 'PUT':
                response = urequests.put(url, data=json.dumps(data), headers=headers)
            elif method == 'PATCH':
                response = urequests.patch(url, data=json.dumps(data), headers=headers)
            elif method == 'POST':
                response = urequests.post(url, data=json.dumps(data), headers=headers)
            else:
                return None
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    response.close()
                    return result
                except:
                    response.close()
                    return True
            else:
                print(f"Request failed: {response.status_code}")
                response.close()
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def get_relay_commands(self, device_id):
        """Get relay commands from Firebase"""
        path = f"/home_automation/devices/{device_id}/relays"
        return self._make_authenticated_request('GET', path)
    
    def update_relay_states(self, device_id, relay_states):
        """Update relay states in Firebase"""
        path = f"/home_automation/devices/{device_id}/relays"
        return self._make_authenticated_request('PATCH', path, relay_states)
    
    def update_device_data(self, device_id, device_data):
        """Update complete device data in Firebase"""
        path = f"/home_automation/devices/{device_id}"
        return self._make_authenticated_request('PATCH', path, device_data)
    
    def update_device_status(self, device_id, status_data):
        """Update device status in Firebase"""
        path = f"/home_automation/devices/{device_id}"
        return self._make_authenticated_request('PATCH', path, status_data)
    
    def update_device_timestamp(self, device_id):
        """Update device last_update timestamp"""
        timestamp_data = {'last_update': str(time.time())}
        path = f"/home_automation/devices/{device_id}"
        return self._make_authenticated_request('PATCH', path, timestamp_data)
    
    def log_error(self, device_id, error_data):
        """Log error to Firebase"""
        path = f"/home_automation/devices/{device_id}/logs"
        return self._make_authenticated_request('POST', path, error_data)
    
    def get_device_commands(self, device_id):
        """Get pending commands for device"""
        path = f"/home_automation/devices/{device_id}/commands"
        return self._make_authenticated_request('GET', path)
    
    def clear_device_command(self, device_id, command_id):
        """Clear a processed command"""
        path = f"/home_automation/devices/{device_id}/commands/{command_id}"
        return self._make_authenticated_request('DELETE', path)
