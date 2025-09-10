# Smart Home Automation System



#### Firebase with Raspberry Pi Pico W, Firebase Realtime Database, and a modern web interface. Control up to 16 electrical loads remotely with real-time monitoring, authentication, and advanced safety features.



## 🏠 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Hardware Setup](#hardware-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development](#development)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## ✨ Features

### Core Functionality
- **16-Channel Relay Control** - Individual and bulk control of electrical loads
- **Real-time Monitoring** - Live status updates and power consumption tracking  
- **Firebase Integration** - Cloud-based data synchronization and storage
- **Web Dashboard** - Responsive, modern UI with dark mode support
- **Mobile Responsive** - Full functionality on desktop, tablet, and mobile devices

### Advanced Features
- **User Authentication** - Secure Firebase Authentication with role-based access
- **Real-time Updates** - Live synchronization between devices and web interface
- **Audit Logging** - Complete activity tracking and security monitoring
- **Scheduling** - Timer-based automation and scheduling capabilities
- **Safety Systems** - Emergency stop, overcurrent protection, and safety interlocks
- **Power Monitoring** - Real-time power consumption and usage analytics
- **API Access** - RESTful API for third-party integrations

### Security Features
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access Control** - Admin, standard user, and device-specific permissions  
- **Rate Limiting** - API protection against abuse and attacks
- **Audit Trails** - Comprehensive logging of all system activities
- **Encrypted Communications** - HTTPS/TLS encryption for all data transfer

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Python Backend │    │ Raspberry Pi    │
│                 │    │                 │    │    Pico W       │
│  • HTML/CSS/JS  │◄──►│  • Flask API    │◄──►│                 │
│  • TailwindCSS  │    │  • Firebase SDK │    │  • MicroPython  │
│  • Firebase Auth│    │  • Middleware   │    │  • GPIO Control │
│  • Real-time UI │    │  • Security     │    │  • 16 Relays    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │ Firebase Cloud  │
                    │                 │
                    │  • Realtime DB  │
                    │  • Authentication│
                    │  • Security Rules│
                    │  • Audit Logs   │
                    └─────────────────┘
```

### Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- TailwindCSS for styling
- Firebase JavaScript SDK
- Responsive design with mobile support

**Backend:**
- Python 3.8+ with Flask framework
- Firebase Admin SDK
- Custom middleware for authentication and logging
- RESTful API design

**Hardware:**
- Raspberry Pi Pico W (RP2040 microcontroller)
- MicroPython firmware
- 16-channel relay module (12V)
- Safety circuits and protection systems

**Cloud Services:**
- Firebase Realtime Database
- Firebase Authentication
- Firebase Security Rules
- Cloud-based data synchronization

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ (for TailwindCSS build)
- Firebase project with Realtime Database
- Raspberry Pi Pico W with MicroPython
- 16-channel relay module

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-home-automation.git
cd smart-home-automation
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_DATABASE_URL="https://your-project-default-rtdb.firebaseio.com/"
export SECRET_KEY="your-secret-key"

# Run backend
python backend/run.py
```

### 3. Frontend Setup
```bash
# Install TailwindCSS
npm install -D tailwindcss

# Build CSS
npx tailwindcss -i ./frontend/style.css -o ./frontend/dist/style.css --watch
```

### 4. Hardware Setup
```bash
# Flash MicroPython to Pico W
# Copy pico-w/ files to Pico W
# Update config.py with your WiFi and Firebase credentials
```

### 5. Access the Application
- Open your browser to `http://localhost:5000`
- Login with your Firebase credentials
- Start controlling your smart home!

## 📦 Installation

### Detailed Backend Installation

