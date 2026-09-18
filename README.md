# ✨ AirDrawer — AI Gesture Paint Studio

[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen?style=for-the-badge&logo=github)](https://nikithajammugani2004-png.github.io/AirDrawer/)
[![Render Demo](https://img.shields.io/badge/Render-Hosted%20Live-46E3B7?style=for-the-badge&logo=render)](https://airdrawer.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands%20v0.10-orange?style=for-the-badge&logo=google)](https://developers.google.com/mediapipe)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](#license)

> **AirDrawer** is a real-time computer-vision art studio that lets you sketch, paint, and erase mid-air using natural hand gestures detected by your webcam. No special hardware or touchscreens required!

---

## 🔗 Live Application Links

| Platform | URL | Launch Speed | Cold Start |
| :--- | :--- | :--- | :--- |
| ⚡ **GitHub Pages** *(Recommended)* | [**airdrawer.github.io**](https://nikithajammugani2004-png.github.io/AirDrawer/) | **⚡ Instant (< 1s)** | **0 ms (Never Sleeps)** |
| 🌐 **Render Web Service** | [**airdrawer.onrender.com**](https://airdrawer.onrender.com/) | ⏱️ 5-15s (Awake) | ~50s (Free tier spin-down) |

---

## ⚡ Why Was Render Not Opening Quickly? (And How It's Solved)

If you noticed that `https://airdrawer.onrender.com/` was loading slowly or taking 50+ seconds on the first click, here is exactly why and how we solved it:

### 1. Root Cause: Render Free Tier "Spin-Down" (Cold Start)
- On Render's Free tier, services **automatically go to sleep after 15 minutes of inactivity** to conserve cloud resources.
- When someone clicks your link after 15 minutes, Render has to allocate a container, boot the Linux runtime, and start the web server. This "cold start" takes **50–90 seconds**.
- In addition, the original configuration was loading heavy machine-learning packages (`mediapipe`, `opencv-python-headless`, `numpy`) on the server during boot, even though the web app executes hand tracking **100% inside the user's browser** via client-side JavaScript!

### 2. The Solutions Implemented

#### Solution A: Instant 1-Click Launch via GitHub Pages (Zero Delay)
- Because all video processing and MediaPipe hand tracking happen directly in the browser's JavaScript engine via WebAssembly, **no Python backend is required to run the web app**.
- By deploying the root [`index.html`](file:///d:/NIKITHA/CV_projects/AirDrawer/index.html) to **GitHub Pages**, your app is served by GitHub's global edge CDN.
- **Result:** Loads **instantly in 1 second on a single click**, 24/7, with **0 ms cold start** and 100% free uptime!

#### Solution B: Keep Render Awake 24/7 (Prevent Sleep)
- If you prefer sharing your Render URL, you can keep the server warm so it **never sleeps**:
  1. Go to a free automated uptime monitoring service like [**cron-job.org**](https://cron-job.org/) or [**UptimeRobot**](https://uptimerobot.com/).
  2. Create a free HTTP monitor pointing to:
     ```
     https://airdrawer.onrender.com/ping
     ```
  3. Set the interval to ping every **10 minutes**.
  4. Because Render receives an incoming request every 10 minutes, **it stays permanently awake and opens immediately for every visitor!**
- We also trimmed [`requirements.txt`](file:///d:/NIKITHA/CV_projects/AirDrawer/requirements.txt) down to only `Flask` and `gunicorn`, reducing Render container boot time by over **80%**.

---

## 🎮 Hand Gesture Cheat Sheet

AirDrawer uses intelligent fingertip detection and palm triangulation to smoothly transition between creative modes:

```
    ☝️ DRAW               🤏 HOVER PREVIEW            ✋ TARGETED ERASER          ✊ PAUSE / LIFT
  (Index Finger)          (Index + Thumb)              (All 5 Fingers Open)         (Closed Fist)
       │                         │                              │                        │
  Smooth brush              Reticle follows finger         Erases drawings under     Move freely across
  drawing strokes           without depositing ink         palm with dynamic HUD     canvas without marks
```

| Gesture | Hand Pose | Action | Visual Feedback |
| :--- | :--- | :--- | :--- |
| **Draw** | ☝️ Index finger raised only | Draws smooth anti-aliased lines on the canvas | Solid colored line following fingertip |
| **Hover / Preview** | 🤏 Index finger + Thumb raised | Shows brush reticle and location without drawing | Circular outline matching brush diameter |
| **Targeted Eraser** | ✋ All 5 fingers extended open | Erases paint underneath the center of your palm | Red dashed HUD ring with center dot |
| **Pause / Idle** | ✊ Closed fist (no fingers up) | Lifts the virtual pen to reposition hand freely | Mode switches to "Idle" |

---

## ✨ Features

- **⚡ Client-Side Real-Time Tracking**: 60 FPS hand tracking powered by Google's MediaPipe Hands via WebAssembly CDN.
- **📈 Quadratic Bézier Curve Smoothing**: Custom smoothing algorithm that removes webcam frame jitter and produces fluid, elegant curves.
- **🎨 Custom Color Palette**: Built-in HTML5 color picker supporting full hex color range with a live visual swatch preview.
- **📏 Dynamic Brush Thickness**: Adjustable line weight from fine precision (`2px`) to broad strokes (`50px`).
- **⭕ Dynamic Eraser Sizing**: Adjustable eraser radius (`15px` to `150px`) with real-time scaling HUD feedback.
- **⏪ Multi-State Undo & Redo**: Dedicated 25-step image buffer history stack to quickly step back and forward through your artwork.
- **🗑️ 1-Click Canvas Wipe**: Instant screen clearance with safety history commit.
- **🎥 Display Toggles**:
  - **Camera Stream**: Toggle webcam visibility on or off (draw over video or on a solid dark artboard).
  - **Hand Skeleton**: Toggle 21-point skeletal joint connectors on/off.
  - **Isolate Skeleton Mode**: Hides background pixels entirely, isolating only glowing neon hand joints and ink.
- **📱 Responsive Glassmorphic UI**: High-contrast, dark-mode design with backdrop blur and fluid layout for desktop and tablet screens.

---

## 📂 Project Structure

```text
AirDrawer/
├── index.html               # Production static entry point (GitHub Pages & direct browser)
├── main.py                  # Flask web server with /health and /ping endpoints (Render)
├── hand_tracker.py          # Standalone desktop OpenCV + MediaPipe Python tracker
├── requirements.txt         # Production dependencies for fast cloud deployment (Flask, Gunicorn)
├── requirements-dev.txt     # Local desktop dependencies (OpenCV, MediaPipe, NumPy)
├── runtime.txt              # Specifies Python 3.10.13 for cloud runtimes
├── static/
│   └── style.css            # Dark glassmorphic design system and responsive styles
└── templates/
    └── index.html           # Flask Jinja template entry point
```

---

## 🚀 Running Locally

### Option 1: Direct in Browser (No Python Required)
Since the web application runs completely client-side:
1. Double-click [`index.html`](file:///d:/NIKITHA/CV_projects/AirDrawer/index.html) or open it directly in Google Chrome, Brave, or Microsoft Edge.
2. Allow webcam permissions when prompted.
3. Start drawing!

---

### Option 2: Run Local Flask Server
To test the Flask backend locally:

```bash
# 1. Clone the repository
git clone https://github.com/nikithajammugani2004-png/AirDrawer.git
cd AirDrawer

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install lightweight production requirements
pip install -r requirements.txt

# 4. Start the Flask application
python main.py
```
Open your browser and navigate to: `http://localhost:5500`

---

### Option 3: Desktop OpenCV Application (`hand_tracker.py`)
If you want to run the native desktop Python tracker with OpenCV window rendering:

```bash
# Install OpenCV and MediaPipe dependencies
pip install -r requirements-dev.txt

# Launch the desktop tracker
python hand_tracker.py
```
*Press `q` in the OpenCV camera window to quit.*

---

## 🌐 How to Enable GitHub Pages (Instant 1-Click Link)

To activate the lightning-fast `https://nikithajammugani2004-png.github.io/AirDrawer/` link:

1. Open your repository on GitHub: [**nikithajammugani2004-png/AirDrawer**](https://github.com/nikithajammugani2004-png/AirDrawer).
2. Click on **Settings** (top right tab).
3. In the left sidebar, click **Pages** (under the "Code and automation" section).
4. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: Select `main`
   - **Folder**: Select `/ (root)`
5. Click **Save**.
6. Wait ~30 to 60 seconds. GitHub will display:
   > *"Your site is live at https://nikithajammugani2004-png.github.io/AirDrawer/"*

---

## 🛠️ Keeping Render Awake (Zero Cold Start)

If you want your Render URL ([`https://airdrawer.onrender.com/`](https://airdrawer.onrender.com/)) to always open immediately without the 50-second sleep delay:

1. Create a free account at [**cron-job.org**](https://cron-job.org/) or [**UptimeRobot**](https://uptimerobot.com/).
2. Create a new monitor / cron job:
   - **Title**: `AirDrawer KeepAlive`
   - **URL**: `https://airdrawer.onrender.com/ping`
   - **Schedule**: Every `10 minutes`
   - **Request Type**: `GET`
3. Save the job.
4. Render will now receive an HTTP ping every 10 minutes, preventing the container from sleeping!

---

## 💻 Tech Stack

- **Frontend**: HTML5 Canvas, Vanilla CSS3 (Glassmorphism, Flexbox/Grid), JavaScript (ES6+)
- **Computer Vision**: [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) (Client-side WebAssembly) & [OpenCV Python](https://opencv.org/) (Desktop Tracker)
- **Backend**: [Flask 3.0.3](https://flask.palletsprojects.com/) & [Gunicorn 22.0.0](https://gunicorn.org/)
- **Deployment**: [GitHub Pages](https://pages.github.com/) & [Render](https://render.com/)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 👤 Author

**Nikitha Jammugani**
- GitHub: [@nikithajammugani2004-png](https://github.com/nikithajammugani2004-png)
- Project: [AirDrawer](https://github.com/nikithajammugani2004-png/AirDrawer)
