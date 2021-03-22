import cv2
import numpy as np


__all__ = ['preprocess']


class ResizeImage(object):
    def __init__(self, resize_short=None):
        self.resize_short = resize_short

    def __call__(self, img):
        img_h, img_w = img.shape[:2]
        percent = float(self.resize_short) / min(img_w, img_h)
        w = int(round(img_w * percent))
        h = int(round(img_h * percent))
        return cv2.resize(img, (w, h))


class NormalizeImage(object):
    def __init__(self, scale=None, mean=None, std=None):
        self.scale = np.float32(scale if scale is not None else 1.0 / 255.0)
        mean = mean if mean is not None else [0.485, 0.456, 0.406]
        std = std if std is not None else [0.229, 0.224, 0.225]

        shape = (1, 1, 3)
        self.mean = np.array(mean).reshape(shape).astype('float32')
        self.std = np.array(std).reshape(shape).astype('float32')

    def __call__(self, img):
        return (img.astype('float32') * self.scale - self.mean) / self.std


class CropImage(object):
    def __init__(self, size):
        if type(size) is int:
            self.size = (size, size)
        else:
            self.size = size

    def __call__(self, img):
        w, h = self.size
        img_h, img_w = img.shape[:2]
        w_start = (img_w - w) // 2
        h_start = (img_h - h) // 2

        w_end = w_start + w
        h_end = h_start + h
        return img[h_start:h_end, w_start:w_end, :]


class ToTensor(object):
    def __init__(self):
        pass

    def __call__(self, img):
        img = img.transpose((2, 0, 1))
        return img


def preprocess(img):
  size = (224, 224)
  origin = img.copy()
  resize_op = ResizeImage(resize_short=256)
  img = resize_op(img)
  resize = img.copy()
  crop_op = CropImage(size)
  img = crop_op(img)
  img_mean = [0.485, 0.456, 0.406]
  img_std = [0.229, 0.224, 0.225]
  img_scale = 1.0 / 255.0
  normalize_op = NormalizeImage(
      scale=img_scale, mean=img_mean, std=img_std)
  img = normalize_op(img)
  tensor_op = ToTensor()
  img = tensor_op(img)
  return size, img