1. **System Requirements**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.8 python3-pip python3-venv git

   # CentOS/RHEL
   sudo yum install python38 python3-pip git

   # macOS
   brew install python@3.8 git
   ```

2. **Project Setup**
   ```bash
   git clone https://github.com/yourusername/smart-home-automation.git
   cd smart-home-automation
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Upgrade pip
   pip install --upgrade pip
   
   # Install backend dependencies
   pip install -r backend/requirements.txt
   ```

3. **Frontend Dependencies**
   ```bash
   # Install Node.js and npm
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Install TailwindCSS
   npm install -D tailwindcss @tailwindcss/cli
   ```

### Firebase Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project" and follow the setup wizard
   - Enable Realtime Database in test mode
   - Enable Authentication with Email/Password provider

2. **Download Service Account Key**
   - Go to Project Settings → Service Accounts
   - Generate new private key
   - Save as `service-account-key.json` in project root

3. **Configure Database Rules**
   ```json
   {
     "rules": {
       ".read": false,
       ".write": false,
       "home_automation": {
         "devices": {
           "$device_id": {
             ".read": "auth != null",
             ".write": "auth != null"
           }
         }
       }
     }
   }
   ```

### Environment Configuration

Create `.env` file in project root:
```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
HOST=0.0.0.0
PORT=5000
DEBUG=true

# Firebase Configuration  
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./service-account-key.json

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret
RATE_LIMIT_ENABLED=true
CORS_ENABLED=true

# Logging Configuration
LOG_LEVEL=INFO
REQUEST_LOGGING=true
AUDIT_LOGGING=true
```

## ⚡ Hardware Setup

### Components Required

| Component | Quantity | Description |
|-----------|----------|-------------|
| Raspberry Pi Pico W | 1 | Main microcontroller with WiFi |
| 16-Channel Relay Module | 1 | 12V, 10A per channel |
| 12V Power Supply | 1 | For relay module (minimum 2A) |
| Jumper Wires | 20+ | Male-to-female, various lengths |
| Breadboard | 1 | For prototyping connections |
| Optocouplers (PC817) | 16 | Electrical isolation |
| Resistors (220Ω) | 16 | Current limiting |
| Diodes (1N4001) | 16 | Flyback protection |
| Fuses | 16 | Circuit protection |

### Circuit Diagram

```
Pico W                    Relay Module
GPIO0  ──[220Ω]──[PC817]──► Relay 1 IN
GPIO1  ──[220Ω]──[PC817]──► Relay 2 IN  
GPIO2  ──[220Ω]──[PC817]──► Relay 3 IN
...
GPIO15 ──[220Ω]──[PC817]──► Relay 16 IN

Power Connections:
Pico W VCC ──────────────► 3.3V Rail
Relay Module VCC ────────► 12V Supply (+)
Relay Module GND ────────► 12V Supply (-)
Pico W GND ──────────────► Common Ground
```

### Safety Considerations

⚠️ **IMPORTANT SAFETY WARNINGS:**

- **High Voltage**: Relays switch mains voltage (110V/220V). Improper wiring can cause electrocution or fire.
- **Isolation**: Always use optocouplers between Pico W and relay inputs.
- **Fusing**: Install appropriate fuses for each circuit (never exceed relay ratings).
- **Enclosure**: Use proper electrical enclosures for all high-voltage connections.
- **Testing**: Test all circuits with low voltage before connecting mains power.
- **Professional Installation**: Consider hiring a licensed electrician for permanent installations.

### Pico W Firmware Installation

1. **Download MicroPython**
   ```bash
   # Download latest MicroPython firmware for Pico W
   wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2
   ```

2. **Flash Firmware**
   - Hold BOOTSEL button while connecting Pico W to USB
   - Copy `.uf2` file to the mounted drive
   - Pico W will reboot with MicroPython

3. **Upload Project Files**
   ```bash
   # Using Thonny IDE or ampy
   ampy --port /dev/ttyACM0 put pico-w/main.py
   ampy --port /dev/ttyACM0 put pico-w/config.py
   ampy --port /dev/ttyACM0 put pico-w/firebase_client.py
   ampy --port /dev/ttyACM0 put pico-w/relay_controller.py
   ```

4. **Configure Settings**
   Edit `pico-w/config.py`:
   ```python
   # WiFi credentials
   WIFI_SSID = 'Your_WiFi_Network'
   WIFI_PASSWORD = 'Your_WiFi_Password'
   
   # Firebase configuration
   FIREBASE_CONFIG = {
       'apiKey': 'your-api-key',
       'databaseURL': 'https://your-project-default-rtdb.firebaseio.com/',
       'deviceEmail': 'device@yourdomain.com',
       'devicePassword': 'secure-device-password'
   }
   ```

## ⚙️ Configuration

### Backend Configuration (`backend/config/app_config.py`)

```python
class DevelopmentConfig(AppConfig):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
class ProductionConfig(AppConfig):  
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 80
    WORKERS = 4
