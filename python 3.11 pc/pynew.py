import cv2
from ultralytics import YOLO

model_path = r"C:\Users\nihal\OneDrive\Desktop\yolov11\datasets\runs\detect\train5\weights\best.pt"
model = YOLO(model_path)

class_names = ["chamomile", "rose", "sunflower", "tulip"]


stream_url = "http://192.168.1.169:81/stream"
cap = cv2.VideoCapture(stream_url)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break
    

    results = model(frame)


    for result in results:
        boxes = result.boxes  
        for box in boxes:

            x1, y1, x2, y2 = box.xyxy[0]  
            class_id = int(box.cls[0]) 
            confidence = box.conf[0]  

            label = f"{class_names[class_id]} {confidence:.2f}"
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow("Live Stream - YOLOv8 Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
