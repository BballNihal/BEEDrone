import cv2
from ultralytics import YOLO
import math

#webcam yolo test

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  
cap.set(4, 720)   


cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 1280, 720) 

# Model
model = YOLO(r"C:\Users\nihal\OneDrive\Desktop\yolov11\datasets\runs\detect\train5\weights\best.pt")

classNames = ["chamomile", "rose", "sunflower", "tulip"]


while True:
    success, img = cap.read()
    results = model(img, stream=True)
    # print(results)

    for r in results:
        boxes = r.boxes

        for box in boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])  

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            confidence = round(box.conf[0].item(), 2)

            cls = int(box.cls[0])
            # print("Class name -->", classNames[cls])

            org = (x1, y1)
            cv2.putText(img, classNames[cls], org, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Webcam", img)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
