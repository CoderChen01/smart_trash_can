import json
import logging

import serial

import configs
from cans import SmartCan
from serial_controlers import BaseSerialControler


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

class MySmartCan(SmartCan):
    def to_switch(self, class_id):
        # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
        # ser.write(class_id)
        serial_controler.send_data(class_id)
        print(serial_controler.read_line())
        # retjson = json.loads(serial_controler.read_line())
        # print(retjson)
        return True

can = MySmartCan(10, detected_num=2, display_interval=1)
d, h = can.run()
