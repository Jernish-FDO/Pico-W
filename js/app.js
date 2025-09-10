// js/app.js

import { auth, database } from './firebase-config.js';

const DEVICE_ID = 'pico_w_001';
const RELAY_NAMES = [
    'Living Room Light', 'Kitchen Fan', 'Bedroom AC', 'Garden Pump',
    'Garage Door', 'Pool Pump', 'Security Light', 'Bathroom Fan',
    'Washing Machine', 'Dryer', 'Water Heater', 'Outdoor Light',
    'Workshop Light', 'Shed Power', 'Irrigation System', 'Backup Power'
];
// (The code that was previously failing will now find RELAY_NAMES and work)

class HomeAutomationApp {
    constructor() {
        this.relayStates = {};
        this.deviceOnline = false;
        this.lastUpdate = null;
        this.relayContainer = document.getElementById('relay-container');
        this.connectionStatus = document.getElementById('connection-status');
        
        this.setupEventListeners();
        this.createRelayControls();
    }
    
    init() {
        console.log('Initializing Home Automation App...');
        this.setupFirebaseListeners();
        this.loadRelayStates();
    }
    
    setupEventListeners() {
        // Quick action buttons
        document.getElementById('all-on-btn').addEventListener('click', () => {
            this.setAllRelays(true);
        });
        
        document.getElementById('all-off-btn').addEventListener('click', () => {
            this.setAllRelays(false);
        });
        
        document.getElementById('toggle-all-btn').addEventListener('click', () => {
            this.toggleAllRelays();
        });
    }
    
    createRelayControls() {
        this.relayContainer.innerHTML = '';
        
        for (let i = 1; i <= 16; i++) {
            const relayId = `relay_${i}`;
            const relayName = RELAY_NAMES[i - 1] || `Device ${i}`;
            
            const relayCard = document.createElement('div');
            relayCard.className = 'bg-gray-700 rounded-lg p-4 transition-all duration-300 hover:bg-gray-600';
            relayCard.innerHTML = `
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-sm">${relayName}</h3>
                    <span class="text-xs text-gray-400">${relayId.toUpperCase()}</span>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="fas fa-power-off text-lg mr-2 text-gray-400" id="icon-${relayId}"></i>
                        <span class="text-sm" id="status-${relayId}">OFF</span>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" id="toggle-${relayId}" class="sr-only peer" 
                               onchange="homeAutomationApp.toggleRelay('${relayId}')">
                        <div class="w-11 h-6 bg-gray-500 peer-focus:outline-none peer-focus:ring-4 
                                   peer-focus:ring-blue-300 rounded-full peer 
                                   peer-checked:after:translate-x-full peer-checked:after:border-white 
                                   after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                                   after:bg-white after:rounded-full after:h-5 after:w-5 
                                   after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                </div>
                <div class="mt-2 text-xs text-gray-400" id="last-changed-${relayId}">
                    Never changed
                </div>
            `;
            
            this.relayContainer.appendChild(relayCard);
            
            // Initialize relay state
            this.relayStates[relayId] = {
                status: false,
                name: relayName,
                lastChanged: null
            };
        }
    }
    
    setupFirebaseListeners() {
        // Listen to device online status
        const deviceRef = database.ref(`home_automation/devices/${DEVICE_ID}`);
        
        deviceRef.child('online').on('value', (snapshot) => {
            this.deviceOnline = snapshot.val() || false;
            this.updateConnectionStatus();
        });
        
        // Listen to relay states
        deviceRef.child('relays').on('value', (snapshot) => {
            const relayData = snapshot.val();
            if (relayData) {
                this.updateRelayStates(relayData);
            }
        });
        
        // Listen to last update timestamp
        deviceRef.child('last_update').on('value', (snapshot) => {
            const timestamp = snapshot.val();
            if (timestamp) {
                this.lastUpdate = new Date(timestamp * 1000);
                this.updateLastUpdateDisplay();
            }
        });
    }
    
    updateConnectionStatus() {
        const statusElement = this.connectionStatus;
        const icon = statusElement.querySelector('i');
        
        if (this.deviceOnline) {
            icon.className = 'fas fa-circle text-green-500';
            statusElement.innerHTML = '<i class="fas fa-circle text-green-500"></i> Connected';
        } else {
            icon.className = 'fas fa-circle text-red-500';
            statusElement.innerHTML = '<i class="fas fa-circle text-red-500"></i> Offline';
        }
    }
    