```

### Frontend Configuration (`frontend/js/firebase-config.js`)

```javascript
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com", 
    databaseURL: "https://your-project-default-rtdb.firebaseio.com",
    projectId: "your-project-id"
};

const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api'
};
```

### TailwindCSS Build

```bash
# Development (with watch)
npm run dev

# Production build
npm run build

# Custom build
npx tailwindcss -i ./frontend/style.css -o ./frontend/dist/style.css --minify
```

## 📖 Usage

### Web Interface

1. **Login**
   - Navigate to `http://localhost:5000`
   - Enter your Firebase credentials
   - Dashboard loads after successful authentication

2. **Control Relays**
   - Toggle individual relays with switches
   - Use quick actions for bulk operations
   - Monitor real-time status and power usage

3. **System Monitoring**
   - View device online status
   - Check last update timestamps
   - Monitor system load and performance

### API Usage

```bash
# Get device status
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/devices/pico_w_001

# Control relay
curl -X PUT \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": true}' \
     http://localhost:5000/api/relays/pico_w_001/relay_1

# Bulk control
curl -X PUT \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": false}' \
     http://localhost:5000/api/relays/pico_w_001/bulk
```

### MicroPython Console

```python
# Connect to Pico W via serial
import machine
from relay_controller import RelayController

# Initialize controller
controller = RelayController([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

# Control individual relay
controller.set_relay('relay_1', True)  # Turn ON
controller.set_relay('relay_1', False) # Turn OFF

# Emergency stop
controller.turn_off_all_relays()
```

## 📚 API Documentation

### Authentication

All API endpoints require authentication via Firebase ID tokens:

```
Authorization: Bearer <firebase-id-token>
```

### Endpoints

#### Device Management

**GET `/api/devices`** - List all accessible devices
```json
{
  "devices": {
    "pico_w_001": {
      "id": "pico_w_001", 
      "online": true,
      "relay_count": 16,
      "active_relays": 3
    }
  }
}
```

**GET `/api/devices/{device_id}`** - Get device details
```json
{
  "id": "pico_w_001",
  "online": true,
  "last_update": "2025-09-10T13:51:00Z",
  "relays": {...},
  "statistics": {
    "total_power_usage": 850,
    "uptime": 86400
  }
}
```

#### Relay Control

**PUT `/api/relays/{device_id}/{relay_id}`** - Control individual relay
```json
// Request
{"status": true}

// Response  
{
  "message": "relay_1 turned ON",
  "status": true,
  "timestamp": "2025-09-10T13:51:00Z"
}
```

**PUT `/api/relays/{device_id}/bulk`** - Bulk control
```json
// Turn all ON
{"status": true}

// Control specific relays
{
  "relays": [
    {"relay_id": "relay_1", "status": true},
    {"relay_id": "relay_2", "status": false}  
  ]
}
```

**POST `/api/relays/{device_id}/toggle-all`** - Toggle all relays
```json
{
  "message": "All 16 relays toggled",
  "toggled_relays": [...]
}
```

### Error Responses

```json
// Authentication Error (401)
{
  "error": "Authentication required",
  "message": "No authentication token provided"
}

// Permission Error (403)  
{
  "error": "Insufficient permissions",
  "message": "Permission denied for device pico_w_001"
}

// Not Found (404)
{
  "error": "Device not found", 
  "message": "Device pico_w_001 does not exist"
}
```

