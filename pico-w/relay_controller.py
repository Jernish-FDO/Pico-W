"""
Relay Controller for Raspberry Pi Pico W
Manages GPIO pins for relay control with safety features
"""

from machine import Pin
import time

class RelayController:
    def __init__(self, relay_pins):
        self.relay_pins = relay_pins
        self.relays = {}
        self.relay_states = {}
        self.safety_enabled = True
        
        # Initialize GPIO pins
        for i, pin_num in enumerate(relay_pins):
            relay_id = f"relay_{i+1}"
            
            # Initialize pin as output (active low for most relay modules)
            pin = Pin(pin_num, Pin.OUT)
            pin.value(1)  # Start with relay OFF (active low)
            
            self.relays[relay_id] = {
                'pin': pin,
                'pin_number': pin_num,
                'name': f"Relay {i+1}",
                'status': False,
                'last_changed': None,
                'switch_count': 0,
                'total_runtime': 0,
                'power_usage': 0
            }
            
            self.relay_states[relay_id] = False
        
        print(f"Relay controller initialized with {len(self.relays)} relays")
    
    def initialize_relays(self):
        """Initialize all relays to OFF state"""
        print("Initializing all relays to OFF state...")
        for relay_id in self.relays:
            self.set_relay(relay_id, False, update_firebase=False)
        print("All relays initialized")
    
    def set_relay(self, relay_id, status, update_firebase=True):
        """Set individual relay state with safety checks"""
        if relay_id not in self.relays:
            print(f"Warning: Relay {relay_id} not found")
            return False
        
        try:
            new_status = bool(status)
            relay = self.relays[relay_id]
            current_status = self.relay_states[relay_id]
            
            # Safety check
            if self.safety_enabled and self._safety_check(relay_id, new_status):
                print(f"Safety check failed for {relay_id}")
                return False
            
            # Update GPIO pin (active low: 0 = ON, 1 = OFF)
            relay['pin'].value(0 if new_status else 1)
            
            # Update internal state
            self.relay_states[relay_id] = new_status
            relay['status'] = new_status
            relay['last_changed'] = time.time()
            
            # Increment switch count if status changed
            if current_status != new_status:
                relay['switch_count'] += 1
            
            # Update power usage estimation (placeholder - implement based on load)
            relay['power_usage'] = self._estimate_power_usage(relay_id, new_status)
            
            print(f"{relay_id} ({'ON' if new_status else 'OFF'}): Pin {relay['pin_number']}")
            return True
            
        except Exception as e:
            print(f"Error setting {relay_id}: {e}")
            return False
    
    def get_relay_status(self, relay_id):
        """Get current status of a relay"""
        return self.relay_states.get(relay_id, False)
    
    def get_all_relay_states(self):
        """Get all relay states in Firebase format"""
        states = {}
        for relay_id, relay in self.relays.items():
            states[relay_id] = {
                'status': self.relay_states[relay_id],
                'name': relay['name'],
                'last_changed': relay['last_changed'],
                'switch_count': relay['switch_count'],
                'power_usage': relay['power_usage'],
                'pin_number': relay['pin_number']
            }
        return states
    
    def turn_off_all_relays(self):
        """Emergency function to turn off all relays"""
        print("EMERGENCY: Turning off all relays")
        for relay_id in self.relays:
            try:
                self.relays[relay_id]['pin'].value(1)  # OFF state
                self.relay_states[relay_id] = False
                self.relays[relay_id]['status'] = False
            except Exception as e:
                print(f"Error turning off {relay_id}: {e}")
    
    def toggle_relay(self, relay_id):
        """Toggle relay state"""
        current_status = self.get_relay_status(relay_id)
        return self.set_relay(relay_id, not current_status)
    
    def get_active_relay_count(self):
        """Get number of currently active relays"""
        return sum(1 for status in self.relay_states.values() if status)
    
    def get_relay_info(self, relay_id):
        """Get detailed information about a specific relay"""
        if relay_id not in self.relays:
            return None
        
        relay = self.relays[relay_id]
        return {
            'relay_id': relay_id,
            'name': relay['name'],
            'status': self.relay_states[relay_id],
            'pin_number': relay['pin_number'],
            'last_changed': relay['last_changed'],
            'switch_count': relay['switch_count'],
            'power_usage': relay['power_usage'],
            'total_runtime': relay['total_runtime']
        }
    
    def _safety_check(self, relay_id, new_status):
        """Perform safety checks before changing relay state"""
        # Example safety checks:
        
        # 1. Check if too many relays would be active
        if new_status:
            active_count = self.get_active_relay_count()
            if active_count >= 12:  # Max 12 active relays
                print(f"Safety: Too many active relays ({active_count})")
                return True
        
        # 2. Check rapid switching (prevent relay damage)
        relay = self.relays[relay_id]
        if relay['last_changed']:
            time_since_change = time.time() - relay['last_changed']
            if time_since_change < 1.0:  # Minimum 1 second between switches
                print(f"Safety: Rapid switching prevented for {relay_id}")
                return True
        
        # 3. Check switch count (prevent relay wear)
        if relay['switch_count'] > 10000:  # Example limit
            print(f"Safety: Switch count limit reached for {relay_id}")
            return True
        
        return False
    
    def _estimate_power_usage(self, relay_id, status):
        """Estimate power usage for relay (placeholder implementation)"""
        if not status:
            return 0
        
        # Placeholder: different relays might control different loads
        # In real implementation, you might use current sensors
        power_ratings = {
            'relay_1': 100,   # 100W light
            'relay_2': 75,    # 75W fan
            'relay_3': 1500,  # 1.5kW heater
            'relay_4': 200,   # 200W pump
        }
        
        return power_ratings.get(relay_id, 50)  # Default 50W
    
    def enable_safety_mode(self, enabled=True):
        """Enable or disable safety checks"""
        self.safety_enabled = enabled
        print(f"Safety mode {'enabled' if enabled else 'disabled'}")
    
    def get_system_status(self):
        """Get overall system status"""
        active_count = self.get_active_relay_count()
        total_power = sum(relay['power_usage'] for relay in self.relays.values())
        
        return {
            'total_relays': len(self.relays),
            'active_relays': active_count,
            'inactive_relays': len(self.relays) - active_count,
            'total_power_usage': total_power,
            'safety_enabled': self.safety_enabled
        }
