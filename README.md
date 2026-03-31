# 👁️ Iris Based Locking System

> A biometric door lock system using iris recognition — built with **ESP32**, **Python (OpenCV + TensorFlow + Flask)**, controlled via Wi-Fi.  
> Mini Project | ECE Department | BITM Ballari | VTU 2024–25

---

## 📌 Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Hardware Components](#hardware-components)
- [Hardware Wiring](#hardware-wiring)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Results](#results)
- [Limitations & Future Scope](#limitations--future-scope)
- [Team](#team)

---

## 🔍 Overview

Traditional security methods like passwords, PINs, and keys can be stolen, guessed, or lost. This project replaces them with **iris biometric authentication**.

Every person's iris has a unique pattern that stays the same throughout their life. Our system:
- Stores reference iris images in a folder on the laptop
- Takes a new photo via mobile phone camera
- Compares it using **OpenCV + TensorFlow** running on the laptop
- Sends the result to **ESP32** over Wi-Fi
- ESP32 **unlocks the door** (servo motor) or **glows LED** for denial

---

## 🔄 How It Works

```
1. Iris images of authorized users are saved in the iris_images/ folder

2. Python (main.py) starts a Flask server on the laptop

3. User presses and holds the push button on the ESP32 circuit

4. ESP32 connects to Flask server over Wi-Fi and requests authentication

5. Mobile phone camera captures the user's eye and sends the photo to Flask

6. Flask processes the image:
      OpenCV  → grayscale, blur, eye detection, crop, normalize
      TensorFlow CNN → extracts 128-D feature vector
      Cosine similarity → compares with all stored iris images

7. If similarity ≥ 0.80 → GRANTED
      ESP32 rotates servo motor to 90° → Door opens for 5 seconds → Locks again

8. If similarity < 0.80 → DENIED
      ESP32 turns on LED for 3 seconds
```

---

## 🛠️ Tech Stack

### Python (all in one file — `main.py`)
| Library | Purpose |
|---------|---------|
| `opencv-python` | Image preprocessing — grayscale, blur, eye detection, crop |
| `tensorflow` / `keras` | CNN model to extract iris feature vectors |
| `flask` | Web server — receives images, sends grant/deny response |
| `numpy` | Array operations and cosine similarity calculation |

### ESP32 (Arduino IDE)
| Library | Purpose |
|---------|---------|
| `WiFi.h` | Connect ESP32 to Wi-Fi |
| `HTTPClient.h` | Send HTTP request to Flask server on laptop |
| `ESP32Servo.h` | Control servo motor for lock/unlock |

---

## 🔧 Hardware Components

| Component | Purpose |
|-----------|---------|
| ESP32-WROOM-32D | Main microcontroller — Wi-Fi + controls all components |
| Servo Motor (SG90) | Physically rotates to lock / unlock the door |
| LED | Glows red when access is denied |
| Push Button | Long press triggers the authentication process |
| Resistor (10kΩ) | Pull-down for push button (avoids random triggers) |
| Breadboard | Circuit prototyping |
| Jumper Wires | Connections between components |
| Laptop / PC | Runs Python (main.py) + Flask server |
| Mobile Phone | Camera used to capture iris photo |

---

## 🔌 Hardware Wiring

```
ESP32-WROOM-32D Connections:

  D12   ──────────── LED (Anode / +)
  GND   ──────────── LED (Cathode / −)

  D14   ──────────── Servo Motor (Signal / Yellow wire)
  GND   ──────────── Servo Motor (Ground / Brown wire)
  5V    ──────────── Servo Motor (Power / Red wire)

  3.3V  ──────────── Push Button (one terminal)
  D15   ──────────── Push Button (other terminal) + Resistor
  GND   ──────────── Resistor (other end)
```

---

## 📁 Project Structure

```
iris-locking-system/
│
├── main.py                  ← All Python code in ONE file
│                              (OpenCV + TensorFlow + Flask)
│
├── iris_images/             ← Folder with saved iris images
│   ├── person1.jpg          ← Enrolled iris photo
│   └── person2.jpg
│
├── esp32_code/
│   └── iris_lock.ino        ← Arduino code for ESP32
│
├── requirements.txt         ← Python libraries to install
└── README.md
```

---

## ⚙️ Setup Instructions

### Step 1: Install Python Libraries
```bash
pip install opencv-python tensorflow flask numpy
```

### Step 2: Add Iris Images
- Take clear close-up photos of the eye (good lighting)
- Save them in the `iris_images/` folder
- Name the file with the person's name, e.g., `afghan.jpg`, `anusha.jpg`

### Step 3: Run the Python Server
```bash
python main.py
```
You will see output like:
```
[INFO] Loaded enrolled iris: afghan
[INFO] 1 user(s) enrolled.
[INFO] Starting Flask server...
 * Running on http://0.0.0.0:5000
```
> Note your laptop's IP address (e.g., `192.168.43.100`)

### Step 4: Flash the ESP32
1. Open `esp32_code/iris_lock.ino` in **Arduino IDE 2.3.4**
2. Edit these 3 lines:
```cpp
const char* ssid     = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://192.168.43.100:5000/authenticate";
```
3. Connect ESP32 to laptop via USB
4. Select **Board**: `ESP32 Dev Module` and correct **Port**
5. Click **Upload**
6. Press **RESET** button on ESP32

> ⚠️ Make sure your laptop and ESP32 are on the **same Wi-Fi / mobile hotspot**

### Step 5: Test
1. Long press the push button (hold for 1.5 seconds)
2. Take a photo of the eye using mobile phone and send to Flask
3. **Match** → Servo rotates to 90° → Door unlocks for 5 seconds ✅
4. **No match** → LED glows red for 3 seconds ❌

---

## 📊 Results

- ✅ Enrolled iris images loaded and processed successfully
- ✅ Mobile phone camera used to capture live iris photo
- ✅ OpenCV correctly detected and cropped eye region
- ✅ TensorFlow CNN extracted feature vectors for comparison
- ✅ Cosine similarity matching worked for registered users
- ✅ Servo motor unlocked correctly on successful match
- ✅ LED indicated denial for unrecognized iris
- ✅ Wi-Fi communication between laptop (Flask) and ESP32 confirmed

---

## ⚠️ Limitations & Future Scope

### Current Limitations
- Mobile phone must manually send image to Flask server
- System may struggle with very poor lighting conditions
- No liveness detection (could potentially be fooled by a photo)
- Only tested with a small number of enrolled users

### Future Scope
- Add dedicated IR camera for better iris imaging in all lighting
- Implement liveness detection (blink detection) to prevent spoofing
- Build a mobile app for easier image capture and sending
- Add cloud database for managing many users
- Combine with face recognition for multi-modal security

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
**University:** Visvesvaraya Technological University (VTU), Belagavi  
**Academic Year:** 2024–2025

---

## 📄 License
Developed for academic purposes under VTU. For queries, contact the authors.
