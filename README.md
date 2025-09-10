# 🏠 Pico-W Home Automation System

[![Live Demo](https://img.shields.io/badge/Demo-pico--w.vercel.app-blue?style=for-the-badge&logo=vercel)](https://pico-w.vercel.app)
[![Python](https://img.shields.io/badge/Python-70.1%25-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-22.6%25-yellow?style=for-the-badge&logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML](https://img.shields.io/badge/HTML-7.3%25-orange?style=for-the-badge&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)

A comprehensive IoT home automation system built with **Raspberry Pi Pico W** that enables wireless control of multiple loads through a web interface. This project combines embedded programming with modern web technologies to create a scalable and secure home automation solution.

## 🚀 Features

- **🔌 Multi-Load Control**: Control up to 16 electrical loads wirelessly
- **📱 Web Interface**: Modern, responsive web application for device control
- **🔥 Firebase Integration**: Real-time database synchronization
- **📡 WiFi Connectivity**: Wireless communication using Pico W's built-in WiFi
- **🔒 Security Features**: Advanced authentication and data encryption
- **⚡ Real-time Updates**: Instant status updates across all connected devices
- **📊 Load Monitoring**: Track and monitor electrical load states
- **🎨 Modern UI**: Clean and intuitive user interface

## 🛠️ Tech Stack

### Hardware
- **Raspberry Pi Pico W** - Main microcontroller with WiFi capability
- **Relay Modules** - For electrical load switching
- **LEDs/Indicators** - Status indication
- **Power Supply** - 5V/3.3V power management

### Software
- **Python (MicroPython)** - Pico W firmware and control logic
- **JavaScript** - Frontend interactivity and API communication
- **HTML/CSS** - User interface and styling
- **Firebase Realtime Database** - Cloud data synchronization
- **Arduino IDE** - Development environment for Pico W

## 📋 Prerequisites

Before setting up this project, ensure you have:

- Raspberry Pi Pico W board
- Arduino IDE with RP2040 board package
- Firebase project with Realtime Database
- Basic electronics components (relays, LEDs, resistors)
- WiFi network credentials

## ⚙️ Installation & Setup

### 1. Hardware Setup

Pico W Pin Configuration:
├── GPIO 0-15  → Relay Control Pins
├── GPIO 16    → Status LED
├── 3.3V       → Power Rail
└── GND        → Ground Rail


### 2. Arduino IDE Configuration
1. Install Arduino IDE
2. Add RP2040 board package
3. Select "Raspberry Pi Pico W" from boards menu
4. Install required libraries:
   - WiFi library for Pico W
   - ArduinoJson
   - Firebase ESP32 Client

### 3. Firebase Setup
1. Create a new Firebase project
2. Enable Realtime Database
3. Configure security rules
4. Get your project credentials

### 4. Code Upload
1. Clone this repository
2. Update WiFi credentials in `config.h`
3. Add Firebase configuration
4. Upload the code to Pico W

## 🖥️ Web Interface

The web application provides:
- **Dashboard**: Overview of all connected loads
- **Individual Control**: Toggle switches for each load
- **Status Monitoring**: Real-time status updates
- **Settings Panel**: Configuration options
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
Pico-W/
├── 📂 src/
│   ├── 🐍 main.py              # Main Pico W control script
│   ├── 🐍 wifi_manager.py      # WiFi connection management
│   ├── 🐍 firebase_client.py   # Firebase communication
│   └── 🐍 load_controller.py   # Load switching logic
├── 📂 web/
│   ├── 🌐 index.html          # Main web interface
│   ├── 🎨 style.css           # Styling and responsive design
│   └── ⚡ script.js           # Frontend JavaScript logic
├── 📂 config/
│   ├── ⚙️ wifi_config.json    # WiFi configuration
│   └── 🔥 firebase_config.json # Firebase settings
├── 📂 docs/
│   ├── 📖 setup_guide.md      # Detailed setup instructions
│   ├── 🔧 troubleshooting.md  # Common issues and solutions
│   └── 📊 api_documentation.md # API endpoints documentation
└── 📋 README.md               # This file
```

## 🔧 Configuration

### WiFi Setup
```
# wifi_config.json
{
  "ssid": "YOUR_WIFI_SSID",
  "password": "YOUR_WIFI_PASSWORD",
  "hostname": "pico-w-automation"
}
```

### Firebase Configuration
```
{
  "apiKey": "YOUR_API_KEY",
  "databaseURL": "https://your-project.firebaseio.com/",
  "projectId": "your-project-id"
}
```

## 🎯 Usage Examples

### Basic Load Control
```
# Toggle a specific load
load_controller.toggle_load(load_id=1)

# Set multiple loads at once
load_controller.set_loads([1][2][3], state=True)

# Get current status
status = load_controller.get_all_status()
```

### Web API Endpoints
```
// Get all load states
fetch('/api/loads')

// Toggle specific load
fetch('/api/loads/1/toggle', { method: 'POST' })

// Set load state
fetch('/api/loads/1', {
  method: 'PUT',
  body: JSON.stringify({ state: true })
})
```

## 🚨 Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| WiFi connection fails | Check credentials and signal strength |
| Firebase sync issues | Verify database rules and API keys |
| Load not responding | Check relay connections and power supply |
| Web interface not loading | Ensure Pico W IP is accessible |

### Debug Mode
Enable debug output by setting `DEBUG = True` in `main.py`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Jernish** - *Electronics & Communication Engineering Student*
- GitHub: [@Jernish-FDO](https://github.com/Jernish-FDO)
- Interest: IoT Automation & Embedded Systems

## 🙏 Acknowledgments

- Raspberry Pi Foundation for the amazing Pico W platform
- Firebase team for the real-time database service
- MicroPython community for excellent documentation
- Open source contributors who made this project possible

## 🔮 Future Enhancements

- [ ] Voice control integration
- [ ] Mobile app development
- [ ] Energy monitoring features
- [ ] Scheduling and automation rules
- [ ] Integration with smart home platforms
- [ ] Over-the-air updates
- [ ] Multi-user access control

---

⭐ **Star this repository if you find it helpful!**

📧 **Have questions?** Feel free to open an issue or contact me directly.

🔗 **Live Demo:** [pico-w.vercel.app](https://pico-w.vercel.app)
```
