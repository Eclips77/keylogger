import cv2
import os
from datetime import datetime
import logging

class VideoRecorder:
    def __init__(self, directory="video_logs", duration=10):
        self.directory = directory
        self.duration = duration
        os.makedirs(self.directory, exist_ok=True)

    def record_video(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.directory, f"video_{timestamp}.avi")
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
        logging.info(f"Recording video to {filename}...")
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < self.duration:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            cv2.imshow('Recording', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        logging.info("Video recording completed.")
