import network
import time
import json
import urequests
from machine import Pin
import gc
from firebase_config import FIREBASE_CONFIG, WIFI_CONFIG

class HomeAutomationController:
    def __init__(self):
        # Initialize GPIO pins for 16 relays
        self.relays = {}
        self.relay_pins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        
        for i, pin_num in enumerate(self.relay_pins):
            relay_id = f"relay_{i+1}"
            self.relays[relay_id] = {
                'pin': Pin(pin_num, Pin.OUT),
                'status': False,
                'name': f"Device {i+1}"
            }
            # Initialize all relays to OFF state (active low)
            self.relays[relay_id]['pin'].value(1)
        
        self.device_id = "pico_w_001"
        self.firebase_url = FIREBASE_CONFIG['databaseURL']
        self.api_key = FIREBASE_CONFIG['apiKey']
        self.auth_token = None
        self.last_sync = 0
        self.sync_interval = 500  # 2 seconds
        
    def connect_wifi(self):
        """Connect to WiFi network"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f"Connecting to WiFi: {WIFI_CONFIG['ssid']}")
            wlan.connect(WIFI_CONFIG['ssid'], WIFI_CONFIG['password'])
            
            timeout = 30
            while not wlan.isconnected() and timeout > 0:
                print(".", end="")
                time.sleep(1)
                timeout -= 1
            
            if wlan.isconnected():
                print(f"\nWiFi connected: {wlan.ifconfig()[0]}")
                return True
            else:
                print("\nWiFi connection failed!")
                return False
        return True
    
    def authenticate(self):
        """Authenticate with Firebase using device credentials"""
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        
        payload = {
            "email": FIREBASE_CONFIG['deviceEmail'],
            "password": FIREBASE_CONFIG['devicePassword'],
            "returnSecureToken": True
        }
        
        try:
            response = urequests.post(auth_url, 
                                    data=json.dumps(payload), 
                                    headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data['idToken']
                print("Firebase authentication successful")
                return True
            else:
                print(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
        finally:
            if 'response' in locals():
                response.close()
    
    def update_device_status(self):
        """Update device online status in Firebase"""
        if not self.auth_token:
            return False
            
        status_url = f"{self.firebase_url}/home_automation/devices/{self.device_id}/online.json?auth={self.auth_token}"
        
        try:
            response = urequests.put(status_url, 
                                   data=json.dumps(True), 
                                   headers={'Content-Type': 'application/json'})
            return response.status_code == 200
        except Exception as e:
            print(f"Status update error: {e}")
            return False
        finally:
            if 'response' in locals():
                response.close()
    
    def sync_with_firebase(self):
        """Synchronize relay states with Firebase"""
        if not self.auth_token:
            return
            
        # Fetch current states from Firebase
        relays_url = f"{self.firebase_url}/home_automation/devices/{self.device_id}/relays.json?auth={self.auth_token}"
        
        try:
            response = urequests.get(relays_url)
            
            if response.status_code == 200:
                firebase_data = response.json()
                
                if firebase_data:
                    changes_made = False
                    for relay_id, relay_data in firebase_data.items():
                        if relay_id in self.relays:
                            new_status = relay_data.get('status', False)
                            if self.relays[relay_id]['status'] != new_status:
                                self.set_relay(relay_id, new_status)
                                changes_made = True
                    
                    if changes_made:
                        self.update_last_sync()
        except Exception as e:
            print(f"Sync error: {e}")
        finally:
            if 'response' in locals():
                response.close()
    
    def set_relay(self, relay_id, status):
        """Set individual relay state"""
        if relay_id in self.relays:
            self.relays[relay_id]['status'] = status
            # Active low: 0 = ON, 1 = OFF
            self.relays[relay_id]['pin'].value(1 if status else 0)
            print(f"{relay_id}: {'ON' if status else 'OFF'}")
    
    def update_last_sync(self):
        """Update last synchronization timestamp"""
        if not self.auth_token:
            return
            
        timestamp_url = f"{self.firebase_url}/home_automation/devices/{self.device_id}/last_update.json?auth={self.auth_token}"
        timestamp = time.time()
        
        try:
            response = urequests.put(timestamp_url, 
                                   data=json.dumps(timestamp), 
                                   headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Timestamp update error: {e}")
        finally:
            if 'response' in locals():
                response.close()
    
    def run(self):
        """Main control loop"""
        print("Starting Home Automation Controller...")
        
        # Initialize connection
        if not self.connect_wifi():
            return
            
        if not self.authenticate():
            return
            
        self.update_device_status()
        
        print("Controller running. Press Ctrl+C to stop.")
        
        try:
            while True:
                current_time = time.ticks_ms()
                
                # Periodic sync with Firebase
                if time.ticks_diff(current_time, self.last_sync) >= self.sync_interval:
                    self.sync_with_firebase()
                    self.last_sync = current_time
                    gc.collect()  # Memory management
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nShutting down controller...")
            # Turn off all relays on shutdown
            for relay_id in self.relays:
                self.set_relay(relay_id, False)
            
            # Update offline status
            offline_url = f"{self.firebase_url}/home_automation/devices/{self.device_id}/online.json?auth={self.auth_token}"
            try:
                urequests.put(offline_url, data=json.dumps(False))
            except:
                pass

# Start the controller
if __name__ == "__main__":
    controller = HomeAutomationController()
    controller.run()

