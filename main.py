from flask import Flask, render_template, Response, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import copy
import time

app = Flask(__name__)

# --- INITIALIZE MEDIAPIPE ---
# Hand Tracking for Drawing 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_draw = mp.solutions.drawing_utils

# Canvas States Engine
imgCanvas = None
xp, yp = 0, 0
was_drawing = False

# --- ONE EURO FILTER SMOOTHING ENGINE ---
class OneEuroFilter:
    def __init__(self, t0, mincutoff=0.3, beta=0.01, dcutoff=1.0):
        self.mincutoff = mincutoff
        self.beta = beta
        self.dcutoff = dcutoff
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = t0

    def alpha(self, cutoff, dt):
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def filter_signal(self, x, t):
        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = np.zeros_like(x, dtype=np.float64)
            self.t_prev = t
            return x
        dt = t - self.t_prev
        if dt <= 0:
            return self.x_prev
        dx = (x - self.x_prev) / dt
        edx = self.dx_prev + self.alpha(self.dcutoff, dt) * (dx - self.dx_prev)
        cutoff = self.mincutoff + self.beta * np.abs(edx)
        rx = self.x_prev + self.alpha(cutoff, dt) * (x - self.x_prev)
        self.x_prev = rx
        self.dx_prev = edx
        self.t_prev = t
        return rx

# TODO: Student - Initialize filter instances for X and Y tracking
filter_x = OneEuroFilter(time.time(), mincutoff=0.3, beta=0.01)
filter_y = OneEuroFilter(time.time(), mincutoff=0.3, beta=0.01)

# Historic Stacks for Undo / Redo
undo_stack = []
redo_stack = []
MAX_HISTORY = 20

# Configurable Global Variables Controlled by Frontend UI
current_color = (127, 0, 255) 
saved_color = (127, 0, 255)  
brush_size = 5
active_mode = "Drawing"
show_camera = True
show_skeleton = True
isolate_hand = False  # Dynamic toggle mode flag variable

## Timer configuration for auto-clear gesture
palm_start_time = None
last_palm_pos = None

# Global Shared Video Capture Instance (Prevents UI toggles from deadlocking the camera)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def save_to_history():
    global imgCanvas, undo_stack, redo_stack
    if imgCanvas is not None:
        if len(undo_stack) >= MAX_HISTORY:
            undo_stack.pop(0)
        undo_stack.append(copy.deepcopy(imgCanvas))
        redo_stack.clear()

def create_hand_mask(frame_shape, landmarks, w, h):
    """
    Generates a padded hand mask with antialiased edges.
    """
    hand_mask = np.zeros(frame_shape[:2], dtype=np.uint8)
    
    if landmarks:
        landmark_coords = np.array([(int(lm.x * w), int(lm.y * h)) for lm in landmarks], dtype=np.int32)
        
        hull = cv2.convexHull(landmark_coords)
        cv2.drawContours(hand_mask, [hull], -1, 255, thickness=cv2.FILLED)
        
        # Soft dilate kernel for smooth curved boundaries around fingers
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        hand_mask = cv2.dilate(hand_mask, kernel, iterations=1)
        
        # Fast blur to soften sharp pixel edges
        hand_mask = cv2.GaussianBlur(hand_mask, (7, 7), 0)

    return hand_mask

def apply_segmentation(frame, hand_mask):
    """
    Crops out the entire body frame background, keeping ONLY the isolated 
    hand tracking window over a clean black canvas background.
    """
    h, w, c = frame.shape
    blank_bg = np.zeros((h, w, 3), np.uint8)
    
    # Convert single-channel mask to color dimensions
    hand_mask_bgr = cv2.cvtColor(hand_mask, cv2.COLOR_GRAY2BGR)
    normalized_mask = hand_mask_bgr.astype(float) / 255.0
    
    # Isolate hand texture directly without body model interference
    foreground = cv2.multiply(normalized_mask, frame.astype(float))
    background = cv2.multiply(1.0 - normalized_mask, blank_bg.astype(float))
    
    return cv2.add(foreground, background).astype(np.uint8)

