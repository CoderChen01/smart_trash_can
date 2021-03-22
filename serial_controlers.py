# self.main_engine.write(chr(0x06).encode("utf-8")) # 十六制发送一个数据
# print(self.main_engine.read().hex()) # # 十六进制的读取读一个字节
# print(self.main_engine.read())#读一个字节
# print(self.main_engine.read(10).decode("gbk"))#读十个字节
# print(self.main_engine.readline().decode("gbk"))#读一行
# print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
# print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
# print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
# print(self.main_engine.readall())#读取全部字符。
import json
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
            if self.main_engine.is_open:
                self.ret = True
        except Exception as e:
            logger.error('BaseSerialContorler.__init__: %s', e.__str__())

    def print_name(self):
        print(self.main_engine.name)
        print(self.main_engine.port)
        print(self.main_engine.baudrate)
        print(self.main_engine.bytesize)
        print(self.main_engine.parity)
        print(self.main_engine.stopbits)
        print(self.main_engine.timeout)
        print(self.main_engine.writeTimeout)
        print(self.main_engine.xonxoff)
        print(self.main_engine.rtscts)
        print(self.main_engine.dsrdtr)
        print(self.main_engine.interCharTimeout)

    def open_engine(self):
        self.main_engine.open()

    def close_engine(self):
        self.main_engine.close()

    def print_used_com(self):
        port_list = list(serial.tools.list_ports.comports())
        self.logger.info('BaseSerialControl.print_used_com: %s', str(port_list))

    def read_size(self, size):
        return self.main_engine.read(size=size)

    def read_line(self):
        return self.main_engine.readline()

    def send_data(self, data):
        self.main_engine.write(data)

    def recive_data(self, is_all):
        self.logger.info('BaseSerialControler.recive_data: %s', 'receving data...')
        while True:
            try:
                if self.main_engine.in_waiting:
                    if not is_all:
                        for i in range(self.main_engine.in_waiting):
                            print("接收ascii数据：" + str(self.read_size(1)))
                            data1 = self.read_size(1).hex()
                            data2 = int(data1, 16)
                            if data2 == "exit":
                                break
                            else:
                                print("收到数据十六进制：" + data1 + " 收到数据十进制：" + str(data2))
                    else:
                        # 整体接收
                        # data = self.main_engine.read(self.main_engine.in_waiting).decode("utf-8")#方式一
                        data = self.main_engine.read_all()  # 方式二
                        if data == "exit":  # 退出标志
                            break
                        else:
                            print("接收ascii数据：", data)
            except Exception as e:
                print("异常报错：", e)
