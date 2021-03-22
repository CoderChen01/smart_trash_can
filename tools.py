import cv2
from PIL import Image, ImageDraw, ImageFont

import configs

FONT_SYTLE = ImageFont.truetype(configs.IMAGE_FONT, 25)


def draw_image(img,text,color):
  img=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
  draw = ImageDraw.Draw(img)
  draw.text((0, 0), '{}'.format(text), color ,font=FONT_SYTLE)
  return img