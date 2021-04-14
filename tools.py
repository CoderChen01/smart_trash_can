import base64
from PIL import Image, ImageDraw, ImageFont

import cv2

import configs


FONT_SYTLE = ImageFont.truetype(configs.IMAGE_FONT, 25)


def draw_image(img, text, color):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), '{}'.format(text), color, font=FONT_SYTLE)
    return img


def cv2base64(image):
    base64_str = cv2.imencode('.jpg',image)[1].tostring()
    base64_str = base64.b64encode(base64_str).decode('utf8')
    return base64_str


def id2data(_id):
    _labels = [
        '_',
        '有害垃圾',
        '可回收垃圾',
        '厨余垃圾',
        '其他垃圾'
    ]
    class_name, object_name = configs.PREDICT_LABELS[_id].split('/')
    class_id = _labels.index(class_name)
    return {
        'class_id': str(class_id),
        'class_name': class_name,
        'object_name': object_name
    }