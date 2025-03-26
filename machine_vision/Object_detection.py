import cv2
from ultralytics import YOLO
import threading
import logging
import yaml
import util.video_tool

# 读取配置信息
config_f = open(r'./file/config.yaml',encoding='utf-8')
config_data = yaml.load(config_f.read(),Loader=yaml.FullLoader)

# 日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s-%(levelname)s-%(message)s',
    filename='./file/run.log',
    filemode='a',
    encoding='utf-8'
)

class Detect():
    def __init__(self,fps,stop_event,url):
        self.fps = fps
        self.stop_event = stop_event
        self.video_stream = util.video_tool.VideoStream(url) # 视频处理对象
        self.model = YOLO(config_data['model_path'])
        self.detection_threshold = config_data['detection_threshold']
        self.box_id_set = set()
        self.frame_buffer = None
    def detect(self,result_callback):
        consecutive_detections = 0
        while not self.stop_event.is_set():
            try:
                frame = self.video_stream.read()
                if frame is None:
                    continue
                try:
                    height, width, _ = frame.shape
                    results = self.model.track(frame, verbose=False, persist=True)
                    detected = False
                    for result in results:
                        boxes = result.boxes
                        if boxes:
                            detected = True
                            if consecutive_detections >= self.detection_threshold:
                                for box in boxes:
                                    if box.conf.item() > config_data['conf_threshold']:
                                        x1,y1,x2,y2 = map(int,box.xyxy[0])
                                        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
                                        class_str = config_data['class_dict'][str(box.cls.item())]
                                        cv2.putText(frame, f'{class_str} {box.conf[0]:.3f}', (x1, y1 - 10),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                                        if box.id is not None and box.id.item() not in self.box_id_set:
                                            self.box_id_set.add(box.id.item())
                                            result_callback() # 回调函数
                                            consecutive_detections = 0
                    if detected:
                        consecutive_detections += 1
                    else:
                        consecutive_detections = 0
                    self.frame_buffer = self.video_stream.frame_buffer()
                except Exception as e:
                    logging.info('处理帧时出错，e:',e)
            except Exception as e:
                logging.info('取帧时出错，e:',e)

    def stop(self):
