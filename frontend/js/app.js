class HomeAutomationApp {
    constructor() {
        this.relayStates = new Map();
        this.deviceOnline = false;
        this.apiConnected = false;
        this.lastUpdate = null;
        this.syncInterval = null;
        
        // DOM elements
        this.relayContainer = document.getElementById('relay-container');
        this.connectionStatus = document.getElementById('connection-status');
        this.deviceStatus = document.getElementById('device-status');
        this.activeCount = document.getElementById('active-count');
        this.lastUpdateElement = document.getElementById('last-update');
        this.systemLoad = document.getElementById('system-load');
        this.apiStatus = document.getElementById('api-status');
        
        this.setupEventListeners();
        this.createRelayControls();
    }
    
    async init() {
        console.log('Initializing Home Automation App...');
        
        try {
            // Check API connection
            await this.checkApiConnection();
            
            // Setup Firebase listeners
            this.setupFirebaseListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Start sync interval
            this.startSyncInterval();
            
            console.log('App initialized successfully');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.showNotification('Failed to initialize application', 'error');
        }
    }
    
    async checkApiConnection() {
        try {
            const response = await Utils.apiRequest('/status');
            this.apiConnected = true;
            this.updateApiStatus('Connected to API server', 'success');
        } catch (error) {
            this.apiConnected = false;
            this.updateApiStatus('API server unavailable', 'error');
        }
    }
    
    updateApiStatus(message, type) {
        const statusElement = this.apiStatus;
        const textElement = document.getElementById('api-status-text');
        
        statusElement.classList.remove('hidden');
        textElement.textContent = message;
        
        // Update styling based on status
        statusElement.className = `mb-6 p-4 rounded-lg border glass-effect ${
            type === 'success' ? 'border-green-500 bg-green-900 bg-opacity-20' :
            type === 'error' ? 'border-red-500 bg-red-900 bg-opacity-20' :
            'border-yellow-500 bg-yellow-900 bg-opacity-20'
        }`;
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
        
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshData();
        });
        
        // View toggle buttons
        document.getElementById('grid-view-btn').addEventListener('click', () => {
            this.setViewMode('grid');
        });
        
        document.getElementById('list-view-btn').addEventListener('click', () => {
            this.setViewMode('list');
        });
        
        // User menu toggle
        const userMenuBtn = document.getElementById('user-menu-btn');
        const userMenu = document.getElementById('user-menu');
        
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.classList.toggle('hidden');
        });
        
        document.addEventListener('click', () => {
            userMenu.classList.add('hidden');
        });
    }
    
    createRelayControls() {
        this.relayContainer.innerHTML = '';
        
        for (let i = 1; i <= APP_CONFIG.RELAY_COUNT; i++) {
            const relayId = `relay_${i}`;
            const relayName = RELAY_NAMES[i - 1] || `Device ${i}`;
            
            const relayCard = this.createRelayCard(relayId, relayName, i);
            this.relayContainer.appendChild(relayCard);
            
            // Initialize state
            this.relayStates.set(relayId, {
                status: false,
                name: relayName,
                lastChanged: null,
                powerUsage: 0
            });
        }
    }
    
    createRelayCard(relayId, relayName, index) {
        const card = document.createElement('div');
        card.className = 'bg-gray-700 rounded-xl p-5 border border-gray-600 hover:border-blue-500 transition-all duration-300 transform hover:scale-105 shadow-lg';
        
        card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <div class="w-3 h-3 rounded-full bg-gray-400 mr-3 transition-colors duration-200" id="indicator-${relayId}"></div>
                    <div>
                        <h3 class="font-semibold text-sm text-gray-200">${relayName}</h3>
                        <p class="text-xs text-gray-400">Channel ${index}</p>
                    </div>
                </div>
                <span class="text-xs text-gray-400 bg-gray-600 px-2 py-1 rounded">${relayId.toUpperCase()}</span>
            </div>
            
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <i class="fas fa-power-off text-2xl mr-3 text-gray-400 transition-colors duration-200" id="icon-${relayId}"></i>
                    <div>
                        <div class="flex items-center">
                            <span class="text-lg font-bold mr-2" id="status-${relayId}">OFF</span>
                            <span class="text-xs text-gray-400" id="power-${relayId}">0W</span>
                        </div>
                        <p class="text-xs text-gray-400" id="last-changed-${relayId}">Never changed</p>
                    </div>
                </div>
                
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" id="toggle-${relayId}" class="sr-only peer" 
                           onchange="homeAutomationApp.toggleRelay('${relayId}')">
                    <div class="w-14 h-7 bg-gray-500 peer-focus:outline-none peer-focus:ring-4 
                               peer-focus:ring-blue-300/20 rounded-full peer 
                               peer-checked:after:translate-x-7 peer-checked:after:border-white 
                               after:content-[''] after:absolute after:top-0.5 after:left-[4px] 
                               after:bg-white after:rounded-full after:h-6 after:w-6 
                               after:transition-all after:shadow-sm peer-checked:bg-blue-600
                               hover:shadow-lg transition-all duration-200"></div>
                </label>
            </div>
            
            <div class="space-y-2">
                <div class="flex justify-between text-xs text-gray-400">
                    <span>Usage</span>
                    <span id="usage-percent-${relayId}">0%</span>
                </div>
                <div class="w-full bg-gray-600 rounded-full h-2">
                    <div class="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500" 
                         style="width: 0%" id="usage-bar-${relayId}"></div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    setupFirebaseListeners() {
        const deviceRef = database.ref(`home_automation/devices/${APP_CONFIG.DEVICE_ID}`);
        
        deviceRef.child('online').on('value', (snapshot) => {
            this.deviceOnline = snapshot.val() || false;
            this.updateConnectionStatus();
        });
        
        deviceRef.child('relays').on('value', (snapshot) => {
            const relayData = snapshot.val();
            if (relayData) {
                this.updateRelayStates(relayData);
            }
        });
        
        deviceRef.child('last_update').on('value', (snapshot) => {
            const timestamp = snapshot.val();
            if (timestamp) {
                this.lastUpdate = new Date(timestamp);
                this.updateLastUpdateDisplay();
            }
        });
        
        deviceRef.child('system_load').on('value', (snapshot) => {
            const load = snapshot.val() || 0;
            this.systemLoad.textContent = `${load}%`;
        });
    }
    
    async loadInitialData() {
        try {
            if (this.apiConnected) {
                // Load from API
                const response = await Utils.apiRequest(`${API_CONFIG.ENDPOINTS.DEVICES}/${APP_CONFIG.DEVICE_ID}`);
                this.updateFromApiData(response);
            } else {
                // Fallback to Firebase
                const deviceRef = database.ref(`home_automation/devices/${APP_CONFIG.DEVICE_ID}`);
                const snapshot = await deviceRef.once('value');
                const data = snapshot.val();
                
                if (data) {
                    this.updateFromFirebaseData(data);
                }
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('Failed to load device data', 'error');
        }
    }
    
    updateFromApiData(data) {
        if (data.relays) {
            this.updateRelayStates(data.relays);
        }
        this.deviceOnline = data.online || false;
        if (data.last_update) {
            this.lastUpdate = new Date(data.last_update);
        }
        this.updateConnectionStatus();
        this.updateLastUpdateDisplay();
    }
    
    updateFromFirebaseData(data) {
        if (data.relays) {
            this.updateRelayStates(data.relays);
        }
        this.deviceOnline = data.online || false;
        if (data.last_update) {
            this.lastUpdate = new Date(data.last_update);
        }
        this.updateConnectionStatus();
        this.updateLastUpdateDisplay();
    }
    
    updateConnectionStatus() {
        const statusElement = this.connectionStatus;
        const deviceStatusElement = this.deviceStatus;
        
        if (this.deviceOnline) {
            statusElement.innerHTML = '<div class="pulse-dot w-3 h-3 bg-green-500 rounded-full mr-2"></div><span>Connected</span>';
            deviceStatusElement.textContent = 'Online';
            deviceStatusElement.className = 'font-bold text-green-500';
        } else {
            statusElement.innerHTML = '<div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div><span>Offline</span>';
            deviceStatusElement.textContent = 'Offline';
            deviceStatusElement.className = 'font-bold text-red-500';
        }
    }
    
    updateRelayStates(relayData) {
        let activeCount = 0;
        
        Object.entries(relayData).forEach(([relayId, data]) => {
            const isActive = data.status || false;
            const powerUsage = data.power_usage || 0;
            
            // Update internal state
            this.relayStates.set(relayId, {
                status: isActive,
                name: data.name || this.relayStates.get(relayId)?.name || `Device ${relayId.split('_')[1]}`,
                lastChanged: new Date(),
                powerUsage: powerUsage
            });
            
            if (isActive) activeCount++;
            
            // Update UI
            this.updateRelayUI(relayId, isActive, powerUsage);
        });
        
        this.activeCount.textContent = `${activeCount}/${APP_CONFIG.RELAY_COUNT}`;
    }
    
    updateRelayUI(relayId, isActive, powerUsage = 0) {
        const elements = {
            toggle: document.getElementById(`toggle-${relayId}`),
            icon: document.getElementById(`icon-${relayId}`),
            status: document.getElementById(`status-${relayId}`),
            indicator: document.getElementById(`indicator-${relayId}`),
            lastChanged: document.getElementById(`last-changed-${relayId}`),
            power: document.getElementById(`power-${relayId}`),
            usageBar: document.getElementById(`usage-bar-${relayId}`),
            usagePercent: document.getElementById(`usage-percent-${relayId}`)
        };
        
        // Update toggle state
        if (elements.toggle) elements.toggle.checked = isActive;
        
        // Update icon
        if (elements.icon) {
            elements.icon.className = `fas fa-power-off text-2xl mr-3 transition-colors duration-200 ${
                isActive ? 'text-green-500' : 'text-gray-400'
            }`;
        }
        
        // Update status text
        if (elements.status) {
            elements.status.textContent = isActive ? 'ON' : 'OFF';
            elements.status.className = `text-lg font-bold mr-2 transition-colors duration-200 ${
                isActive ? 'text-green-500' : 'text-gray-400'
            }`;
        }
        
        // Update indicator
        if (elements.indicator) {
            elements.indicator.className = `w-3 h-3 rounded-full mr-3 transition-colors duration-200 ${
                isActive ? 'bg-green-500' : 'bg-gray-400'
            }`;
        }
        
        // Update timestamps
        if (elements.lastChanged) {
            elements.lastChanged.textContent = `Changed: ${new Date().toLocaleTimeString()}`;
        }
        
        // Update power usage
        if (elements.power) {
            elements.power.textContent = `${powerUsage}W`;
        }
        
        // Update usage bar
        const usagePercent = Math.min(100, (powerUsage / 1000) * 100);
        if (elements.usageBar) {
            elements.usageBar.style.width = `${usagePercent}%`;
        }
        if (elements.usagePercent) {
            elements.usagePercent.textContent = `${usagePercent.toFixed(1)}%`;
        }
    }
    
    async toggleRelay(relayId) {
        const currentState = this.relayStates.get(relayId);
        const newStatus = !currentState.status;
        
        try {
            if (this.apiConnected) {
                // Use API
                await Utils.apiRequest(`${API_CONFIG.ENDPOINTS.RELAYS}/${relayId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ status: newStatus })
                });
            } else {
                // Use Firebase directly
                const relayRef = database.ref(`home_automation/devices/${APP_CONFIG.DEVICE_ID}/relays/${relayId}/status`);
                await relayRef.set(newStatus);
            }
            
            this.showNotification(`${relayId} turned ${newStatus ? 'ON' : 'OFF'}`, 'success');
        } catch (error) {
            console.error(`Error toggling ${relayId}:`, error);
            this.showNotification(`Failed to control ${relayId}`, 'error');
            
            // Revert toggle
            const toggle = document.getElementById(`toggle-${relayId}`);
            if (toggle) toggle.checked = currentState.status;
        }
    }
    
    async setAllRelays(status) {
        try {
            if (this.apiConnected) {
                await Utils.apiRequest(`${API_CONFIG.ENDPOINTS.RELAYS}/bulk`, {
                    method: 'PUT',
                    body: JSON.stringify({ status })
                });
            } else {
                const updates = {};
                for (let i = 1; i <= APP_CONFIG.RELAY_COUNT; i++) {
                    updates[`home_automation/devices/${APP_CONFIG.DEVICE_ID}/relays/relay_${i}/status`] = status;
                }
                await database.ref().update(updates);
            }
            
            this.showNotification(`All relays turned ${status ? 'ON' : 'OFF'}`, 'success');
        } catch (error) {
            console.error('Error setting all relays:', error);
            this.showNotification('Failed to control all relays', 'error');
        }
    }
    
    async toggleAllRelays() {
        try {
            if (this.apiConnected) {
                await Utils.apiRequest(`${API_CONFIG.ENDPOINTS.RELAYS}/toggle-all`, {
                    method: 'POST'
                });
            } else {
                const updates = {};
                for (let i = 1; i <= APP_CONFIG.RELAY_COUNT; i++) {
                    const relayId = `relay_${i}`;
                    const currentState = this.relayStates.get(relayId);
                    updates[`home_automation/devices/${APP_CONFIG.DEVICE_ID}/relays/${relayId}/status`] = !currentState.status;
                }
                await database.ref().update(updates);
            }
            
            this.showNotification('All relays toggled', 'success');
        } catch (error) {
            console.error('Error toggling all relays:', error);
            this.showNotification('Failed to toggle all relays', 'error');
        }
    }
    
    async refreshData() {
        this.showNotification('Refreshing data...', 'info');
        await this.checkApiConnection();
        await this.loadInitialData();
    }
    
    setViewMode(mode) {
        const container = this.relayContainer;
        if (mode === 'list') {
            container.className = 'space-y-4';
        } else {
            container.className = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6';
        }
    }
    
    updateLastUpdateDisplay() {
        if (this.lastUpdateElement && this.lastUpdate) {
            this.lastUpdateElement.textContent = Utils.formatTime(this.lastUpdate);
        }
    }
    
    startSyncInterval() {
        this.syncInterval = setInterval(() => {
            this.updateLastUpdateDisplay();
        }, 1000);
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        
        const bgColor = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            warning: 'bg-yellow-600',
            info: 'bg-blue-600'
        }[type] || 'bg-blue-600';
        
        notification.className = `${bgColor} text-white px-6 py-4 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="font-medium">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.remove('translate-x-full'), 100);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('translate-x-full');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
    
    destroy() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
        }
        
        const deviceRef = database.ref(`home_automation/devices/${APP_CONFIG.DEVICE_ID}`);
        deviceRef.off();
    }
}

// Initialize app
window.homeAutomationApp = new HomeAutomationApp();
