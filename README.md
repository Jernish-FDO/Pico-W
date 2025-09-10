<div align="center">
   <img src="https://cdn.cdnlogo.com/logos/f/48/firebase.svg" width="200" height="200" alt="Firebase Logo">
  <h1>🔥 Smart Home Automation Control Panel 🔥</h1>
  <p>A sleek, real-time, and secure web interface for controlling your DIY smart home devices.</p>

 <p>
    <img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge"/>
    <img alt="Vite" src="https://img.shields.io/badge/Built%20with-Vite-purple.svg?style=for-the-badge"/>
    <img alt="Tailwind CSS" src="https://img.shields.io/badge/Styled%20with-TailwindCSS-38B2AC.svg?style=for-the-badge"/>
  </p>
</div>

---

> This project provides a responsive and modern control panel that connects to a **Firebase Realtime Database**. It's designed for hobbyists and DIY enthusiasts who want a professional-grade interface to monitor and control up to 16 relays on devices like an ESP32, ESP8266, or Raspberry Pi.

<!-- 💡 TIP: Create a GIF of your app working (logging in, toggling switches) and replace this image! -->
<div align="center">
  <img src="https://github.com/Jernish-FDO/Pico-W/blob/main/Screenshot_20250910-221145.png" alt="App Screenshot" width="800">
</div>

---

## ✨ Core Features

-   🔐 **Secure Firebase Authentication:** Protect your control panel with a robust email and password login system.
-   ⚡ **Real-Time Database Sync:** Switches and status indicators update instantly across all connected clients, powered by Firebase Realtime Database.
-   🎛️ **Granular Relay Control:** Individually toggle each of the 16 available relays.
-   🤖 **Powerful Quick Actions:**
    -   `Turn All ON`: Activate all relays with a single click.
    -   `Turn All OFF`: Deactivate all relays instantly.
    -   `Toggle All`: Invert the current state of every relay.
-   📊 **At-a-Glance Dashboard:** A clean status panel shows:
    -   🟢 WiFi Connectivity Status of your device.
    -   🕒 Timestamp of the last data update.
    -   💡 Count of currently active relays.
-   📱 **Fully Responsive UI:** A beautiful and functional interface on any device, from a desktop monitor to your smartphone, built with Tailwind CSS.
-   🔑 **Secure Configuration:** All sensitive API keys are safely stored in a `.env` file, keeping them out of your codebase.

---

## 🛠️ Technology & Tools

| Category      | Technology                                    | Purpose                                       |
| ------------- | --------------------------------------------- | --------------------------------------------- |
| **Frontend**  | 💻 HTML5, CSS3, JavaScript (ES Modules)       | Core web technologies for the interface.      |
| **Styling**   | 🎨 Tailwind CSS                               | A utility-first CSS framework for rapid UI development. |
| **Backend**   | 🔥 Firebase Authentication & Realtime Database | User management and real-time data synchronization. |
| **Build Tool**| 🚀 Vite                                       | A next-generation frontend tool for blazing-fast development. |
| **Icons**     | ✨ Font Awesome                               | Provides a wide range of high-quality icons. |

---

## 🚀 Getting Started

Follow these steps to get the project running on your local machine.

### Prerequisites

