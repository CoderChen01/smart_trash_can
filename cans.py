import time
import logging
import importlib

import cv2

import configs


logger = logging.getLogger(configs.LOGGER_NAME)


class BaseSamartCan:
    def __init__(self,
                 all_time,
                 inspection_interval=1,
                 detected_num=5,
                 infer='paddlelite_infer'):
        self.infer = infer
        self.all_time = all_time * 60
        self.inspection_interval = inspection_interval
        # When a certain category is detected 'detected_num' times,
        # the final judgment is that category
        self.detected_num = detected_num
        self.predictor = self.get_predictor()

    def run(self):  # run trash can
        self._handle_result()

    def _handle_result(self):
        for result in self._handler():
            print(result['text'], ' is current can full: ' + str(result['is_full']))

    def _provider(self):  # get pictures in real time
        start_time = time.time()
        capture = cv2.VideoCapture(configs.CAMERA_FILE)
        if not capture.isOpened():
            logger.error('BaseSamartCan._provider: %s',
                         'Can\'t turn on the camera')
            capture.release()
            return
        logger.info('BaseSmartCan._provider: %s', 'start get iamges...')
        while True:
            if time.time() - start_time >= self.all_time:
                capture.release()
                return
            retval, frame = capture.read()
            if not retval:
                logger.warning('BaseSamartCan._provider: %s',
                               'No frame was read')
                break
            yield frame
            time.sleep(self.inspection_interval)

    def _handler(self):
        # initial
        class_list_len = len(configs.PREDICT_LABELS)
        class_num = [0] * class_list_len
        start_time = time.time()
        logger.info('SmartCan._handler: %s', 'start handling images...')
        for frame in self._provider():
            # predict image
            result = self.predictor.predict(frame, configs.INFER_THRESHOLD)
            class_id = result['class_id']
            text = result['text']
            # handle prediction result
            handle_result = {}
            class_num[result['class_id']] += 1
            max_num = max(class_num)
            if max_num < self.detected_num:
                continue
            class_id = str(class_num.index(max_num))
            logger.info('SmartCan._handler: %s', 'class is ' + class_id)
            retval = self.to_switch(class_id.encode('utf8'))
            handle_result['frame'] = frame
            handle_result['class_id'] = int(class_id)
            handle_result['text'] = '{id}  {class_name}  {num}  OK'\
                .format(id=class_id, class_name=text, num=1)
            class_num = [0] * class_list_len
            # Load testing
            if not retval:
                handle_result['is_full'] = False
                yield handle_result
                continue
            current_class_id = retval['class_id']
            class_distance = retval['id_distance']
            logger.info('BaseSmartCan._handler: distance is %d', class_distance)
            if class_distance / configs.HEIGHT >= configs.HEIGHT_THRESHOLD \
                and current_class_id != configs.NO_TRASH_ID:
                logger.info('SmartCan._handler: %s', '{id} can is full'.format(id=current_class_id))
                handle_result['is_full'] = True
            else:
                handle_result['is_full'] = False
            yield handle_result

    def get_predictor(self):  # get a trash classifier
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

    def __del__(self):
        cv2.destroyAllWindows()
