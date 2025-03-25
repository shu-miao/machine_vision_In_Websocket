import logging
import threading
import time

import cv2
from collections import deque

class VideoStream:
    # 视频流处理类
    def __init__(self,src,max_duration=5,fps=24):
        self.src = src
        self.stopped = False
        self.frame = None
        self.frames = deque() # 引入队列缓存帧
        self.max_duration = max_duration
        self.fps = fps
        self.max_frames = max_duration * fps

    def start(self):
        self.stream = cv2.VideoCapture(self.src)
        if not self.stream.isOpened():
            logging.error('无法打开视频源：',self.src)
            raise ValueError('无法打开视频源：',self.src)
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if grabbed:
                self.frame = frame
                if len(self.frames) >= self.max_frames: # 如果当前累积帧超过最大值
                    try:
                        self.frames.popleft() # 抛弃最旧的帧
                    except Exception as e:
                        logging.info(f'移除旧帧失败，error：{e}')
                    self.frames.append((time.time(),frame)) # 累积新帧
                else:
                    self.frames.append((time.time(),frame)) # 累积新帧
            else:
                continue

    def read(self):
        # 取当前帧
        return self.frame

    def frame_buffer(self):
        # 取当前帧缓存池
        return [frame for timestamp, frame in self.frames]

    def stop(self):
        logging.info(f'{self.src} 停止取流')
        if not self.stopped:
            self.stopped = True
            if self.thread.is_alive():
                self.thread.join() # 等待视频线程结束
            self.stream.release() # 释放资源