def generate_frames():
    global xp, yp, sm_x, sm_y, imgCanvas, current_color, saved_color, brush_size, active_mode, show_camera, show_skeleton, was_drawing, palm_start_time, last_palm_pos, cap
    
    # Safely re-open hardware if it closed down unexpectedly 
    if not cap.isOpened():
        cap.open(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        success, frame = cap.read()
        if not success:
            # Retry camera read without crashing the frame generator loop
            time.sleep(0.03)
            continue
            
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Initialize canvas if it doesn't exist
        if imgCanvas is None:
            imgCanvas = np.zeros((h, w, 3), np.uint8)
            # Commit first clear state to history
            undo_stack.append(copy.deepcopy(imgCanvas))

        # Resize frame to a smaller size for faster MediaPipe tracking processing
        small_frame = cv2.resize(frame, (640, 360))
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # PROCESS FRAME: Hands Landmark Detection
        rgb_small.flags.writeable = False
        hand_results = hands.process(rgb_small)
        rgb_small.flags.writeable = True

        # Initialize clean blank hand mask frame window
        final_hand_mask = np.zeros((h, w), dtype=np.uint8)

        # Draw hand features and track landmarks
        if hand_results.multi_hand_landmarks:
            # We are limiting max_num_hands=1 during initialization
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # 1. Optionally draw the MediaPipe skeleton/connections
                if show_skeleton:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                landmarks = hand_landmarks.landmark
                
                # --- CREATE CROPPED HAND MASK ---
                final_hand_mask = create_hand_mask(frame.shape, landmarks, w, h)
                
                # --- DETECT INDIVIDUAL FINGER STATES ---
                index_up  = landmarks[8].y  < landmarks[6].y
                middle_up = landmarks[12].y < landmarks[10].y
                ring_up   = landmarks[16].y < landmarks[14].y
                pinky_up  = landmarks[20].y < landmarks[18].y
                thumb_up  = landmarks[4].x  < landmarks[3].x if landmarks[17].x > landmarks[5].x else landmarks[4].x > landmarks[3].x
                
                # Extract raw coordinates
                raw_x, raw_y = int(landmarks[8].x * w), int(landmarks[8].y * h)

                # --- ADAPTIVE FILTERING & DEAD-ZONE ENGINE ---
                current_time = time.time()
                filtered_x = filter_x.filter_signal(raw_x, current_time)
                filtered_y = filter_y.filter_signal(raw_y, current_time)

                # Apply anti-jitter deadzone threshold when drawing
                if xp != 0 and yp != 0:
                    dist_moved = np.hypot(filtered_x - xp, filtered_y - yp)
                    # TODO: Student - Implement dead-zone threshold logic to fix micro-shaking
                    if dist_moved < 2.5:
                        cx, cy = xp, yp
                    else:
                        cx, cy = int(filtered_x), int(filtered_y)
                else:
                    cx, cy = int(filtered_x), int(filtered_y)

                # --- GESTURE DECISION MATRIX ---
                
                # 1. OPEN PALM -> Targeted Eraser / Auto-Clear Hold
                if index_up and middle_up and ring_up and pinky_up:
                    active_mode = "Targeted Eraser"
                    if was_drawing:
                        save_to_history()
                        was_drawing = False
                    
                    current_color = (0, 0, 0)
                    active_brush = 160
                    
                    # Auto-Clear tracking logic: Check if hand is held relatively still
                    if palm_start_time is None:
                        palm_start_time = time.time()
                        last_palm_pos = (cx, cy)
                    else:
                        # Check distance from last frame position
                        dist = np.sqrt((cx - last_palm_pos[0])**2 + (cy - last_palm_pos[1])**2)
                        if dist < 15: # Hand is holding still
                            elapsed = time.time() - palm_start_time
                            countdown = max(0, int(2 - elapsed))
                            if countdown > 0:
                                cv2.putText(frame, f"CLEARING CANVAS IN: {countdown}", (cx - 80, cy - 50), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            if elapsed >= 1.5: # Trigger auto-clear after 1.5 seconds
                                save_to_history()
                                imgCanvas.fill(0)
                                palm_start_time = None
                        else:
                            # Hand moved too much, reset timer
                            palm_start_time = time.time()
                            last_palm_pos = (cx, cy)
                    
                    cv2.circle(frame, (cx, cy), 30, (255, 255, 255), 2)
                    cv2.line(imgCanvas, (xp, yp) if xp != 0 else (cx, cy), (cx, cy), current_color, active_brush)
                    xp, yp = cx, cy

                # 2. THUMB + INDEX -> Hover / Move
                elif index_up and thumb_up and not middle_up and not ring_up and not pinky_up:
                    palm_start_time = None # Reset auto-clear timer
                    active_mode = "Hover / Move"
                    if was_drawing:
                        save_to_history()
                        was_drawing = False
                    
                    current_color = saved_color
                    xp, yp = 0, 0 
                    
                    # Enhanced HUD: Draw exact brush size preview outline with a crosshair center
                    cv2.circle(frame, (cx, cy), int(brush_size / 2), current_color, 2)
                    cv2.circle(frame, (cx, cy), 2, (0, 255, 0), cv2.FILLED)
                    
                    # HUD text is handled dynamically by the web UI header
                    pass

                # 3. INDEX UP ONLY -> Precise Drawing
                elif index_up and not middle_up and not ring_up and not pinky_up:
                    active_mode = "Drawing"
                    was_drawing = True
                    current_color = saved_color
                    
                    cv2.circle(frame, (cx, cy), int(brush_size/2) + 3, current_color, cv2.FILLED)
                    
                    if xp == 0 or yp == 0:
                        xp, yp = cx, cy
                        
                    # Smooth line rendering with anti-aliasing
                    if xp != 0 and yp != 0:
                        cv2.line(imgCanvas, (xp, yp), (cx, cy), current_color, brush_size, cv2.LINE_AA)
                    xp, yp = cx, cy

                # 4. CLOSED FIST -> Pause Drawing
                elif not index_up and not middle_up and not ring_up and not pinky_up:
                    active_mode = "Pause Drawing"
                    if was_drawing:
                        save_to_history()
                        was_drawing = False
                    # Stop tracking coordinates
                    xp, yp = 0, 0 
                    sm_x, sm_y = 0, 0 # Reset filter memory
                
                else:
                    # Keep previous coordinates briefly to maintain line continuity if gesture drops for a single frame
                    pass

        else:
            if was_drawing:
                save_to_history()
                was_drawing = False
            xp, yp = 0, 0
            sm_x, sm_y = 0, 0

        # 1. Isolate the camera background if Isolate Hand mode is enabled
        if isolate_hand and hand_results.multi_hand_landmarks:
            frame = apply_segmentation(frame, final_hand_mask)
        elif isolate_hand:
            frame = np.zeros((h, w, 3), dtype=np.uint8)

        # 2. Toggle full camera stream visibility
        if not show_camera:
            frame = np.zeros((h, w, 3), dtype=np.uint8)

        # 3. Solid mask-based overlay so pen ink remains 100% bold and vibrant
        canvas_gray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, paint_mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
        
        # Cut out exact camera pixels where ink is drawn
        frame_bg = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(paint_mask))
        
        ## Combine camera background with solid non-faded paint ink
        final_blended_frame = cv2.add(frame_bg, imgCanvas)

        # Draw the visual highlight overlay after everything else is combined so it's always on top
        if active_mode == "Targeted Eraser" and hand_results.multi_hand_landmarks:
            eraser_radius = 80  # Exactly matches active_brush / 2
            
            # Create a dedicated overlay space for the semi-transparent glow effect
            overlay = final_blended_frame.copy()
            # Draw a filled circle highlighting the eraser's footprint shape (Translucent pink/red)
            cv2.circle(overlay, (cx, cy), eraser_radius, (127, 0, 255), cv2.FILLED)
            # Blend the alpha overlay into the final frame output layer
            cv2.addWeighted(overlay, 0.25, final_blended_frame, 0.75, 0, final_blended_frame)
            
            # Draw a sharp outer circle border ring and precise center dot alignment guide
            cv2.circle(final_blended_frame, (cx, cy), eraser_radius, (255, 255, 255), 2)
            cv2.circle(final_blended_frame, (cx, cy), 4, (255, 255, 255), cv2.FILLED)

        # Encode as JPEG with 80% quality to reduce network payload and latency
        ret, buffer = cv2.imencode('.jpg', final_blended_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/style.css')
def style():
    return app.send_static_file('style.css')    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_config', methods=['POST'])
def set_config():
    global current_color, saved_color, brush_size, show_camera, show_skeleton, imgCanvas, undo_stack, redo_stack
    data = request.json
    
    if 'color' in data:
        # Convert incoming hex color into full-depth BGR tuple for OpenCV
        hex_color = data['color'].lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        saved_color = (int(b), int(g), int(r)) 
        current_color = saved_color
        
    if 'size' in data:
        brush_size = int(data['size'])
        
    if 'show_camera' in data:
        show_camera = data['show_camera']
        
    if 'show_skeleton' in data:
        show_skeleton = data['show_skeleton']
        
    if 'isolate_hand' in data:
        global isolate_hand
        # Convert incoming frontend string/boolean cleanly into a Python boolean value
        isolate_hand = str(data['isolate_hand']).lower() == 'true'
        
    if 'action' in data:
        action = data['action']
        if action == 'clear':
            if imgCanvas is not None:
                save_to_history()
                # Entirely reset digital canvas to black
                imgCanvas.fill(0)
        elif action == 'undo':
            # Need at least current state and one historic state to step back
            if len(undo_stack) > 1:
                # Store present state to redo stack
                redo_stack.append(undo_stack.pop())
                # Restore previous state
                imgCanvas = copy.deepcopy(undo_stack[-1])
        elif action == 'redo':
            if len(redo_stack) > 0:
                next_state = redo_stack.pop()
                undo_stack.append(next_state)
                imgCanvas = copy.deepcopy(next_state)
            
    return jsonify({"status": "success"})
 
@app.route('/get_mode')
def get_mode():
    global active_mode
    return jsonify({"mode": active_mode})

if __name__ == "__main__":
    import os
    # Read PORT dynamically from environment for deployment platforms, defaulting to 5500 locally
    port = int(os.environ.get("PORT", 5500))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)