## 🚀 Deployment

### Development Deployment

```bash
# Backend
python backend/run.py --config development

# Frontend  
npx tailwindcss -i ./frontend/style.css -o ./frontend/dist/style.css --watch

# Access at http://localhost:5000
```

### Production Deployment

#### Using Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY backend/ ./backend/
   COPY frontend/ ./frontend/
   COPY requirements.txt .
   
   RUN pip install -r requirements.txt
   
   EXPOSE 5000
   CMD ["python", "backend/run.py", "--production"]
   ```

2. **Build and Run**
   ```bash
   docker build -t smart-home-api .
   docker run -d -p 5000:5000 \
     -e FIREBASE_PROJECT_ID=your-project \
     -e SECRET_KEY=your-secret \
     smart-home-api
   ```

#### Using Systemd

1. **Create Service File**
   ```ini
   # /etc/systemd/system/smart-home.service
   [Unit]
   Description=Smart Home Automation API
   After=network.target
   
   [Service] 
   Type=simple
   User=www-data
   WorkingDirectory=/opt/smart-home
   Environment=FLASK_ENV=production
   ExecStart=/opt/smart-home/venv/bin/python backend/run.py --production
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start**
   ```bash
   sudo systemctl enable smart-home
   sudo systemctl start smart-home
   sudo systemctl status smart-home
   ```

#### Using Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/smart-home
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /opt/smart-home/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Cloud Deployment

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/smart-home
gcloud run deploy --image gcr.io/PROJECT-ID/smart-home --platform managed
```

#### AWS Elastic Beanstalk

```bash
# Initialize and deploy  
eb init smart-home-api
eb create production
eb deploy
```

#### Heroku

```bash
# Deploy to Heroku
heroku create smart-home-api
git push heroku main
heroku config:set FIREBASE_PROJECT_ID=your-project
```

## 🔧 Development

### Setting Up Development Environment

1. **Install Development Tools**
   ```bash
   # Python development
   pip install black flake8 pytest pytest-cov

   # JavaScript development  
   npm install -D prettier eslint
   
   # Pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

2. **Code Formatting**
   ```bash
   # Python
   black backend/
   flake8 backend/
   
   # JavaScript
   prettier --write frontend/js/
   eslint frontend/js/
   ```

3. **Testing**
   ```bash
   # Backend tests
   pytest backend/tests/ -v --cov=backend
   
   # Frontend tests (if using Jest)
   npm test
   ```

### Project Structure

```
smart-home-automation/
├── backend/                 # Python Flask API
│   ├── app.py              # Application factory
│   ├── run.py              # Application runner
│   ├── config/             # Configuration files
│   ├── middleware/         # Custom middleware
│   ├── routes/            # API routes  
│   └── tests/             # Backend tests
├── frontend/              # Web interface
│   ├── index.html         # Main HTML file
│   ├── js/               # JavaScript files
│   ├── style.css         # TailwindCSS input
│   └── dist/             # Built CSS files
├── pico-w/               # Pico W firmware
│   ├── main.py           # Main controller
│   ├── config.py         # Hardware configuration
│   ├── firebase_client.py # Firebase integration
│   └── relay_controller.py # Relay management
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies  
├── tailwind.config.js    # TailwindCSS configuration
└── README.md            # This file
```

### Development Workflow

1. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature
   
   # Make changes and test
   python backend/run.py --debug
   
   # Run tests
   pytest backend/tests/
   
   # Commit and push
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **Code Review Process**
   - Create pull request
   - Ensure all tests pass
   - Code review by team members
   - Merge to main branch

### Debugging

#### Backend Debugging
```bash
# Enable debug mode
export FLASK_DEBUG=true
python backend/run.py

# View logs
tail -f logs/app.log

# Database debugging
python -c "from backend.config import get_firebase_config; print(get_firebase_config())"
```

