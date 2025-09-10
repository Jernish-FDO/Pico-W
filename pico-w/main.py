"""
Smart Home Automation - Raspberry Pi Pico W Controller
Advanced GPIO relay control with Firebase integration
"""

import network
import time
import json
import gc
from machine import Pin, reset, unique_id
import ubinascii
import urequests
from firebase_client import FirebaseClient
from relay_controller import RelayController
from config import Config

class HomeAutomationController:
    def __init__(self):
        # Device identification
        self.device_id = Config.DEVICE_ID
        self.mac_address = ubinascii.hexlify(unique_id()).decode()
        
        # Initialize components
        self.firebase = FirebaseClient(Config.FIREBASE_CONFIG)
        self.relay_controller = RelayController(Config.RELAY_PINS)
        
        # Network and status
        self.wlan = None
        self.connected = False
        self.last_sync = 0
        self.sync_interval = Config.SYNC_INTERVAL
        self.heartbeat_interval = Config.HEARTBEAT_INTERVAL
        self.last_heartbeat = 0
        
        # System monitoring
        self.start_time = time.time()
        self.error_count = 0
        self.max_errors = Config.MAX_ERRORS
        
        print(f"Home Automation Controller initialized")
        print(f"Device ID: {self.device_id}")
        print(f"MAC Address: {self.mac_address}")
    
    def connect_wifi(self):
        """Connect to WiFi network with retry logic"""
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        if self.wlan.isconnected():
            print(f"Already connected to WiFi: {self.wlan.ifconfig()[0]}")
            return True
        
        print(f"Connecting to WiFi: {Config.WIFI_SSID}")
        self.wlan.connect(Config.WIFI_SSID, Config.WIFI_PASSWORD)
        
        # Wait for connection with timeout
        timeout = 30
        while not self.wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        
        if self.wlan.isconnected():
            ip_info = self.wlan.ifconfig()
            print(f"\nWiFi connected successfully!")
            print(f"IP Address: {ip_info[0]}")
            print(f"Subnet Mask: {ip_info[1]}")
            print(f"Gateway: {ip_info[2]}")
            print(f"DNS: {ip_info[3]}")
            
            self.connected = True
            return True
        else:
            print("\nWiFi connection failed!")
            self.connected = False
            return False
    
    def initialize_device_data(self):
        """Initialize device data in Firebase"""
        try:
            device_data = {
                'name': f'Pico W Controller {self.device_id}',
                'type': 'raspberry_pi_pico_w',
                'firmware_version': Config.FIRMWARE_VERSION,
                'mac_address': self.mac_address,
                'ip_address': self.wlan.ifconfig()[0] if self.wlan else None,
                'online': True,
                'created_at': self.get_iso_timestamp(),
                'last_update': self.get_iso_timestamp(),
                'uptime': 0,
                'system_load': 0,
                'memory_usage': 0,
                'wifi_strength': self.get_wifi_strength(),
                'relays': self.relay_controller.get_all_relay_states()
            }
            
            # Update device data in Firebase
            success = self.firebase.update_device_data(self.device_id, device_data)
            if success:
                print("Device data initialized in Firebase")
            else:
                print("Failed to initialize device data")
                
            return success
            
        except Exception as e:
            print(f"Error initializing device data: {e}")
            return False
    
    def sync_with_firebase(self):
        """Synchronize relay states with Firebase"""
        try:
            # Get current relay commands from Firebase
            commands = self.firebase.get_relay_commands(self.device_id)
            
            if commands:
                changes_made = False
                
                for relay_id, command_data in commands.items():
                    if isinstance(command_data, dict) and 'status' in command_data:
                        new_status = bool(command_data['status'])
                        current_status = self.relay_controller.get_relay_status(relay_id)
                        
                        if current_status != new_status:
                            print(f"Updating {relay_id}: {current_status} -> {new_status}")
                            self.relay_controller.set_relay(relay_id, new_status)
                            changes_made = True
                
                if changes_made:
                    # Update relay states in Firebase
                    updated_states = self.relay_controller.get_all_relay_states()
                    self.firebase.update_relay_states(self.device_id, updated_states)
                    
                    # Update device timestamp
                    self.firebase.update_device_timestamp(self.device_id)
            
            # Reset error count on successful sync
            self.error_count = 0
            
        except Exception as e:
            print(f"Sync error: {e}")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                print(f"Max errors ({self.max_errors}) reached, restarting...")
                time.sleep(5)
                reset()
    
    def send_heartbeat(self):
        """Send heartbeat and system status to Firebase"""
        try:
            uptime = time.time() - self.start_time
            memory_info = gc.mem_alloc(), gc.mem_free()
            memory_usage = (memory_info[0] / (memory_info[0] + memory_info[1])) * 100
            
            status_data = {
                'online': True,
                'last_update': self.get_iso_timestamp(),
                'uptime': int(uptime),
                'memory_usage': round(memory_usage, 2),
                'wifi_strength': self.get_wifi_strength(),
                'error_count': self.error_count,
                'free_memory': memory_info[1],
                'used_memory': memory_info[0]
            }
            
            success = self.firebase.update_device_status(self.device_id, status_data)
            if success:
                print(f"Heartbeat sent - Uptime: {int(uptime)}s, Memory: {memory_usage:.1f}%")
            
        except Exception as e:
            print(f"Heartbeat error: {e}")
            self.error_count += 1
    
    def get_wifi_strength(self):
        """Get WiFi signal strength"""
        try:
            if self.wlan and self.wlan.isconnected():
                return self.wlan.status('rssi')
        except:
            pass
        return None
    
    def get_iso_timestamp(self):
        """Get current time in ISO format"""
        # Simple timestamp - in production, consider using RTC
        return str(time.time())
    
    def handle_system_error(self, error):
        """Handle system errors with recovery"""
        print(f"System error: {error}")
        self.error_count += 1
        
        # Log error to Firebase
        try:
            error_data = {
                'timestamp': self.get_iso_timestamp(),
                'error': str(error),
                'uptime': time.time() - self.start_time,
                'free_memory': gc.mem_free()
            }
            self.firebase.log_error(self.device_id, error_data)
        except:
            pass
        
        # Force garbage collection
        gc.collect()
        
        # Restart if too many errors
        if self.error_count >= self.max_errors:
            print("Too many errors, restarting device...")
            self.set_offline_status()
            time.sleep(2)
            reset()
    
    def set_offline_status(self):
        """Set device status to offline in Firebase"""
        try:
            self.firebase.update_device_status(self.device_id, {
                'online': False,
                'last_update': self.get_iso_timestamp()
            })
        except:
            pass
    
    def emergency_stop(self):
        """Emergency stop - turn off all relays"""
        print("EMERGENCY STOP - Turning off all relays")
        try:
            self.relay_controller.turn_off_all_relays()
            # Log emergency stop
            self.firebase.log_error(self.device_id, {
                'timestamp': self.get_iso_timestamp(),
                'event': 'emergency_stop',
                'reason': 'system_shutdown'
            })
        except Exception as e:
            print(f"Error in emergency stop: {e}")
    
    def run(self):
        """Main control loop"""
        print("Starting Home Automation Controller...")
        
        try:
            # Initialize WiFi connection
            if not self.connect_wifi():
                print("Failed to connect to WiFi, restarting...")
                time.sleep(10)
                reset()
            
            # Initialize Firebase authentication
            if not self.firebase.authenticate():
                print("Firebase authentication failed, restarting...")
                time.sleep(10)
                reset()
            
            # Initialize device data
            if not self.initialize_device_data():
                print("Failed to initialize device data")
            
            # Initialize all relays to OFF state
            self.relay_controller.initialize_relays()
            
            print("Controller running successfully!")
            print("Press Ctrl+C to stop")
            
            # Main control loop
            while True:
                current_time = time.ticks_ms()
                
                # Check WiFi connection
                if not self.wlan.isconnected():
                    print("WiFi disconnected, attempting reconnection...")
                    if not self.connect_wifi():
                        time.sleep(5)
                        continue
                
                # Periodic sync with Firebase
                if time.ticks_diff(current_time, self.last_sync) >= self.sync_interval:
                    self.sync_with_firebase()
                    self.last_sync = current_time
                    gc.collect()  # Manage memory
                
                # Send heartbeat
                if time.ticks_diff(current_time, self.last_heartbeat) >= self.heartbeat_interval:
                    self.send_heartbeat()
                    self.last_heartbeat = current_time
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutdown requested...")
            self.emergency_stop()
            self.set_offline_status()
            print("Controller stopped")
            
        except Exception as e:
            self.handle_system_error(e)
            
        finally:
            # Cleanup
            try:
                self.set_offline_status()
            except:
                pass

# Main execution
if __name__ == "__main__":
    try:
        controller = HomeAutomationController()
        controller.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        time.sleep(5)
        reset()
