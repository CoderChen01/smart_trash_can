import os

BASE_DIR = os.path.dirname(__file__)

CAMERA_FILE = 0
PADDLE_INFERENCE_MODEL_DIR = os.path.join(BASE_DIR, 'paddle_inference_infer_model')
PADDLELITE_MODEL = os.path.join(BASE_DIR, 'model.nb')
IMAGE_FONT = os.path.join(BASE_DIR, 'arialuni.ttf')
INFER_THRESHOLD = 0.8
PREDICT_LABELS = [
    "无垃圾/无垃圾",
    "有害垃圾/电池",
    "可回收垃圾/易拉罐",
    "可回收垃圾/矿泉水瓶",
    "厨余垃圾/水果、蔬菜",
    "其他垃圾/烟蒂",
    "其他垃圾/砖瓦陶瓷"
]
NO_TRASH_ID = 4
LOGGER_NAME = 'smartcan'
HEIGHT = 100
HEIGHT_THRESHOLD = 0.75
MQTT_SERVER = '1.15.149.90'
MQTT_PORT = 1883
MQTT_PATH = 'smartTrash/pub'
