import time
import logging
import importlib

import configs
from tools import cv2base64, id2data
from good_videocapture import GoodVideoCpature


logger = logging.getLogger(configs.LOGGER_NAME)


class BaseSamartCan:
    def __init__(self,
                 all_time,
                 detected_num=5,
                 infer='paddlelite_infer'):
        self.infer = infer
        self.all_time = all_time * 60
        # When a certain category is detected 'detected_num' times,
        # the final judgment is that category
        self.detected_num = detected_num
        self.predictor = self._get_predictor()

    def run(self):  # run trash can
        self.handle_result()

    def handle_result(self):
        for result in self._handler():
            print(result['text'], ' is current can full: ' + str(result['is_full']))

    def _provider(self):  # get pictures in real time
        start_time = time.time()
        capture = GoodVideoCpature.create(configs.CAMERA_FILE)
        capture.start_read()
        if not capture.is_started():
            logger.error('BaseSamartCan._provider: %s',
                         'Can\'t turn on the camera')
            capture.stop_read()
            capture.release()
            return
        logger.info('BaseSmartCan._provider: %s', 'start get iamges...')
        while True:
            if time.time() - start_time >= self.all_time:
                capture.release()
                return
            retval, frame = capture.read_latest_frame()
            if not retval:
                logger.warning('BaseSamartCan._provider: %s',
                               'No frame was read')
                break
            yield frame

    def _handler(self):
        # initial
        class_list_len = len(configs.PREDICT_LABELS)
        class_num = [0] * class_list_len
        logger.info('SmartCan._handler: %s', 'start handling images...')
        for frame in self._provider():
            # predict image
            _id = self.predictor.predict(frame, configs.INFER_THRESHOLD)
            # handle prediction result
            handle_result = {}
            class_num[_id] += 1
            max_num = max(class_num)
            if max_num < self.detected_num:
                continue
            _id = class_num.index(max_num)
            if not _id:
                continue
            class_info = id2data(_id)
            class_id = class_info['class_id']
            logger.info('SmartCan._handler: %s', 'class is ' + class_info['object_name'])
            retval = self.to_switch(class_id.encode('utf8'))
            handle_result['status'] = True
            handle_result['image'] = cv2base64(frame)
            handle_result['message'] = {}
            handle_result['message']['num'] = _id
            handle_result['message']['class'] = class_info['object_name']
            handle_result['distance'] = retval['id_distance']
            class_num = [0] * class_list_len
            yield handle_result

    def _get_predictor(self):  # get a trash classifier
        if self.infer == 'paddle_inference_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLE_INFERENCE_MODEL_DIR)
        elif self.infer == 'paddlelite_infer':
            infer_module = importlib.import_module(self.infer)
            predictor = infer_module.Detector(configs.PADDLELITE_MODEL)
        else:
            logger.error('BaseSamartCan.get_predictor: %s',
                         'The Infer parameter can only be paddle_inference_infer'
                         ' or paddlelite_infer!')
            return
        return predictor

    def to_switch(self, class_id):  # garbage disposal
        raise NotImplementedError('You must implement to_switch method')
