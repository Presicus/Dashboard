from CarCommunication.threadwithstop import ThreadWithStop
from CameraHandler.src.hoanchinhlane import Lane
import cv2
class Threadcamera_lane_detect(ThreadWithStop):
    def __init__(self,data_queue,data_queue_send):
        super(Threadcamera_lane_detect, self).__init__()
        self.data_queue=data_queue
        self.data_queue_send=data_queue_send
    def run(self):
            while True:
                while not self.data_queue.empty():
                    frame=self.data_queue.get()
                    # speed=4
                    lane=Lane(orig_frame=frame)
                    frame2,steer=lane.run()
                    if frame2 is not None:
                        cv2.imshow("img",frame2)
                        cv2.waitKey(1)
                    # data2 = {"action": "speed", "value": speed}
                    data1 = {"action": "steer", "value": steer}
                    # self.data_queue_send.put(data2)
                    self.data_queue_send.put(data1)
                    
    def stop(self):
        super(Threadcamera_lane_detect,self).stop()

