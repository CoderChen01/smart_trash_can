import json
import time

import serial
import serial.tools.list_ports


class BaseSerialControler:
    def __init__(self, com, bps, timeout, logger):
        self.port = com
        self.bps = bps
        self.timeout = timeout
        self.logger = logger
        try:
            self.main_engine = serial.Serial(self.port, self.bps, timeout=self.timeout)
        except Exception as e:
            logger.error('BaseSerialContorler.__init__: %s', e.__str__())

    def read_line(self):
        return self.main_engine.readline()

    def read_line_json(self):
        data = self.read_line()
        start_time = time.time()
        while not data \
              and not time.time() - start_time > 3:
            data = self.read_line()
        if not data:
            return {'id_distance': '999'}
        return json.loads(data)

    def send_data(self, data):
        self.main_engine.write(data)
