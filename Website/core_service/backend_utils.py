
import cv2
import numpy as np
from core_service import YawnDetection


class Recognizer():
    def __init__(self, camera_src=0, username=""):


        self.camera_src = camera_src
        self.username=username
        self.camera = None

    
    def gen_frames(self):
        closed = False
        while True:
            if self.camera is None :
                self.open()
            success, frame = self.camera.read()
            print("Checking",self.username)
            frame = YawnDetection.yawn_detection_wrapper(frame,self.username)
            frame = YawnDetection.drowsiness_detection_wrapper(frame, closed, self.username)

            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def close(self):
        if self.camera is not None :
            self.camera.release()
            self.camera = None

    def open(self):
        self.camera = cv2.VideoCapture(self.camera_src)
        #self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        #self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
    def setUsername(self,username):
        self.username=username
    def status(self):
        return self.camera is not None