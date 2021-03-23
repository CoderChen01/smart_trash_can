import time
import logging
import importlib
import multiprocessing as mp

import cv2
import numpy as np

import configs
from tools import draw_image


logger = logging.getLogger(configs.LOGGER_NAME)


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
        # When a certain category is detected 'detected_num' times,
        # the final judgment is that category
        self.detected_num = detected_num
        self.display_interval = display_interval
        self.shared_queue = mp.Queue()  # for storing images
        self._is_run = mp.Value('i', 0)  # for storing runing status

    def to_switch(self, class_id):  # garbage disposal
        raise NotImplementedError('You must implement to_switch method')

    def run(self):  # run trash can
        return self._run_can()

    def get_predictor(self):  # get a trash classifier
        if self.infer == 'paddle_inference_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLE_INFERENCE_MODEL_DIR)
        elif self.infer == 'paddlelite_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLELITE_MODEL)
        else:
            logger.error('SmartCan.get_predictor: %s',
                         'The Infer parameter can only be paddle_inference_infer'
                         ' or paddlelite_infer!')
            self.set_run_status(False)
            return
        return predictor

    def _handler(self):
        raise NotImplementedError('You must implement _handler method')

    def _detector(self):  # get pictures in real time
        start_time = time.time()
        capture = cv2.VideoCapture(configs.CAMERA_FILE)
        if not capture.isOpened():
            EXIT = -1
            logger.error('SmartCan._detector: %s',
                         'Can\'t turn on the camera')
            capture.release()
            self.set_run_status(False)
            return
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
            self.shared_queue.put(frame)
            time.sleep(self.inspection_interval)

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


class SmartCan(BaseSamartCan):
    def to_switch(self, class_id):
        raise NotImplementedError('You must implement to_switch method')

    def _handler(self):
        predictor = self.get_predictor()
        # initial
        count = 0
        class_list_len = len(configs.PREDICT_LABELS)
        class_num = [0] * class_list_len
        start_time = time.time()
        cv2.namedWindow('display', cv2.WINDOW_NORMAL)
        # start handling
        logger.info('SmartCan._handler: %s', 'start handling images...')
        while True:
            if time.time() - start_time >= self.all_time:
                self.set_run_status(False)
                return
            if not self.get_run_status():
                return
            # predict image
            frame = self.shared_queue.get()
            result = predictor.predict(frame)
            class_id = result['class_id']
            text = result['text']
            # display image
            if count == self.display_interval:
                text = '{id}  {class_name}  {num}  OK'.format(id=class_id, class_name=text, num=1)
                img = draw_image(frame, text, (0, 255, 0))
                cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2RGB)
                cv2.imshow('display', img)
                count = 0
            else:
                count += 1
            # handle prediction result
            class_num[result['class_id']] += 1
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
            if class_distance / configs.HEIGHT >= configs.HEIGHT_THRESHOLD:
                logger.info('SmartCan._handler: %s', '{id} can is full'.format(id=current_class_id))
                pass



