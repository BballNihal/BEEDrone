import time
import cv2
import threading
import requests
import numpy as np
import FreeSimpleGUI as sg
from ultralytics import YOLO

# YOLO model setup
model_path = r"C:\Users\nihal\OneDrive\Desktop\yolov11\datasets\runs\detect\train5\weights\best.pt"
model = YOLO(model_path)
model.fuse()  # Optional: improves speed slightly

# Turn off Ultralytics logging
import logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

class_names = ["chamomile", "rose", "sunflower", "tulip"]

ESP32 = "http://192.168.1.133"
ESP32_IP = "http://192.168.1.133:85"
stream_url = "http://192.168.1.133:81/stream"

# Try setting the resolution
try:
    requests.get(f"{ESP32}/control?var=framesize&val=10", timeout=2)
    print("[INFO] Camera resolution set to VGA")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Failed to set resolution: {e}")

# Open video stream
cap = cv2.VideoCapture(stream_url)

frame_buffer = []
frame_lock = threading.Lock()

last_direction = None
last_command_time = 0
COMMAND_DELAY = 1.0  

# Event used to pause all HTTP commands
pause_http_event = threading.Event()

def receive_frames():
    while True:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                frame_buffer.append(frame)
                if len(frame_buffer) > 20:
                    frame_buffer.pop(0)
        else:
            print("Camera disconnected. Attempting to reconnect.")
            time.sleep(5)

def send_command(direction):
    global last_direction, last_command_time

    if pause_http_event.is_set():
        return  # Skip sending if pause is active

    current_time = time.time()
    if direction != last_direction or (current_time - last_command_time) > COMMAND_DELAY:
        url = f"{ESP32_IP}/move?dir={direction}"
        print(f"[COMMAND SENT] {url}")
        try:
            response = requests.get(url, timeout=2)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send command: {e}")
        last_direction = direction
        last_command_time = current_time

def control_led(state):
    if pause_http_event.is_set():
        return  # Skip sending if paused

    url = f"{ESP32_IP}/led_{'on' if state else 'off'}"
    try:
        response = requests.get(url, timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send LED command: {e}")

def process_yolo(frame):
    results = model(frame, verbose=False)
    detection_made = False

    # Loop through each detection result
    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = float(box.conf[0])
            if confidence < 0.40:
                continue

            class_id = int(box.cls[0])
            if class_names[class_id] == "rose":
                continue 
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"{class_names[class_id]} {confidence:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            detection_made = True

            box_area = (x2 - x1) * (y2 - y1)
            frame_area = frame.shape[0] * frame.shape[1]

            # Stop command if the object is close enough
            if box_area > 0.25 * frame_area:
                send_command("stop")
                return frame, detection_made

            h, w, _ = frame.shape
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            if center_x < w / 3:
                send_command("left")
            elif center_x > 2 * w / 3:
                send_command("right")
            elif center_y < h / 3:
                send_command("up")
            elif center_y > 2 * h / 3:
                send_command("down")
            else:
                send_command("forward")

            return frame, detection_made

    # If no detections were made, stop the drone
    send_command("wait")
    return frame, detection_made

# GUI Setup using PySimpleGUI
class DroneControlApp:
    def __init__(self):
        self.window = sg.Window("Drone Controller", layout=self.create_layout(), finalize=True)

        self.last_direction = None
        self.switch_state = False
        self.pause_http_event = threading.Event()

    def create_layout(self):
        layout = [
            [sg.Image(filename='', key='-IMAGE-', size=(640, 480))],
            [sg.Button("Arm"), sg.Button("Dearm"), sg.Button("Toggle Switch")],
            [sg.Text("Switch is OFF", key='-SWITCH_STATE-')],
            [sg.Text("Directions Sent: None", key='-DIRECTION_LABEL-')],
        ]
        return layout

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_bytes = cv2.imencode('.png', frame_rgb)[1].tobytes()
        self.window['-IMAGE-'].update(data=img_bytes)

    def arm_system(self):
        self.pause_http_event.set()
        try:
            requests.get(f"{ESP32_IP}/arm", timeout=2)
            sg.popup("Armed", "Drone Armed Successfully!")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send arm command: {e}")
        time.sleep(1.5)
        self.pause_http_event.clear()

    def dearm_system(self):
        self.pause_http_event.set()
        try:
            requests.get(f"{ESP32_IP}/dearm", timeout=2)
            sg.popup("Dearmed", "Drone Dearmed Successfully!")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send dearm command: {e}")
        time.sleep(1.5)
        self.pause_http_event.clear()

    def toggle_switch(self):
        self.switch_state = not self.switch_state
        action = 'switch_on' if self.switch_state else 'switch_off'
        self.pause_http_event.set()
        try:
            requests.get(f"{ESP32_IP}/{action}", timeout=2)
            self.window['-SWITCH_STATE-'].update(f"Switch is {'ON' if self.switch_state else 'OFF'}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send switch command: {e}")
        time.sleep(0.5)
        self.pause_http_event.clear()

    def handle_events(self):
        while True:
            event, values = self.window.read(timeout=10)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Arm':
                self.arm_system()
            elif event == 'Dearm':
                self.dearm_system()
            elif event == 'Toggle Switch':
                self.toggle_switch()
        self.window.close()

# Start receiving frames from the stream
receive_thread = threading.Thread(target=receive_frames, daemon=True)
receive_thread.start()

# Initialize the GUI
app = DroneControlApp()

# Start processing frames and updating the GUI
while True:
    event, values = app.window.read(timeout=10)
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Arm':
        app.arm_system()
    elif event == 'Dearm':
        app.dearm_system()
    elif event == 'Toggle Switch':
        app.toggle_switch()

    if frame_buffer:
        with frame_lock:
            frame = frame_buffer[-1].copy()

        frame, detection_made = process_yolo(frame)

        directions = "Directions Sent: None"
        if detection_made:
            directions = f"Directions Sent: {last_direction}"
        app.window['-DIRECTION_LABEL-'].update(directions)

        app.update_frame(frame)

cap.release()
app.window.close()
