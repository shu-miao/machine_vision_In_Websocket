import cv2
from ultralytics import YOLO
import threading
import logging
import yaml

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