    updateRelayStates(relayData) {
        let activeCount = 0;
        
        Object.keys(relayData).forEach(relayId => {
            const relay = relayData[relayId];
            const isActive = relay.status || false;
            
            this.relayStates[relayId] = {
                status: isActive,
                name: relay.name || this.relayStates[relayId]?.name || `Device ${relayId.split('_')[1]}`,
                lastChanged: new Date()
            };
            
            if (isActive) activeCount++;
            
            this.updateRelayUI(relayId, isActive);
        });
        
        // Update active count display
        document.getElementById('active-count').textContent = `${activeCount} / 16`;
    }
    
    updateRelayUI(relayId, isActive) {
        const toggle = document.getElementById(`toggle-${relayId}`);
        const icon = document.getElementById(`icon-${relayId}`);
        const status = document.getElementById(`status-${relayId}`);
        const lastChanged = document.getElementById(`last-changed-${relayId}`);
        
        if (toggle) toggle.checked = isActive;
        
        if (icon) {
            icon.className = `fas fa-power-off text-lg mr-2 ${isActive ? 'text-green-500' : 'text-gray-400'}`;
        }
        
        if (status) {
            status.textContent = isActive ? 'ON' : 'OFF';
            status.className = `text-sm ${isActive ? 'text-green-500' : 'text-gray-400'}`;
        }
        
        if (lastChanged) {
            const time = new Date().toLocaleTimeString();
            lastChanged.textContent = `Last changed: ${time}`;
        }
    }
    
    async toggleRelay(relayId) {
        const newStatus = !this.relayStates[relayId].status;
        await this.setRelay(relayId, newStatus);
    }
    
    async setRelay(relayId, status) {
        try {
            const relayRef = database.ref(`home_automation/devices/${DEVICE_ID}/relays/${relayId}/status`);
            await relayRef.set(status);
            
            console.log(`${relayId} set to ${status ? 'ON' : 'OFF'}`);
        } catch (error) {
            console.error(`Error setting ${relayId}:`, error);
            this.showNotification(`Failed to control ${relayId}`, 'error');
        }
    }
    
    async setAllRelays(status) {
        const updates = {};
        
        for (let i = 1; i <= 16; i++) {
            const relayId = `relay_${i}`;
            updates[`home_automation/devices/${DEVICE_ID}/relays/${relayId}/status`] = status;
        }
        
        try {
            await database.ref().update(updates);
            this.showNotification(`All relays turned ${status ? 'ON' : 'OFF'}`, 'success');
        } catch (error) {
            console.error('Error setting all relays:', error);
            this.showNotification('Failed to control all relays', 'error');
        }
    }
    
    async toggleAllRelays() {
        const updates = {};
        
        for (let i = 1; i <= 16; i++) {
            const relayId = `relay_${i}`;
            const currentStatus = this.relayStates[relayId]?.status || false;
            updates[`home_automation/devices/${DEVICE_ID}/relays/${relayId}/status`] = !currentStatus;
        }
        
        try {
            await database.ref().update(updates);
            this.showNotification('All relays toggled', 'success');
        } catch (error) {
            console.error('Error toggling all relays:', error);
            this.showNotification('Failed to toggle all relays', 'error');
        }
    }
    
    loadRelayStates() {
        // Initial load of relay states
        const relaysRef = database.ref(`home_automation/devices/${DEVICE_ID}/relays`);
        relaysRef.once('value', (snapshot) => {
            const relayData = snapshot.val();
            if (relayData) {
                this.updateRelayStates(relayData);
            }
        });
    }
    
    updateLastUpdateDisplay() {
        const element = document.getElementById('last-update');
        if (this.lastUpdate && element) {
            const now = new Date();
            const diffMs = now - this.lastUpdate;
            const diffSecs = Math.floor(diffMs / 1000);
            
            let displayText;
            if (diffSecs < 60) {
                displayText = 'Just now';
            } else if (diffSecs < 3600) {
                displayText = `${Math.floor(diffSecs / 60)}m ago`;
            } else {
                displayText = this.lastUpdate.toLocaleTimeString();
            }
            
            element.textContent = displayText;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create and show notification (you can enhance this)
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // You can implement a proper notification system here
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
            type === 'success' ? 'bg-green-600' : 
            type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }
}

// Initialize the application
window.homeAutomationApp = new HomeAutomationApp();
