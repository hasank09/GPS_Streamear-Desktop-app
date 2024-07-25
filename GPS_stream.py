from parse_data import get_converted_data
from queue import Full, Empty
import socket
import time


class Stream:
    DEVICE_ONLINE = False

    def __init__(self, que_message, que_stop):

        self._q = que_message
        self._q_stop = que_stop
        self.stop_tcp = False

    def tcp_stream(self, tcp_ip, tcp_port):
        server_ip = tcp_ip
        server_port = tcp_port

        self.stop_tcp = False
        while not self.stop_tcp:

            try:
                self.stop_tcp = self._q_stop.get_nowait()
            except Empty:
                self.stop_tcp = False

            time.sleep(2)
            if self.stop_tcp:
                return

            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((server_ip, server_port))

                data_buffer = b''
                start_time = time.time()
                stop_rcv = False
                while not stop_rcv:
                    response = client.recv(4096)
                    response = response
                    if response:
                        data_buffer += response

                    if time.time() - start_time > 2:
                        # client.shutdown(socket.SHUT_RD)
                        client.close()
                        stop_rcv = True

                        if len(data_buffer) > 1:
                            self.message_parser(self._q, data_buffer)
                            Stream.DEVICE_ONLINE = True
            except ConnectionRefusedError:
                Stream.DEVICE_ONLINE = False
                print("Connection to GPS Lost")

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
