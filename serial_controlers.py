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
        while not data:
            data = self.read_line()
        return json.loads(data)

    def send_data(self, data):
        self.main_engine.write(data)
