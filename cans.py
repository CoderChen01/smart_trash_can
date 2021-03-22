import os
import time
import logging
import subprocess
import importlib
import multiprocessing as mp

import cv2
import numpy as np

import configs
from tools import draw_image
from gpio_controlers import GPIOControler

logger = logging.getLogger(configs.LOGGER_NAME)


def check_network():
    fnull = open(os.devnull, 'w')
    retval = subprocess.call('ping ' + configs.PING_NETWORK + ' -n 2',
                             shell=True,
                             stdout=fnull,
                             stderr=fnull)
    fnull.close()
    return False if retval else True


class BaseSamartCan:
    def __init__(self,
                 all_time,
                 inspection_interval=1,
                 detected_num=5,
                 display_interval=2,
                 infer='paddlelite_infer'):
        self.infer = infer
        self.all_time = all_time * 60
        self.inspection_interval = inspection_interval
        self.detected_num = detected_num
        self.shared_queue = mp.Queue()
        self._is_run = mp.Value('i', 0)

    def run(self):
        raise NotImplementedError('You must implement run method')

    def _handler(self):
        raise NotImplementedError('You must implement _handler method')

    def _detector(self):
        if self.infer == 'paddle_inference_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLE_INFERENCE_MODEL_DIR)
        elif self.infer == 'paddlelite_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLELITE_MODEL)
        else:
            logger.error('SmartCan._detector: %s',
                         'The Infer parameter can only be paddle_inference_infer'
                         ' or paddlelite_infer!')
            self.set_run_status(False)
            return
        start_time = time.time()
        capture = cv2.VideoCapture(configs.CAMERA_FILE)
        if not capture.isOpened():
            EXIT = -1
            logger.error('SmartCan._detector: %s',
                         'Can\'t turn on the camera')
            capture.release()
            self.set_run_status(False)
            return
        logger.info('SmartCan._detector: %s',
                    'Start detecting...')
        counter = 0
        cv2.namedWindow('display', cv2.WINDOW_NORMAL)
        while True:
            if time.time() - start_time >= self.all_time:
                capture.release()
                self.set_run_status(False)
                return
            if not self.get_run_status():
                capture.release()
                return
            retval, frame = capture.read()
            if not retval:
                logger.warning('SmartCan.detector: %s',
                               'No frame was read')
                continue
            logger.debug('SmartCan._detector: %s',
                         'predicting...')
            result = predictor.predict(frame,
                                       threshold=configs.INFER_THRESHOLD)
            logger.debug('SmartCan._detector: %s',
                         'finished...')
            self.shared_queue.put(result['class_id'])
            if counter == 2:
                logger.debug('SmartCan._detector: %s',
                             'displaying...')
                color = (0, 255, 0)
                display_image = draw_image(frame,
                                           '{class_id} {text} {class_num} OK'
                                           .format(class_id=result['class_id'],
                                                   text=result['text'],
                                                   class_num=1),
                                           color)
                display_image = cv2.cvtColor(np.asarray(display_image), cv2.COLOR_RGB2BGR)
                cv2.imshow('display', display_image)
                counter = 0
            else:
                counter += 1
            cv2.waitKey(self.inspection_interval * 1000)
            # time.sleep(self.inspection_interval)

    def to_switch(self, class_id):
        raise NotImplementedError('You must implement to_switch method')

    def _run_can(self):
        self.set_run_status(True)
        d = mp.Process(target=self._detector)
        h = mp.Process(target=self._handler)
        d.start()
        h.start()
        return d, h

    def set_run_status(self, is_run):
        if is_run:
            self._is_run.value = 1
        else:
            self._is_run.value = 0

    def get_run_status(self):
        return self._is_run.value

    def __del__(self):
        cv2.destroyAllWindows()
        GPIOControler.close()


class SmartCan(BaseSamartCan):
    def run(self):
        return self._run_can()

    def to_switch(self, class_id):
        raise NotImplementedError('You must implement to_switch method')

    def _handler(self):
        detected_num = 0
        class_list_len = len(configs.PREDICT_LABELS)
        class_num = [0] * class_list_len
        start_time = time.time()
        while True:
            if time.time() - start_time >= self.all_time:
                self.set_run_status(False)
                return
            if not self.get_run_status():
                return
            result = self.shared_queue.get()
            class_num[result] += 1
            max_num = max(class_num)
            if max_num < self.detected_num:
                continue
            class_id = str(class_num.index(max_num))
            logger.info('SmartCan._handler: %s', 'class is ' + class_id)
            retval = self.to_switch(class_id.encode('utf8'))
            class_num = [0] * class_list_len
            # Load testing
            if not retval:
                continue
            current_class_id = retval['class_id']
            class_distance = retval['id_distance']
            if class_distance / configs.HEIGHT >= 0.75:
                logger.info('SmartCan._handler: %s', '{id} can is full'.format(id=current_class_id))
                pass



