from parse_data import get_converted_data
from queue import Full, Empty
import time


class Stream:
    DEVICE_ONLINE = False
    COUNT = 0

    def __init__(self, que_message, que_stop):
        self.tcp_ip = '127.0.0.1'
        self.tcp_port = 4001
        self._q = que_message
        self._q_stop = que_stop
        self.stop_tcp = False

    def tcp_stream(self, tcp_ip, tcp_port):
        print(tcp_ip, tcp_port)

        self.stop_tcp = False
        while not self.stop_tcp:

            try:
                self.stop_tcp = self._q_stop.get_nowait()
            except Empty:
                self.stop_tcp = False

            if self.stop_tcp:
                break
            Stream.COUNT += 1
            time.sleep(2)
            try:
                with open('gps_record_3.txt', 'rb') as file:
                    data_buffer = file.read()
                self.message_parser(self._q, data_buffer)
                Stream.DEVICE_ONLINE = True

            except(FileNotFoundError, OSError):
                Stream.DEVICE_ONLINE = False
                print("file not Find")
        print("Streaming STOPPED")
        Stream.DEVICE_ONLINE = False

    def message_parser(self, que, data):
        q = que
        test = bytearray(data)

        start_delimiters = []
        end_delimiters = []
        for i in range(len(test) - 1):

            if test[i:i + 2] == b'\x10\xff':
                start_delimiters.append(i)
                continue
            if start_delimiters:
                if test[i:i + 2] == b'\x10\x03':
                    end_delimiters.append(i)
                continue

        for j in range(1, len(test) - 2):
            try:
                packet = test[start_delimiters[j]:end_delimiters[j] + 2]
            except IndexError:
                packet = []

            if len(packet) != 31:
                continue
            else:
                get_converted_data(que=q, data=packet)
