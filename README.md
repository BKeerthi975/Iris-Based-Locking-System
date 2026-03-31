# 👁️ Iris Based Locking System

> A biometric authentication system using unique iris patterns to control a physical servo-based lock — built with **ESP32**, **Python**, **OpenCV**, **TensorFlow**, and **Flask**.

---

## 📌 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Hardware Components](#hardware-components)
- [Hardware Wiring](#hardware-wiring)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How It Works](#how-it-works)
- [Results](#results)
- [Limitations](#limitations)
- [Future Scope](#future-scope)
- [Team](#team)

---

## 🔍 Overview

The **Iris Based Locking System** is a mini-project developed for the Bachelor of Engineering (ECE) program at **Ballari Institute of Technology & Management**, under **Visvesvaraya Technological University (VTU)**.

Traditional security methods like passwords, PINs, and keys are vulnerable to theft or duplication. This project replaces them with **iris biometric authentication** — leveraging the fact that every individual's iris pattern is **unique and stable throughout their lifetime**.

The system:
1. Captures a live iris image via webcam
2. Processes it using **OpenCV** (segmentation, normalization)
3. Matches it against enrolled templates using a **TensorFlow CNN model**
4. Communicates the result to an **ESP32** over **Wi-Fi**
5. **ESP32** actuates a **servo motor** to unlock the door, or lights an LED for denial

---

## ✨ Features

| Feature | Details |
|--------|---------|
| 🔐 Biometric Security | Unique iris pattern for each user |
| 📡 Wireless Control | ESP32 communicates with Flask server over Wi-Fi |
| 🧠 Deep Learning | TensorFlow CNN extracts 128-D iris embeddings |
| 🔒 Physical Lock | Servo motor controls door lock mechanism |
| 💡 LED Feedback | Indicates access granted or denied |
| 🌐 Web Interface | Flask UI for enrollment and authentication |
| 🔘 Push Button | Long press triggers iris scan from hardware side |
| 👁 Contactless | No touch required — hygienic and convenient |

---

## 🛠️ Tech Stack

### Software
| Tool | Purpose |
|------|---------|
| Python 3.8+ | Core application logic |
| OpenCV (`opencv-python`) | Iris image capture & preprocessing |
| TensorFlow / Keras | CNN model for feature extraction & matching |
| Flask | Web server — bridges ESP32 ↔ Python |
| PyCharm | Python IDE |
| Arduino IDE 2.3.4 | ESP32 firmware programming |

### ESP32 Libraries
| Library | Purpose |
|---------|---------|
| `WiFi.h` | Wi-Fi connectivity |
| `HTTPClient.h` | Send HTTP GET to Flask server |
| `ESP32Servo.h` | Control servo motor |

---

## 🔧 Hardware Components

| Component | Qty | Purpose |
|-----------|-----|---------|
| ESP32-WROOM-32D | 1 | Main microcontroller with Wi-Fi |
| Servo Motor (SG90 / MG90S) | 1 | Lock/unlock mechanism |
| LED (Red) | 1 | Denial indicator |
| Push Button | 1 | Trigger iris scan |
| Resistor (10kΩ) | 1 | Pull-down for push button |
| Breadboard | 1 | Prototyping |
| Jumper Wires | — | Connections |
| USB Cable | 1 | Power + programming ESP32 |
| Webcam / Laptop Camera | 1 | Iris capture |

---

## 🔌 Hardware Wiring

```
ESP32-WROOM-32D Pin Connections:

┌──────────────┬─────────────────────────────┐
│  ESP32 Pin   │  Connected To               │
├──────────────┼─────────────────────────────┤
│  D12         │  LED Anode (+)              │
│  GND         │  LED Cathode (−)            │
│  D14         │  Servo Signal (Yellow/White)│
│  GND         │  Servo Ground (Brown/Black) │
│  5V (VIN)    │  Servo Power (Red)          │
│  3.3V        │  Push Button (one terminal) │
│  D15         │  Push Button + Resistor     │
│  GND         │  Resistor other end         │
└──────────────┴─────────────────────────────┘
```

> 💡 Make sure ESP32 and the PC running Flask are on the **same Wi-Fi network**.

---

## 🏗️ System Architecture

```
[Webcam / Camera]
       │
       ▼
[Python + OpenCV]         ← Captures & preprocesses iris image
       │
       ▼
[TensorFlow CNN Model]    ← Extracts 128-D feature embedding
       │
       ▼
[Cosine Similarity Match] ← Compares with enrolled templates
       │
       ▼
[Flask Web Server]        ← Sends HTTP response (granted/denied)
       │  (Wi-Fi)
       ▼
[ESP32-WROOM-32D]         ← Receives response
       │
  ┌────┴────┐
  ▼         ▼
[Servo]   [LED]
(UNLOCK)  (DENY)
```

---

## 📁 Project Structure

```
iris-locking-system/
│
├── server/
│   ├── app.py                  # Flask web server (main entry point)
│   ├── iris_processing.py      # OpenCV iris detection & preprocessing
│   ├── iris_model.py           # TensorFlow CNN model definition & matching
│   ├── enroll_iris.py          # Script to enroll a new user
│   ├── iris_model.h5           # (Generated after training)
│   ├── enrolled_iris/          # Stored iris feature templates (.npy files)
│   └── templates/
│       └── index.html          # Web UI for enrollment & authentication
│
├── esp32_code/
│   └── iris_lock.ino           # Arduino firmware for ESP32
│
├── requirements.txt            # Python dependencies
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Arduino IDE 2.3.4 with ESP32 board support
- A webcam (built-in or external)
- ESP32 and ESP32Servo library installed in Arduino IDE

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/iris-locking-system.git
cd iris-locking-system
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Enroll a User
```bash
cd server

# From camera:
python enroll_iris.py --name YourName

# From an image file:
python enroll_iris.py --name YourName --image path/to/eye_photo.jpg

# List enrolled users:
python enroll_iris.py --list
```

### Step 4: Run the Flask Server
```bash
python app.py
```
> Note the URL shown — e.g., `http://192.168.1.100:5000`  
> Copy this URL — you'll paste it into the ESP32 code.

### Step 5: Flash the ESP32

1. Open `esp32_code/iris_lock.ino` in Arduino IDE
2. Edit these lines:
   ```cpp
   const char* ssid     = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* serverURL = "http://192.168.1.100:5000/capture";  // Flask URL
   ```
3. Connect ESP32 via USB → Select board `ESP32 Dev Module` and correct COM port
4. Click **Upload**
5. Press **RESET** button on ESP32

### Step 6: Test the System

- Long press the push button on the hardware
- The ESP32 sends a request to Flask
- Flask activates the webcam, captures your iris, and returns granted/denied
- **Match** → Servo unlocks door for 5 seconds ✅
- **No Match** → LED glows red for 3 seconds ❌

---

## 🔄 How It Works

### Enrollment
1. User runs `enroll_iris.py`
2. Webcam captures eye image
3. OpenCV detects the iris region using Haar cascade + HoughCircles
4. Image is resized to 128×128 and normalized
5. TensorFlow CNN extracts a 128-dimensional feature vector
6. Feature vector is saved as `enrolled_iris/<name>.npy`

### Authentication
1. ESP32 push button triggers an HTTP GET to `/capture`
2. Flask activates the webcam and captures a live image
3. OpenCV preprocesses the iris (same pipeline as enrollment)
4. CNN extracts features from the live iris
5. Cosine similarity is computed against all enrolled users
6. If similarity ≥ 0.85 → `granted`, else → `denied`
7. Response is sent back to ESP32 as JSON
8. ESP32 actuates servo (unlock) or LED (denial) accordingly

---

## 📊 Results

- ✅ Registered users authenticated successfully with high similarity scores
- ✅ Unregistered users correctly rejected
- ✅ Servo motor correctly unlocks and re-locks after 5 seconds
- ✅ LED indicator works for all denial cases
- ✅ Wi-Fi communication between ESP32 and Flask confirmed stable
- ✅ End-to-end scan-to-result in under 3 seconds

---

## ⚠️ Limitations

- Higher initial cost compared to PIN-based systems
- Accuracy may drop under poor lighting or extreme angles
- Users with glasses, cataracts, or eye injuries may face issues
- Potential spoofing using high-resolution iris photos
- Managing large databases of users may require a proper DB backend

---

## 🚀 Future Scope

- Integrate **cloud database** (Firebase / AWS) for scalable user management
- Add **anti-spoofing** using liveness detection (blink detection, etc.)
- Combine with **facial recognition** for multi-modal biometrics
- Build a **mobile app** for remote monitoring and access logs
- Integrate with **IoT smart home** platforms (Home Assistant, etc.)
- Use a **dedicated IR camera** for better iris imaging under all lighting

---

## 👩‍💻 Team

| Name | USN |
|------|-----|
| Afghan Muthaheera | 3BR22EC005 |
| Anusha S | 3BR22EC014 |
| B Keerthi | 3BR22EC018 |
| Gangireddy Nagapoojitha | 3BR22EC044 |

**Guide:** Dr. Abdul Lateef Haroon P S *(Associate Professor)*  
**Department:** Electronics & Communication Engineering  
**Institution:** Ballari Institute of Technology & Management, Ballari  
**University:** Visvesvaraya Technological University, Belagavi  
**Academic Year:** 2024–2025

---

## 📄 License

This project was developed for academic purposes under VTU.  
For collaboration or usage, please contact the authors.
