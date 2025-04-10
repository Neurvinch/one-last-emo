from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from tensorflow.keras.models import load_model
import dlib
from sleepy_detector import is_sleepy
import sys
import os
sys.path.append(os.path.abspath("..")) 


# Get the directory of the current file (main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level and into the models folder
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "emotion_model.h5")

emotion_model = load_model(MODEL_PATH)
 # Go one level up

from sleepy_detector import is_sleepy

from nervous_detector import is_nervous

app = FastAPI()

# Allow frontend requests (adjust for deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
emotion_model = load_model("emotion_model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        image_data = base64.b64decode(data.split(',')[1])
        np_data = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        response = {"emotion": "Unknown", "confidence": 0.0, "sleepy": False, "nervous": False}

        for rect in rects:
            landmarks = predictor(gray, rect)

            # Sleepy/Nervous detection
            response["sleepy"] = is_sleepy(landmarks)
            response["nervous"] = is_nervous(landmarks)

            # Emotion prediction
            x, y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48))
            roi = roi_gray.astype("float") / 255.0
            roi = np.expand_dims(np.expand_dims(roi, axis=0), axis=-1)

            preds = emotion_model.predict(roi)[0]
            label = emotion_labels[np.argmax(preds)]
            confidence = np.max(preds)

            response["emotion"] = label
            response["confidence"] = float(confidence)
            break  # One face at a time for now

        await websocket.send_json(response)
