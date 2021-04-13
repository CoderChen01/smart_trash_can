import time

import configs
from cans import BaseSamartCan


class DeceiveSmartCan(BaseSamartCan):
    def __init__(self, all_time, inspection_interval=1, detected_num=5, infer='paddlelite_infer'):
        super(DeceiveSmartCan, self).__init__(all_time, inspection_interval, detected_num, infer)
        self.infer = infer
        self.all_time = all_time * 60
        self.inspection_interval = inspection_interval
        # When a certain category is detected 'detected_num' times,
        # the final judgment is that category
        self.detected_num = detected_num
        self.deceive_list = [1,3,3,2]

    def run(self):  # run trash can
        self._handle_result()

    def _handle_result(self):
        for result in self._handler():
            print(result['text'], ' is current can full: ' + str(result['is_full']))

    def _handler(self):
        for class_id in self.deceive_list:
            time.sleep(8)
            handle_result = {}
            text = configs.PREDICT_LABELS[class_id]
            retval = self.to_switch(str(class_id).encode('utf8'))
            handle_result['class_id'] = int(class_id)
            handle_result['text'] = '{id}  {class_name}  {num}  OK' \
                .format(id=class_id, class_name=text, num=1)
            # Load testing
            if not retval:
                handle_result['is_full'] = False
                yield handle_result
                continue
            current_class_id = retval['class_id']
            class_distance = retval['id_distance']
            if class_distance / configs.HEIGHT >= configs.HEIGHT_THRESHOLD \
                    and current_class_id != configs.NO_TRASH_ID:
                handle_result['is_full'] = True
            else:
                handle_result['is_full'] = False
            yield handle_result

    def to_switch(self, class_id):  # garbage disposal
        raise NotImplementedError('You must implement to_switch method')