#### Frontend Debugging
```javascript
// Enable debug logging
localStorage.setItem('debug', 'true');

// View Firebase connection
console.log(firebase.database().ref('.info/connected'));

// Monitor authentication state
firebase.auth().onAuthStateChanged(user => console.log(user));
```

#### Pico W Debugging
```python
# Serial connection debugging
import sys
sys.print_exception(e)  # Print detailed exceptions

# Memory debugging
import gc
print(f"Free memory: {gc.mem_free()} bytes")
gc.collect()

# WiFi debugging  
import network
wlan = network.WLAN(network.STA_IF)
print(f"Connection status: {wlan.status()}")
print(f"IP address: {wlan.ifconfig()[0]}")
```

## 🔒 Security

### Security Features

1. **Authentication & Authorization**
   - Firebase Authentication with JWT tokens
   - Role-based access control (Admin, User, Device)
   - Custom claims for granular permissions

2. **API Security**
   - Rate limiting to prevent abuse
   - Input validation and sanitization
   - CORS configuration for cross-origin requests
   - Security headers (HSTS, XSS protection, etc.)

3. **Data Security** 
   - Firebase Security Rules for database access
   - Encrypted data transmission (HTTPS/TLS)
   - Audit logging for all activities
   - Data validation at all layers

4. **Hardware Security**
   - Device authentication with Firebase
   - Secure credential storage
   - Network isolation capabilities
   - Emergency safety systems

### Security Best Practices

1. **Environment Security**
   ```bash
   # Use strong secrets
   export SECRET_KEY=$(openssl rand -hex 32)
   
   # Restrict file permissions
   chmod 600 service-account-key.json
   chmod 600 .env
   
   # Use separate environments
   export FLASK_ENV=production
   ```

2. **Firebase Security Rules**
   ```json
   {
     "rules": {
       "home_automation": {
         "devices": {
           "$device_id": {
             ".read": "auth != null && (auth.uid == $device_id || root.child('users/' + auth.uid + '/role').val() == 'admin')",
             ".write": "auth != null && (auth.uid == $device_id || root.child('users/' + auth.uid + '/role').val() == 'admin')"
           }
         }
       }
     }
   }
   ```

3. **Network Security**
   ```bash
   # Use firewall rules
   sudo ufw allow 22/tcp    # SSH only from specific IPs
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw deny 5000/tcp   # Block direct Flask access
   
   # Use VPN for remote access
   # Configure fail2ban for intrusion prevention
   ```

### Security Checklist

- [ ] All secrets stored in environment variables
- [ ] Firebase Security Rules properly configured  
- [ ] HTTPS enabled for all connections
- [ ] Rate limiting configured and tested
- [ ] Input validation implemented
- [ ] Audit logging enabled
- [ ] Regular security updates applied
- [ ] Backup and recovery procedures tested
- [ ] Network segmentation implemented
- [ ] Physical security measures in place

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

**Issue: Flask app won't start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check environment variables
python -c "import os; print(os.environ.get('FIREBASE_PROJECT_ID'))"

# Check logs
tail -f logs/app.log
```

**Issue: Firebase connection failed**
```bash
# Verify service account key
ls -la service-account-key.json

# Test Firebase connection
python -c "
from backend.config.firebase_config import FirebaseConfig
config = FirebaseConfig()
print(config.validate_configuration())
"

# Check network connectivity
curl -I https://your-project-default-rtdb.firebaseio.com/
```

#### Frontend Issues

**Issue: Authentication not working**
```javascript
// Check Firebase config
console.log(firebaseConfig);

// Verify authentication state
firebase.auth().onAuthStateChanged(user => {
    if (user) {
        console.log('User signed in:', user.uid);
    } else {
        console.log('User signed out');
    }
});

// Check browser console for errors
```

**Issue: TailwindCSS styles not applying**
```bash
# Rebuild CSS
npx tailwindcss -i ./frontend/style.css -o ./frontend/dist/style.css

# Check build output
ls -la frontend/dist/style.css

