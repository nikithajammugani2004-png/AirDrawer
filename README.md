# ✨ AirDrawer — AI Gesture Paint Studio

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-success?style=for-the-badge&logo=github)](https://nikithajammugani2004-png.github.io/AirDrawer/)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fnikithajammugani2004-png%2FAirDrawer)
[![HTML5 / Canvas](https://img.shields.io/badge/HTML5-Canvas%20API-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands%20v0.10-orange?style=for-the-badge&logo=google)](https://developers.google.com/mediapipe)
[![Vanilla JS](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](#license)

> **AirDrawer** is a real-time computer vision art studio that lets you sketch, paint, and erase mid-air using natural hand gestures detected by your webcam.
> 
> ⚡ **100% Serverless & Instant:** Runs entirely inside your browser via WebAssembly and client-side JavaScript. **No server wake-up delay, no cold starts, and zero latency!**

---

## 🚀 Live Demo & Deployment

| Platform | Live Link | Status |
| :--- | :--- | :--- |
| ⚡ **Vercel** *(Instant Edge CDN)* | [**Deploy on Vercel**](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fnikithajammugani2004-png%2FAirDrawer) | 🟢 0s Cold Start |
| 🌐 **GitHub Pages** | [**airdrawer.github.io**](https://nikithajammugani2004-png.github.io/AirDrawer/) | 🟢 0s Cold Start |

- **⚡ Launch Speed:** Under 1 second
- **⏱️ Cold Start:** **0 ms** — Never goes to sleep, opens immediately on a single click!
- **🔒 Privacy:** 100% Client-side. Webcam frames are processed directly on your device and are never sent to any external server.

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

## ✨ Features & UI Controls

- **⚡ Real-Time Client-Side Tracking**: 60 FPS hand tracking powered by Google MediaPipe Hands via WebAssembly CDN.
- **📈 Quadratic Bézier Curve Smoothing**: Adaptive smoothing filter that removes webcam jitter to produce clean, natural lines.
- **🎨 Custom Color Palette**: HTML5 hex color picker with live color swatch indicator.
- **📏 Dynamic Brush Thickness**: Adjustable slider from fine precision (`2px`) to broad strokes (`50px`).
- **⭕ Dynamic Eraser Sizing**: Adjustable eraser radius (`15px` to `150px`) with real-time scaling HUD feedback.
- **⏪ Multi-State Undo & Redo**: Dedicated 25-step image buffer history stack to step backward and forward through changes.
- **🗑️ 1-Click Clear Canvas**: Instant screen wipe with safe history backup.
- **🎥 Display Toggles**:
  - **Camera Stream**: Toggle webcam video on or off (draw directly over video or on a solid dark artboard).
  - **Hand Skeleton**: Toggle 21-point skeletal joint connectors on/off.
  - **Isolate Skeleton Mode**: Hides background completely, isolating only glowing neon hand joints and painted ink.
- **📱 Responsive Glassmorphic UI**: High-contrast dark-mode studio interface with backdrop blur and fluid layout for desktop and tablet screens.

---

## 📂 Project Structure

```text
AirDrawer/
├── .github/
│   └── workflows/
│       └── deploy.yml       # Automated GitHub Actions deployment to GitHub Pages
├── index.html               # 100% Serverless web application (GitHub Pages & direct browser)
├── static/
│   └── style.css            # Dark glassmorphic design system and responsive styles
├── hand_tracker.py          # Standalone desktop OpenCV + MediaPipe Python tracker
├── main.py                  # Optional local Flask server
├── requirements-dev.txt     # Dependencies for desktop OpenCV tracker (OpenCV, MediaPipe)
├── requirements.txt         # Dependencies for optional local Flask server (Flask, Gunicorn)
└── templates/
    └── index.html           # Flask template entry point
```

---

## 🚀 Running Locally

### Option 1: Direct in Browser (Zero Installation Required)
Since AirDrawer runs completely in the browser:
1. Double-click [`index.html`](file:///d:/NIKITHA/CV_projects/AirDrawer/index.html) or open it in Google Chrome, Microsoft Edge, or Brave.
2. Allow webcam permissions when prompted.
3. Start drawing immediately!

---

### Option 2: Run Desktop OpenCV Tracker (`hand_tracker.py`)
If you want to run the native desktop Python tracker with OpenCV window rendering:

```bash
# 1. Clone the repository
git clone https://github.com/nikithajammugani2004-png/AirDrawer.git
cd AirDrawer

# 2. Install desktop requirements
pip install -r requirements-dev.txt

# 3. Launch the desktop tracker
python hand_tracker.py
```
*Press `q` in the OpenCV camera window to quit.*

---

### Option 3: Run Optional Local Flask Server
If you prefer running via a local Python server:

```bash
pip install -r requirements.txt
python main.py
```
Open your browser at: `http://localhost:5500`

---

## 🌐 Enabling GitHub Pages (Instant Live Link)

GitHub Pages hosts your web app permanently for free with zero cold starts:

1. Open your repository on GitHub: [**nikithajammugani2004-png/AirDrawer**](https://github.com/nikithajammugani2004-png/AirDrawer).
2. Go to **Settings** (top navigation tab).
3. In the left sidebar, click **Pages** (under *Code and automation*).
4. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: Select `main`
   - **Folder**: Select `/ (root)`
5. Click **Save**.
6. Within a minute, your web app is live and opens instantly at:
   👉 **`https://nikithajammugani2004-png.github.io/AirDrawer/`**

*(Alternatively, you can select **Source: GitHub Actions** to use the included automated `.github/workflows/deploy.yml` workflow).*

---

## ⚡ Deploying on Vercel (1-Click Instant Edge Deployment)

Deploying AirDrawer to Vercel takes **under 30 seconds** and delivers global edge speeds with **0 ms cold start**:

### Method 1: 1-Click Dashboard Import (Recommended)
1. Click this button: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fnikithajammugani2004-png%2FAirDrawer)
   *(Or go to [**vercel.com/new**](https://vercel.com/new) and log in with your GitHub account).*
2. Under **"Import Git Repository"**, find and click **Import** next to `AirDrawer`.
3. Keep default settings (Framework Preset: *Other*, Root Directory: `./`).
4. Click **Deploy**.
5. Within 10 seconds, your site is live with a fast custom domain (e.g., `https://airdrawer.vercel.app`)!

### Method 2: Via Terminal (Vercel CLI)
```bash
# In your terminal, inside the AirDrawer folder:
npx vercel
```
- Log in with GitHub when prompted in the browser.
- Press **Enter** to accept the default settings.
- Run `npx vercel --prod` to deploy to production.

---

## 💻 Tech Stack

- **Client-Side Framework**: HTML5 Canvas API, Vanilla CSS3 (Glassmorphism, Flexbox/Grid), Modern JavaScript (ES6+)
- **Computer Vision**: [Google MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) (WebAssembly / CDN) & [OpenCV Python](https://opencv.org/) (Desktop Tracker)
- **Hosting / CI/CD**: [GitHub Pages](https://pages.github.com/) & [GitHub Actions](https://github.com/features/actions)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 👤 Author

**Nikitha Jammugani**
- GitHub: [@nikithajammugani2004-png](https://github.com/nikithajammugani2004-png)
- Project: [AirDrawer](https://github.com/nikithajammugani2004-png/AirDrawer)
