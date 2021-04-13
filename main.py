import json
import logging

import configs
from cans import BaseSamartCan
from serial_controlers import BaseSerialControler
import paho.mqtt.client as mqtt


logger = logging.getLogger(configs.LOGGER_NAME)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('monitor.log', mode='w')
fh.setLevel(logging.ERROR)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formater = logging.Formatter('%(asctime)s %(name)s'
                             ' %(levelname)s %(message)s')
fh.setFormatter(formater)
ch.setFormatter(formater)

logger.addHandler(fh)
logger.addHandler(ch)

serial_controler = BaseSerialControler('/dev/ttyUSB0', 115200, timeout=0.5, logger=logger)

class MySmartCan(BaseSamartCan):
    def __init__(self,
                 all_time,
                 detected_num=5,
                 infer='paddlelite_infer'):
        super(MySmartCan, self).__init__(all_time, detected_num, infer)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(configs.MQTT_SERVER)
        self.mqtt_client.loop_start()

    def to_switch(self, class_id):
        serial_controler.send_data(class_id)
        retval = serial_controler.read_line_json()
        return retval

    def handle_result(self):
        for result in self._handler():
            self.mqtt_client.publish(configs.MQTT_PATH,json.dumps(result))


can = MySmartCan(999, detected_num=30)
can.run()