# Verify HTML link tag
grep -n "style.css" frontend/index.html
```

#### Hardware Issues

**Issue: Pico W not connecting to WiFi**
```python
# Check WiFi credentials in config.py
print(f"SSID: {WIFI_SSID}")

# Test WiFi connection
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
available_networks = wlan.scan()
print("Available networks:", [net[0].decode() for net in available_networks])
```

**Issue: Relays not responding**
```python
# Test GPIO pins
from machine import Pin
test_pin = Pin(0, Pin.OUT)
test_pin.value(1)  # Should turn OFF relay (active low)
test_pin.value(0)  # Should turn ON relay

# Check relay module power supply
# Verify optocoupler connections
# Test with multimeter
```

### Debug Commands

```bash
# Backend debugging
python backend/run.py --debug --info

# Check API health
curl http://localhost:5000/api/status

# Test authentication
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/devices

# Monitor Firebase  
firebase database:get / --project your-project-id

# Pico W serial monitor
screen /dev/ttyACM0 115200
# Or using Thonny IDE
```

### Performance Optimization

1. **Backend Optimization**
   ```python
   # Use connection pooling
   # Enable caching for static data
   # Optimize database queries
   # Use async operations where possible
   ```

2. **Frontend Optimization**
   ```bash
   # Minify CSS and JavaScript
   npx tailwindcss -o frontend/dist/style.css --minify
   
   # Enable browser caching
   # Use CDN for static assets
   # Implement service workers
   ```

3. **Hardware Optimization**
   ```python
   # Reduce sync frequency for battery operation
   # Implement sleep modes
   # Optimize memory usage with gc.collect()
   ```

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Getting Started

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/smart-home-automation.git
   cd smart-home-automation
   
   # Add upstream remote
   git remote add upstream https://github.com/original/smart-home-automation.git
   ```

2. **Set Up Development Environment**
   ```bash
   # Follow installation instructions
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Development Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make Changes**
   - Write code following project style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest backend/tests/ -v
   
   # Check code style
   black backend/
   flake8 backend/
   
   # Test frontend
   npm test
   ```

4. **Submit Pull Request**
   - Push branch to your fork
   - Create pull request with clear description
   - Include screenshots for UI changes
   - Reference any related issues

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8 style guide
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints where appropriate
- Write docstrings for all functions and classes

**JavaScript (Frontend):**
- Use ES6+ features
- Follow Airbnb JavaScript style guide
- Use consistent indentation (2 spaces)
- Add JSDoc comments for complex functions

**Documentation:**
- Update README.md for new features
- Add inline comments for complex logic
- Include examples in docstrings
- Keep documentation up-to-date

### Reporting Issues

When reporting issues, please include:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Log files and error messages
- Screenshots for UI issues

### Feature Requests

For feature requests:
- Check existing issues first
- Provide clear use case and rationale
- Include mockups or examples if applicable
- Be open to discussion and feedback

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

```
Copyright (c) 2025 Smart Home Automation Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 💬 Support

### Getting Help

- **Documentation**: Start with this README and check the `docs/` folder
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join community discussions for questions and ideas
- **Wiki**: Check the project wiki for additional guides and tutorials

### Community

- **GitHub Discussions**: [Project Discussions](https://github.com/yourusername/smart-home-automation/discussions)
- **Discord Server**: [Join our Discord](https://discord.gg/your-invite)  
- **Subreddit**: [r/SmartHomeAutomation](https://reddit.com/r/smarthomeautomation)

### Professional Support

For commercial deployments and professional support:
- Email: support@yourdomain.com
- Consulting services available
- Custom development and integration
- Training and workshops

***

## 🙏 Acknowledgments

- **Raspberry Pi Foundation** - For the amazing Pico W microcontroller
- **Google Firebase** - For the robust cloud platform  
- **Flask Community** - For the excellent web framework
- **TailwindCSS Team** - For the utility-first CSS framework
- **MicroPython Team** - For making Python accessible on microcontrollers
- **Contributors** - Thanks to all who have contributed to this project

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/starss/youyourus Automation Community**

*Last updated: September 10, 2025*
