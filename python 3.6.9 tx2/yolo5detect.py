import torch
import numpy as np
import cv2
import time

class ObjectDetection:
    """
    Class implements YOLOv5 model to make inferences using OpenCV on Jetson TX2.
    """
    
    def __init__(self):
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:", self.device)

    def load_model(self):
        #loading yolo model from repository
        YOLO = r"C:\Users\nihal\OneDrive\Desktop\yolov11\yolov5"  # path to yolov5 model
        WEIGHTS = r"C:\Users\nihal\OneDrive\Desktop\yolov11\yolov5\runs\train\exp6\weights\best.pt"  # path to trained yolo weights
        model = torch.hub.load(YOLO, 'custom', path=WEIGHTS, source="local")
        return model

    def score_frame(self, frame):

        #Takes a single frame as input and scores it using YOLOv5 model.

        self.model.to(self.device)
        results = self.model(frame)  
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):

        return self.classes[int(x)]

    def plot_boxes(self, results, frame):

        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.3:  # Confidence 
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                color = (0, 255, 0)  
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        return frame
    
    def stream_video(self, url):

        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            print("Error: Couldn't open video stream.")
            return None
        return cap

    def __call__(self, stream_url):

        cap = self.stream_video(stream_url)
        if cap is None:
            return
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (640, 640))  #resize frame
            results = self.score_frame(frame)  # get results
            frame = self.plot_boxes(results, frame)  # draw boxes

            cv2.imshow("Flower Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detection = ObjectDetection()
    stream_url = "url"  # URL of the live stream
    detection(stream_url)