-   **Node.js:** You'll need Node.js version 16.x or higher. You can download it from [nodejs.org](https://nodejs.org/).
-   **Firebase Project:** A free Google Firebase project is required. Create one at the [Firebase Console](https://console.firebase.google.com/).
-   **Git:** You'll need Git to clone the repository.

### Installation Guide

1.**Clone the Repository:**
  Open your terminal and clone this project to your local machine.
  ```bash
   git clone https://your-repository-url.git
   cd firebase-loads
  ```

2.**Install Dependencies:**
  This command will download all the necessary packages defined in `package.json`.
 ```bash
 npm install
 ```

3.**Configure Environment Variables:**
  Create a `.env` file in the project root. This file will hold your secret Firebase credentials. **This file should NOT be committed to Git.**

 > **⚠️ Important:** Vite requires that environment variables exposed to the client-side code are prefixed with `VITE_`.

 Copy the following into your new `.env` file and replace the placeholder values with your actual Firebase project credentials.

```ini
 # .env - Your secret Firebase configuration
 VITE_FIREBASE_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXX"
 VITE_FIREBASE_AUTH_DOMAIN="your-project-id.firebaseapp.com"
 VITE_FIREBASE_DATABASE_URL="https://your-project-id-default-rtdb.firebaseio.com"
 VITE_FIREBASE_PROJECT_ID="your-project-id"
 VITE_FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
 VITE_FIREBASE_MESSAGING_SENDER_ID="1234567890"
 VITE_FIREBASE_APP_ID="1:1234567890:web:XXXXXXXXXXXXXXXX"
```

4.**Set Your Unique Device ID:**
  The application needs to know which device to listen to in the database. Open `js/app.js` and set the `DEVICE_ID` constant.
  ```javascript
   // in file: js/app.js
   const DEVICE_ID = 'esp32-living-room'; // 👈 CHANGE THIS to match your hardware's ID
  ```

5.**Start the Development Server:**
  You're all set! Run the following command to start the Vite dev server.
  ```bash
  npm run dev
  ```
  Your application should now be running at `http://localhost:5173`.

---

## 🔥 Firebase Setup Deep Dive

For the app to work, your Firebase project needs to be configured correctly.

1.**Authentication:**
   -   In the Firebase Console, go to **Authentication**.
   -   Click the "Sign-in method" tab.
   -   Enable the **Email/Password** provider.
   -   Go to the "Users" tab and add at least one user so you can log in.

2.**Realtime Database:**
  -   In the Firebase Console, go to **Realtime Database**
  -   Create a new database. Start in **Locked mode** for security.
  -   Go to the **Rules** tab and paste the following rules. These rules ensure that only authenticated users can read from and write to the device data.

```json
    {
      "rules": {
        "devices": {
          "$uid": {
            // Only authenticated users can read/write to their own device data path
            ".read": "auth != null",
            ".write": "auth != null"
          }
        }
      }
    }
```

3.**Database Structure:**
  Your hardware should be programmed to send data to Firebase in this specific JSON format. Make sure the root key (`esp32-living-room` in this example) matches your `DEVICE_ID`.

 ```json
 {
   "devices": {
     "esp32-living-room": {
       "relays": {
         "RELAY_1": 0, "RELAY_2": 1, /* ... up to RELAY_16 */
          },
          "last_seen": 1678886400,
          "wifi_status": "Connected"
        }
     }
  }
 ```

---

## 📂 Project Structure

A brief overview of the project's directory structure.
```
/
├── js/
│ ├── app.js # Core application logic, DOM manipulation, Firebase listeners
│ ├── auth.js # Handles all Firebase authentication logic
│ └── firebase-config.js# Initializes Firebase with credentials from .env
├── node_modules/ # Project dependencies
├── .env # Stores secret API keys (ignored by Git)
├── .gitignore # Specifies files for Git to ignore
├── index.html # The main HTML entry point
├── main.js # The main JavaScript entry point for Vite
├── package.json # Project metadata and dependencies
├── postcss.config.js # Configuration for PostCSS
├── style.css # Main stylesheet with Tailwind directives
└── tailwind.config.js # Configuration for Tailwind CSS
```

---

## 📦 Deployment

Ready to go live? Deploying a Vite project is simple.

1.**Build the Project:**
  Run the build command. This will compile and optimize all your files into a `dist` folder.
  ```bash
  npm run build
  ```

2.**Deploy the `dist` Folder:**
  Upload the contents of the `dist` folder to any static hosting provider. Excellent free options include:
   -   [Netlify](https://www.netlify.com/)
   -   [Vercel](https://vercel.com/)
   -   [Firebase Hosting](https://firebase.google.com/docs/hosting)
   -   [GitHub Pages](https://pages.github.com/)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/your-username/your-repo/issues).

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.