/*
  ============================================================
  IRIS BASED LOCKING SYSTEM — ESP32 Hardware Code
  File: iris_lock.ino
  Board: ESP32-WROOM-32D
  IDE: Arduino IDE 2.3.4

  PIN CONNECTIONS:
  D12   -> LED (Anode +)
  GND   -> LED (Cathode -)
  D14   -> Servo Signal Wire
  GND   -> Servo Ground
  5V    -> Servo Power
  3.3V  -> Push Button (one end)
  D15   -> Push Button + Resistor
  GND   -> Resistor (other end)
  ============================================================
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>

// ── Wi-Fi Settings ──────────────────────────────────────────
const char* ssid     = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ── Flask Server URL ────────────────────────────────────────
// Replace with your laptop IP shown when you run main.py
const char* serverURL = "http://192.168.43.XXX:5000/authenticate";

// ── Pin Numbers ─────────────────────────────────────────────
#define LED_PIN     12
#define SERVO_PIN   14
#define BUTTON_PIN  15

// ── Servo Positions ─────────────────────────────────────────
#define LOCKED_POSITION   0
#define UNLOCKED_POSITION 90

// ── Timing ──────────────────────────────────────────────────
#define LONG_PRESS_TIME  1500
#define DOOR_OPEN_TIME   5000
#define LED_GLOW_TIME    3000

Servo myServo;
unsigned long buttonPressStart = 0;
bool isButtonHeld = false;


// ============================================================
// SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("=== IRIS LOCKING SYSTEM STARTING ===");

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);

  myServo.attach(SERVO_PIN);
  myServo.write(LOCKED_POSITION);
  Serial.println("[SETUP] Door is LOCKED.");

  digitalWrite(LED_PIN, LOW);

  connectToWiFi();
}


// ============================================================
// LOOP
// ============================================================
void loop() {
  int btnState = digitalRead(BUTTON_PIN);

  if (btnState == HIGH) {
    if (!isButtonHeld) {
      buttonPressStart = millis();
      isButtonHeld = true;
      Serial.println("[BUTTON] Button pressed...");
    }

    if ((millis() - buttonPressStart) >= LONG_PRESS_TIME) {
      Serial.println("[BUTTON] Long press! Sending to server...");
      isButtonHeld = false;
      sendAuthRequest();
    }

  } else {
    isButtonHeld = false;
  }

  delay(50);
}


// ============================================================
// CONNECT TO WI-FI
// ============================================================
void connectToWiFi() {
  Serial.print("[WIFI] Connecting to: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected!");
    Serial.print("[WIFI] ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI] Failed. Check SSID and password.");
  }
}


// ============================================================
// SEND REQUEST TO FLASK SERVER
// ============================================================
void sendAuthRequest() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Reconnecting...");
    connectToWiFi();
  }

  Serial.println("[HTTP] Sending request to Flask...");

  HTTPClient http;
  http.begin(serverURL);
  http.setTimeout(15000);

  int httpCode = http.GET();

  Serial.print("[HTTP] Response code: ");
  Serial.println(httpCode);

  if (httpCode == 200) {
    String response = http.getString();
    Serial.print("[HTTP] Response: ");
    Serial.println(response);

    if (response.indexOf("granted") >= 0) {
      grantAccess();
    } else {
      denyAccess();
    }
  } else {
    Serial.println("[HTTP] Server not reachable.");
    denyAccess();
  }

  http.end();
}


// ============================================================
// GRANT ACCESS
// ============================================================
void grantAccess() {
  Serial.println("[ACCESS] GRANTED - Opening door...");

  digitalWrite(LED_PIN, LOW);

  myServo.write(UNLOCKED_POSITION);
  Serial.println("[SERVO] Unlocked - 90 degrees");

  delay(DOOR_OPEN_TIME);

  myServo.write(LOCKED_POSITION);
  Serial.println("[SERVO] Locked - 0 degrees");
}


// ============================================================
// DENY ACCESS
// ============================================================
void denyAccess() {
  Serial.println("[ACCESS] DENIED - Iris not recognized.");

  digitalWrite(LED_PIN, HIGH);
  Serial.println("[LED] Glowing red...");

  delay(LED_GLOW_TIME);

  digitalWrite(LED_PIN, LOW);
}
```

---

## FILE 3 — Create file named: `requirements.txt`
```
opencv-python
tensorflow
flask
numpy
