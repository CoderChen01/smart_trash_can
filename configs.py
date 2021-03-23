import os

BASE_DIR = os.path.dirname(__file__)

PING_NETWORK = 'www.baidu.com'
CAMERA_FILE = 1
PADDLE_INFERENCE_MODEL_DIR = os.path.join(BASE_DIR, 'paddle_inference_infer_model')
PADDLELITE_MODEL = os.path.join(BASE_DIR, 'model.nb')
IMAGE_FONT = os.path.join(BASE_DIR, 'arialuni.ttf')
INFER_THRESHOLD = 0.8
GPIO_POWER_PIN_NUM = 12
PREDICT_LABELS = [
    '其他垃圾',
    '厨余垃圾',
    '可回收垃圾',
    '有害垃圾',
    '未检测到垃圾'
]
LOGGER_NAME = 'monitor'
HEIGHT = 100
HEIGHT_THRESHOLD = 0.75
