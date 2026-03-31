# ============================================================
#  IRIS BASED LOCKING SYSTEM
#  File: main.py
#  Run this on your laptop/PC
#
#  What this code does:
#  1. Loads pre-saved iris images from the 'iris_images' folder
#  2. Starts a Flask web server
#  3. Receives a photo taken from mobile phone
#  4. Compares it with saved images using OpenCV + TensorFlow
#  5. Sends GRANTED or DENIED response to ESP32
# ============================================================

# ── IMPORTS ─────────────────────────────────────────────────
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from flask import Flask, request, jsonify

# ── FLASK APP ────────────────────────────────────────────────
app = Flask(__name__)

# ── FOLDER WHERE YOU SAVED IRIS IMAGES ──────────────────────
# Put your enrolled eye images here as: iris_images/name.jpg
IRIS_IMAGES_FOLDER = "iris_images"
os.makedirs(IRIS_IMAGES_FOLDER, exist_ok=True)

# ── IMAGE SIZE ───────────────────────────────────────────────
IMG_SIZE = (128, 128)

# ── MATCHING THRESHOLD ───────────────────────────────────────
# If similarity is above this value → ACCESS GRANTED
THRESHOLD = 0.80


# ============================================================
# STEP 1: PREPROCESS IMAGE (OpenCV)
# Converts any iris image into a clean 128x128 grayscale image
# ============================================================
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Reduce noise using Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Try to detect eye region using Haar Cascade
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(blurred, scaleFactor=1.1, minNeighbors=5)

    if len(eyes) > 0:
        # Crop to the first detected eye
        (x, y, w, h) = eyes[0]
        blurred = blurred[y:y+h, x:x+w]

    # Resize to standard size
    resized = cv2.resize(blurred, IMG_SIZE)

    # Improve contrast
    equalized = cv2.equalizeHist(resized)

    # Normalize pixel values to 0-1
    normalized = equalized.astype(np.float32) / 255.0

    return normalized


# ============================================================
# STEP 2: BUILD CNN MODEL (TensorFlow/Keras)
# Extracts a feature vector from iris image
# ============================================================
def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)),
        MaxPooling2D(2, 2),

        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(128, activation='relu')   # 128-D feature vector output
    ])
    return model

# Load the model once at startup
print("[INFO] Building CNN model...")
model = build_model()
print("[INFO] Model ready.")


# ============================================================
# STEP 3: GET FEATURE VECTOR FROM IMAGE
# ============================================================
def get_features(image):
    # Reshape for model input: (1, 128, 128, 1)
    img_input = image.reshape(1, 128, 128, 1)
    features = model.predict(img_input, verbose=0)
    return features.flatten()


# ============================================================
# STEP 4: COMPARE TWO FEATURE VECTORS
# Using cosine similarity
# ============================================================
def cosine_similarity(vec_a, vec_b):
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if norm == 0:
        return 0.0
    return float(dot / norm)


# ============================================================
# STEP 5: LOAD ALL SAVED IRIS IMAGES FROM FOLDER
# These are the images you uploaded before running
# ============================================================
def load_enrolled_iris():
    enrolled = {}
    for filename in os.listdir(IRIS_IMAGES_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(IRIS_IMAGES_FOLDER, filename)
            img = cv2.imread(path)
            if img is not None:
                processed = preprocess_image(img)
                features = get_features(processed)
                name = os.path.splitext(filename)[0]
                enrolled[name] = features
                print(f"[INFO] Loaded enrolled iris: {name}")
    return enrolled

print("[INFO] Loading enrolled iris images...")
enrolled_iris = load_enrolled_iris()
print(f"[INFO] {len(enrolled_iris)} user(s) enrolled.")


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def home():
    return "Iris Locking System is Running!"


# ESP32 calls this route after button press
# Mobile phone photo is sent here
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Receive image sent from mobile or ESP32
    file = request.files.get('image')
    if not file:
        return jsonify({'status': 'denied', 'message': 'No image received'})

    # Read image from request
    img_array = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'status': 'denied', 'message': 'Could not read image'})

    # Preprocess the received image
    processed = preprocess_image(img)
    live_features = get_features(processed)

    # Compare with all enrolled iris images
    best_score = 0.0
    best_match = None

    for name, stored_features in enrolled_iris.items():
        score = cosine_similarity(live_features, stored_features)
        print(f"[MATCH] {name}: {score:.4f}")
        if score > best_score:
            best_score = score
            best_match = name

    # Decision
    if best_score >= THRESHOLD:
        print(f"[ACCESS GRANTED] Match: {best_match}, Score: {best_score:.4f}")
        return jsonify({
            'status': 'granted',
            'message': f'Access granted for {best_match}',
            'score': round(best_score, 4)
        })
    else:
        print(f"[ACCESS DENIED] Best score: {best_score:.4f}")
        return jsonify({
            'status': 'denied',
            'message': 'Iris not recognized',
            'score': round(best_score, 4)
        })


# Reload enrolled images without restarting server
@app.route('/reload', methods=['GET'])
def reload_enrolled():
    global enrolled_iris
    enrolled_iris = load_enrolled_iris()
    return jsonify({'message': f'Reloaded. {len(enrolled_iris)} user(s) enrolled.'})


# ============================================================
# RUN THE FLASK SERVER
# ============================================================
if __name__ == '__main__':
    print("\n[INFO] Starting Flask server...")
    print("[INFO] Make sure your ESP32 and mobile are on the SAME Wi-Fi as this laptop.")
    print("[INFO] Copy this laptop's IP address and paste it in the ESP32 code.\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
