<div align="center">

# Fire & Smoke Detection Web Application  
_Credits to Sayed Gamal: his Kaggle repo and dataset form the foundation of this project._

<img src="detected_fires/custom_ss.png" alt="Fire Smoke Detection Cover" width="700"/>

![Python](https://img.shields.io/badge/Python-3.12-blue)
[![Ultralytics](https://img.shields.io/badge/Ultralytics-181717?logo=github&logoColor=white)](https://github.com/ultralytics/ultralytics)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-181717?logo=github&logoColor=white)](https://github.com/ultralytics/ultralytics)
<a href="https://universe.roboflow.com/sayed-gamall/fire-smoke-detection-yolov11">
<img src="https://app.roboflow.com/images/download-dataset-badge.svg"></img>
</a>
<a href="https://www.kaggle.com/code/sayedgamal99/smoke-fire-detection-yolon11">
<img src="https://kaggle.com/static/images/open-in-kaggle.svg" alt="Open in Kaggle Notebook">
</a>

</div>

## 📌 Table of Contents

1. [Introduction](#introduction)
2. [Dataset](#dataset)
3. [Training Summary](#training-summary)
4. [Example Detections](#example-detections)
5. [Installation and Usage](#installation-and-usage)
   - [Installation](#installation)
   - [Running the Web App](#running-the-web-app)
   - [Inference](#inference)

---

## Introduction

This project is a **real-time fire and smoke detection web application** powered by YOLOv11 and a modern Vue 3 frontend. It enables users to detect fire and smoke in images or live video streams using a local camera, with instant visual alerts in the browser.

**Key Features:**
- Real-time detection using your webcam or uploaded images
- High-accuracy YOLOv11 model, fine-tuned on a large fire/smoke dataset
- User-friendly web interface (Vue 3 + Vite)
- Local deployment (no cloud or messaging integration required)
- Visual alert system for detected fire/smoke events

---

## Dataset

The model is trained on the [Fire & Smoke Detection YOLOv11 dataset](https://universe.roboflow.com/sayed-gamall/fire-smoke-detection-yolov11) (by Sayed Gamal), containing **10,463 annotated images**:

| Split      | Images | Annotations |
| ---------- | ------ | ----------- |
| Training   | 9,156  | 27,468      |
| Validation | 872    | 2,616       |
| Test       | 435    | 1,305       |

**Classes:** `Fire` (0), `Smoke` (1)  
**Annotation Format:** YOLOv11-compatible bounding boxes

```python
# Download dataset via Roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("sayed-gamall").project("fire-smoke-detection-yolov11")
dataset = project.version(2).download("yolov11")
```

---

## Training Summary

- **Model:** YOLOv11n (nano)
- **Epochs:** 250 (early stopping at best epoch)
- **Batch size:** 32
- **Image size:** 640x640
- **Best Epoch:** 92

### Final Validation Results

| Metric        | Value     |
| ------------- | --------- |
| Precision (P) | **0.806** |
| Recall (R)    | **0.717** |
| mAP@50        | **0.770** |
| mAP@50-95     | **0.492** |

#### Class-Specific Performance

| Class     | Precision | Recall | mAP@50 | mAP@50-95 |
| --------- | --------- | ------ | ------ | --------- |
| **Fire**  | 0.813     | 0.806  | 0.828  | 0.513     |
| **Smoke** | 0.800     | 0.629  | 0.711  | 0.472     |

---

## Example Detections

Here are examples from the test set and live webcam:

<div align="center">
<img src="data/ex1.png" alt="Example 1" width="250"/>
<img src="data/ex2.png" alt="Example 2" width="250"/>
<img src="data/ex3.png" alt="Example 3" width="250"/>
</div>

---

## Installation and Usage 🚀

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/fire-smoke-webapp.git
   cd fire-smoke-webapp
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

### Running the Web App

1. **Start the backend (Flask):**
   ```bash
   python app.py
   ```
   By default, this runs on [http://localhost:5000](http://localhost:5000).

2. **Start the frontend (Vue 3 + Vite):**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

### Inference

- **Webcam Detection:**  
  Use the web interface to start real-time detection from your webcam. Detected fire/smoke will trigger an alert in the browser.

- **Image Detection:**  
  Upload an image via the web interface to see detection results.

- **Command-line Inference:**  
  You can also run:
  ```bash
  yolo detect predict model=models/best_nano_111.pt source=data/house.png conf=0.35 iou=0.1
  ```
  or for webcam:
  ```bash
  yolo detect predict model=models/best_nano_111.pt source=0 conf=0.35 iou=0.1 show=True
  ```

---

## Credits

- **Dataset & Baseline:** [Sayed Gamal](https://www.kaggle.com/sayedgamal99)  
- **Original Research:** Pedro Vinícius Almeida Borges de Venâncio et al., Neural Computing and Applications, 2022

---

<div align="center">

**Protect What Matters Most – Early Detection Saves Lives**

</div>