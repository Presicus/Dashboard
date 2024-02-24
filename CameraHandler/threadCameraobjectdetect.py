import sys
sys.path.append(r"C:\Users\PC\Desktop\Work\Github\Bosch_mobility\Dashboard")
from CarCommunication.threadwithstop import ThreadWithStop
from multiprocessing import Queue
from ultralytics import YOLO
import cv2
class Threadcamera_object_detect(ThreadWithStop):
    def __init__(self,data_queue,data_queue_send):
        super(Threadcamera_object_detect, self).__init__()
        self.data_queue=data_queue
        self.data_queue_send=data_queue_send
        self.model = YOLO('last.pt')
        self.focal_length=211.75
        self.real_height=4  
        self.speed=10

    def run(self):
            data2 = {"action": "speed", "value": self.speed}
            self.data_queue_send.put(data2)
            while True:
                count=0
                while not self.data_queue.empty():   
                    frame=self.data_queue.get()
                    if frame is not None:
                        results= self.model.predict(frame,show=True)
                        cv2.waitKey(1)
                        for r in results:
                            boxes = r.boxes
                            for box in boxes:
                                count = count+1
                                h=int(box.cls[0].item())
                                class_names = r.names[box.cls[0].item()]
                                height = box.xywh[0].tolist()[3]
                                distance = self.focal_length*self.real_height/height
                                if class_names == "stop_sign" and distance < 40:
                                    data2 = {"action": "brake", "value": True}
                                    self.data_queue_send.put(data2)
                        if count == 0:
                            self.speed = 10
                            data2 = {"action": "speed", "value": self.speed}
                            self.data_queue_send.put(data2)


                                
    def stop(self):
        super(Threadcamera_object_detect,self).stop()
