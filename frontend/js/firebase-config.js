// Firebase configuration
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    databaseURL: "https://your-project-default-rtdb.firebaseio.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize services
const auth = firebase.auth();
const database = firebase.database();

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',  // Your Flask server URL
    ENDPOINTS: {
        DEVICES: '/devices',
        RELAYS: '/relays',
        AUTH: '/auth',
        STATUS: '/status'
    }
};

// Application Constants
const APP_CONFIG = {
    DEVICE_ID: 'pico_w_001',
    RELAY_COUNT: 16,
    SYNC_INTERVAL: 3000,
    MAX_RETRIES: 3
};

// Relay default names
const RELAY_NAMES = [
    'Living Room Light', 'Kitchen Fan', 'Bedroom AC', 'Garden Pump',
    'Garage Door', 'Pool Pump', 'Security Light', 'Bathroom Fan',
    'Washing Machine', 'Dryer', 'Water Heater', 'Outdoor Light',
    'Workshop Light', 'Shed Power', 'Irrigation System', 'Backup Power'
];

// Utility functions
const Utils = {
    formatTime: (date) => {
        if (!date) return 'Never';
        const now = new Date();
        const diff = now - new Date(date);
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
        return new Date(date).toLocaleDateString();
    },
    
    debounce: (func, wait) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },

    // API request helper
    apiRequest: async (endpoint, options = {}) => {
        const token = await auth.currentUser?.getIdToken();
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error(`API request to ${endpoint} failed:`, error);
            throw error;
        }
    }
};
