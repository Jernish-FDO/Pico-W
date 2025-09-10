import { auth } from './firebase-config.js';

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.loginModal = document.getElementById('login-modal');
        this.loginForm = document.getElementById('login-form');
        this.loginError = document.getElementById('login-error');
        
        this.setupAuthListeners();
        this.setupEventListeners();
    }
    
    setupAuthListeners() {
        // Monitor authentication state
        auth.onAuthStateChanged((user) => {
            if (user) {
                this.currentUser = user;
                this.hideLoginModal();
                this.initializeApp();
            } else {
                this.currentUser = null;
                this.showLoginModal();
            }
        });
    }
    
    setupEventListeners() {
        // Login form submission
        this.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });
    }
    
    async login() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            await auth.signInWithEmailAndPassword(email, password);
            this.hideError();
        } catch (error) {
            this.showError(this.getErrorMessage(error.code));
        }
    }
    
    async logout() {
        try {
            await auth.signOut();
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    showLoginModal() {
        this.loginModal.classList.remove('hidden');
    }
    
    hideLoginModal() {
        this.loginModal.classList.add('hidden');
    }
    
    showError(message) {
        this.loginError.textContent = message;
        this.loginError.classList.remove('hidden');
    }
    
    hideError() {
        this.loginError.classList.add('hidden');
    }
    
    getErrorMessage(errorCode) {
        switch (errorCode) {
            case 'auth/invalid-email':
                return 'Invalid email address.';
            case 'auth/user-disabled':
                return 'This account has been disabled.';
            case 'auth/user-not-found':
                return 'No account found with this email.';
            case 'auth/wrong-password':
                return 'Incorrect password.';
            case 'auth/too-many-requests':
                return 'Too many failed attempts. Please try again later.';
            default:
                return 'Login failed. Please try again.';
        }
    }
    
    initializeApp() {
        // Initialize the main application
        if (window.homeAutomationApp) {
            window.homeAutomationApp.init();
        }
    }
}

// Initialize authentication
const authManager = new AuthManager();
