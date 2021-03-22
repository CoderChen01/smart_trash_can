import logging

import configs
from cans import SmartCan


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

class MySmartCan(SmartCan):
    def to_switch(self, class_id):
        print(class_id)
        return True

can = MySmartCan(10)
d, h = can.run()