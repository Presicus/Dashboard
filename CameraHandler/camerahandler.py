import sys
sys.path.append(r"C:\Users\PC\Desktop\Bosch_mobility\Dashboard")
from CarCommunication.threadwithstop import ThreadWithStop
from CameraHandler.threadCameralanedetect import Threadcamera_lane_detect
from CameraHandler.threadCameraobjectdetect import Threadcamera_object_detect
from multiprocessing import Queue,Pipe
import cv2
import base64
import numpy as np
class Camera(ThreadWithStop):
    def __init__(self,pipeRecv,pipeSend):
        super(Camera, self).__init__()
        self.pipeRecv=pipeRecv
        self.pipeSend=pipeSend
        self.data_queue2=Queue()
        self.data_queue_send=Queue()
        self.data_queue1=Queue()
    def run(self):        
        self.lane_detect=Threadcamera_lane_detect(self.data_queue1,self.data_queue_send,)
        self.object_detect=Threadcamera_object_detect(self.data_queue2,self.data_queue_send)
        self.lane_detect.start()
        # self.object_detect.start()
        data = {"action": "startEngine", "value": True}
        self.pipeSend.send(data)
        while True:
            self.continuos_update()
            while not self.data_queue_send.empty():
                data=self.data_queue_send.get()
                # print(data)
                # self.pipeSend.send(data)
        self.stop()

    def stop(self):
        super(Camera, self).stop()
        self.lane_detect.stop()
        self.object_detect.stop()
        self.lane_detect.join()
        self.object_detect.join()  
    def continuos_update(self):
        if self.pipeRecv.poll():
            msg = self.pipeRecv.recv() 
            if msg["action"] == "modImg":
                newFrame = cv2.imdecode(msg["value"], cv2.IMREAD_COLOR)
                newFrame = cv2.cvtColor(newFrame, cv2.COLOR_BGR2RGB)
                newFrame=cv2.resize(newFrame,(600,300))
                self.data_queue1.put(newFrame)
                self.data_queue2.put(newFrame)
if __name__ == "__main__":
    pipe1, pipe2 = Pipe()
    pipe3, pipe4 = Pipe()
    camera_instance = Camera(pipe2, pipe3)

    # Start the Camera process
    camera_instance.start()

    cap = cv2.VideoCapture("bfmc.mp4")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (600, 300))
            # Convert image to bytes and then encode it as base64
            _, img_str = cv2.imencode('.jpg', frame)
            # img_str = base64.b64encode(img_str).decode("utf-8")   
            data = {"action": "modImg", "value": img_str}
            pipe1.send(data)

    finally:
        # Stop the camera process when done
        camera_instance.stop()
        camera_instance.join()   