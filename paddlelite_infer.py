import numpy as np
from lite import *

import configs
from preprocessing import preprocess


class Detector:
    def __init__(self, model_dir):
        config = MobileConfig()
        config.set_model_from_file(model_dir)
        self._predictor = create_paddle_predictor(config)

    @staticmethod
    def _create_inputs(im):
        """
        create yolov3 inputs
        :param im: ndarray
        :return: model input
        """
        return preprocess(im)

    @staticmethod
    def _postprocess(raw_result, threshold=0.5):
        """
        process yolov3 output
        :param raw_result: model output
        :param threshold: threshold
        :return: dict
        """
        _labels = [
            '_',
            '有害垃圾',
            '可回收垃圾',
            '厨余垃圾',
            '其他垃圾'
        ]
        _id = int(np.where(raw_result == np.max(raw_result))[0])
        if raw_result[_id] < threshold:
            return 0
        return _id

    def predict(self,
                image,
                threshold=0.5):
        """
        predict image
        :param image: ndarray
        :param threshold: threshold
        :return: result
        """
        size, food = self._create_inputs(image)
        input_tensor = self._predictor.get_input(0)
        input_tensor.resize([1, 3, size[0], size[1]])
        input_tensor.set_float_data(food.flatten())
        self._predictor.run()
        output_tensor = self._predictor.get_output(0)
        raw_result = output_tensor.float_data()
        result = self._postprocess(raw_result)
        return result
