# Smart Home Automation Control Panel

A modern, responsive web-based control panel for a DIY smart home automation system. This interface connects to a Firebase Realtime Database to monitor and control up to 16 relays in real-time.


*(Feel free to replace this with your own screenshot!)*

---

## ✨ Features

-   **Secure User Authentication:** Login system powered by Firebase Authentication.
-   **Real-Time Status:** Instantly see the current state (ON/OFF) of all connected relays.
-   **Individual Control:** Toggle each of the 16 relays individually.
-   **Quick Actions:** Buttons to turn all relays ON, OFF, or toggle their current state simultaneously.
-   **Device Status Dashboard:** At-a-glance view of device connectivity, last update time, and the number of active relays.
-   **Modern Tech Stack:** Built with Vite for a fast development experience and Tailwind CSS for a sleek, responsive UI.
-   **Environment-Ready:** All Firebase configuration is securely managed using environment variables.

---

## 🛠️ Tech Stack

-   **Frontend:** HTML5, Tailwind CSS, JavaScript (ES Modules)
-   **Backend & Database:** Firebase Authentication, Firebase Realtime Database
-   **Build Tool:** [Vite](https://vitejs.dev/)
-   **Icons:** [Font Awesome](https://fontawesome.com/)

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   [Node.js](https://nodejs.org/) (v16 or higher)
-   [npm](https://www.npmjs.com/) (comes with Node.js)
-   A Firebase project. If you don't have one, create one at the [Firebase Console](https://console.firebase.google.com/).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url.git
    cd firebase-loads
    ```

2.  **Install NPM packages:**
    ```bash
    npm install
    ```

3.  **Set up your Firebase Configuration:**
    Create a new file named `.env` in the root of the project folder. Copy the contents below and fill in the values from your Firebase project's settings.

    > **Important:** Vite requires client-side environment variables to be prefixed with `VITE_`.

    ```ini
    # .env

    VITE_FIREBASE_API_KEY="YOUR_API_KEY"
    VITE_FIREBASE_AUTH_DOMAIN="YOUR_AUTH_DOMAIN"
    VITE_FIREBASE_DATABASE_URL="YOUR_DATABASE_URL"
    VITE_FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
    VITE_FIREBASE_STORAGE_BUCKET="YOUR_STORAGE_BUCKET"
    VITE_FIREBASE_MESSAGING_SENDER_ID="YOUR_MESSAGING_SENDER_ID"
    VITE_FIREBASE_APP_ID="YOUR_APP_ID"
    ```

4.  **Set your Device ID:**
    Open the `js/app.js` file and update the `DEVICE_ID` constant to match the unique ID your hardware (e.g., ESP32, Raspberry Pi) uses to publish data to Firebase.

    ```javascript
    // in js/app.js
    const DEVICE_ID = 'your-unique-device-id'; // <--- Change this value
    ```

### Available Scripts

-   **To run the development server:**
    The site will be available at `http://localhost:5173` (or another port if 5173 is busy).
    ```bash
    npm run dev
    ```

-   **To build for production:**
    This will create an optimized `dist/` folder ready for deployment.
    ```bash
    npm run build
    ```

-   **To preview the production build:**
    This command serves the `dist/` folder locally to test the final build.
    ```bash
    npm run preview
    ```

---

## 🔥 Firebase Database Structure

For the web app to function correctly, your hardware device should publish data to the Firebase Realtime Database with the following structure:

```json
{
  "devices": {
    "your-unique-device-id": {
      "relays": {
        "RELAY_1": 0,
        "RELAY_2": 1,
        "RELAY_3": 0,
        "RELAY_4": 0,
        "RELAY_5": 1,
        "RELAY_6": 0,
        "RELAY_7": 0,
        "RELAY_8": 1,
        "RELAY_9": 0,
        "RELAY_10": 0,
        "RELAY_11": 0,
        "RELAY_12": 1,
        "RELAY_13": 0,
        "RELAY_14": 0,
        "RELAY_15": 1,
        "RELAY_16": 0
      },
      "last_seen": 1678886400,
      "wifi_status": "Connected"
    }
  }
}