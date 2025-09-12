import { auth } from './firebase-config.js';

// Email validation functionality
document.addEventListener('DOMContentLoaded', function() {
    const emailField = document.getElementById('login-email');
    const validationIcon = document.getElementById('email-validation-icon');
    const errorDiv = document.getElementById('email-error');
    const errorText = document.getElementById('email-error-text');
    
    // Email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // Real-time email validation
    function validateEmail() {
        const email = emailField.value.trim();
        const isValid = emailRegex.test(email);
        
        if (email === '') {
            // Empty field
            hideValidation();
            return;
        }
        
        if (isValid) {
            showSuccess();
        } else {
            showError('Please enter a valid email address');
        }
    }
    
    function showSuccess() {
        emailField.classList.remove('border-red-500', 'focus:border-red-500');
        emailField.classList.add('border-green-500', 'focus:border-green-500');
        
        validationIcon.classList.remove('fa-times', 'text-red-500', 'hidden');
        validationIcon.classList.add('fa-check', 'text-green-500');
        
        errorDiv.classList.add('hidden');
    }
    
    function showError(message) {
        emailField.classList.remove('border-green-500', 'focus:border-green-500');
        emailField.classList.add('border-red-500', 'focus:border-red-500');
        
        validationIcon.classList.remove('fa-check', 'text-green-500', 'hidden');
        validationIcon.classList.add('fa-times', 'text-red-500');
        
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    function hideValidation() {
        emailField.classList.remove('border-red-500', 'border-green-500', 'focus:border-red-500', 'focus:border-green-500');
        validationIcon.classList.add('hidden');
        errorDiv.classList.add('hidden');
    }
    
    // Event listeners
    emailField.addEventListener('input', validateEmail);
    emailField.addEventListener('blur', validateEmail);
    
    // Clear validation on focus
    emailField.addEventListener('focus', function() {
        if (!this.value.trim()) {
            hideValidation();
        }
    });
});


// Minimal version - just essential functionality
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('login-password');
    const passwordToggle = document.getElementById('password-toggle');
    
    // Password toggle
    passwordToggle.addEventListener('click', function() {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            this.classList.remove('fa-eye');
            this.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            this.classList.remove('fa-eye-slash');
            this.classList.add('fa-eye');
        }
    });
    
    // Password strength checker
    passwordField.addEventListener('input', function() {
        const password = this.value;
        const strengthIndicator = document.getElementById('password-strength');
        const strengthText = document.getElementById('strength-text');
        const bars = strengthIndicator.querySelectorAll('.h-1');
        
        if (password.length === 0) {
            strengthIndicator.classList.add('hidden');
            return;
        }
        
        strengthIndicator.classList.remove('hidden');
        
        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        const colors = ['bg-red-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];
        const labels = ['Very Weak', 'Weak', 'Good', 'Strong'];
        
        bars.forEach(bar => bar.className = 'h-1 bg-gray-600 rounded flex-1');
        
        for (let i = 0; i < strength; i++) {
            bars[i].classList.remove('bg-gray-600');
            bars[i].classList.add(colors[strength - 1]);
        }
        
        strengthText.textContent = labels[strength - 1] || 'Very Weak';
    });
});

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