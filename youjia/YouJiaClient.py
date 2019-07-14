"""
Copyright 2019 Vincent Qiu
Email: nov30th@gmail.com
Description:
莱特 LaiTe Devices (laitecn) Host Connection Manager
Notice:
"""

import logging
import queue
import socket
import threading
import time
from typing import List, Dict

_LOGGER = logging.getLogger(__name__)
RETRY_SECS = 3

YOUJIA_HOSTS = {}  # type: Dict[str,YouJiaClient]

DEFAULT_SOCKET_OPTION = [(socket.SOL_TCP, socket.TCP_NODELAY, 1), ]
if hasattr(socket, "SO_KEEPALIVE"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1))
if hasattr(socket, "TCP_KEEPIDLE"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPIDLE, 1))
if hasattr(socket, "TCP_KEEPINTVL"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPINTVL, 1))
if hasattr(socket, "TCP_KEEPCNT"):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPCNT, 5))


class YouJiaClient:
    def __init__(self,
                 host_name: str,
                 host: str,
                 port: int,
                 device_id: str,
                 username: str,
                 password: str,
                 control_delay: float
                 ) -> None:
        self._sock = None  # type: socket.socket
        self._host_name = host_name  # type: str
        self._host = host  # type: str
        self._port = port  # type: int
        self._device_id = device_id.lower()  # type: str
        self._username = username  # type: str
        self._password = password  # type: str
        self._message_hex_receiver = []  # type: List
        self._message_str_receiver = []  # type: List
        self._is_connected = False
        self._control_delay = control_delay  # type: float

        self._connection_thread = threading.Thread(target=self.connect_loop)
        self._sending_str_thread = threading.Thread(target=self.sending_loop)
        # self._keep_alive_thread = threading.Thread(target=self.keep_alive_and_error_detect)

        self._connection_thread.start()
        self._sending_str_thread.start()
        # self._keep_alive_thread.start()
        self.sending_queue = queue.Queue()  # type: queue.Queue

    def is_connected(self):
        return self._is_connected

    # def keep_alive_and_error_detect(self):
    #     while True:
    #         time.sleep(5)
    #         if self._is_connected:
    #             try:
    #                 _LOGGER.warn("KEEP ALIVE.......SENDING")
    #                 self._sock.sendall(bytes([0x00, 0x01, 0x02, 0xFF]))
    #             except Exception as e:
    #                 _LOGGER.error(e)
    #                 _LOGGER.error("Keep alive error...")

    def sending_loop(self):
        while True:
            time.sleep(self._control_delay)
            item = self.sending_queue.get()
            if not self._is_connected:
                self.sending_queue.empty()
                time.sleep(3)
                continue
            _LOGGER.debug("Sending command %s", ''.join('{:02x}'.format(x) for x in item))
            self._sock.sendall(item)

    def connect_loop(self):
        server_address = (self._host, self._port)
        _LOGGER.debug('connecting to {} port {}'.format(*server_address))
        while True:
            while True:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    for name, value, value2 in DEFAULT_SOCKET_OPTION:
                        sock.setsockopt(name, value, value2)
                    self._sock = sock
                    sock.connect(server_address)
                    self._is_connected = True
                    _LOGGER.info('connected to {} port {}'.format(*server_address))
                    break
                except Exception as e:
                    self._is_connected = False
                    _LOGGER.error(e)
                    _LOGGER.error("You Jia host %s failed!", self._host_name)
                    _LOGGER.error("Can not connect to YouJia host, %s%s", self._host, self._port)
                    _LOGGER.error("Retry after %s secs...", RETRY_SECS)
                    time.sleep(RETRY_SECS)

            try:

                # Send data

                sock.sendall(bytes([0xFF, 0xFF, 0xFF, 0xFF]))

                while True:
                    data = sock.recv(512)
                    _LOGGER.debug('received {!r}'.format(data))
                    self.handle_receivers(data)

            except Exception as e:
                self._is_connected = False
                _LOGGER.error(e)
                _LOGGER.error("Host %s Connection has been closed, reconnecting...", self._host_name)
                sock.close()
                time.sleep(RETRY_SECS)

    def handle_receivers(self, data):
        if len(self._message_str_receiver) > 0:
            str_message = ''.join('{:02x}'.format(x) for x in data)  # str(binascii.hexlify(bytearray(data)))
            _LOGGER.warn("Handle string message %s", str_message)
            for receiver in self._message_str_receiver:
                try:
                    receiver(str_message)
                except Exception as e:
                    _LOGGER.fatal(e)
        for receiver in self._message_hex_receiver:
            receiver(data)

    def add_hex_receiver(self, client_hex_receiver):
        self._message_hex_receiver.append(client_hex_receiver)

    def add_str_receiver(self, client_str_receiver):
        self._message_str_receiver.append(client_str_receiver)

    def send_str_command(self, message: str) -> None:
        if self._sock is not None and self._is_connected:
            message = self._device_id + 'CDB8B4AB' + message
            _LOGGER.warn("sending bytes to host {}".format(message))
            self.sending_queue.put(bytes.fromhex(message))
        else:
            _LOGGER.error("Can not send commands as host %s is not connected", self._host_name)

    # def send_hex_command(self, message: bytes) -> None:
    #     if self._sock is not None and self._is_connected:
    #         self._sock.sendall(message)
    #     else:
    #         _LOGGER.error("Can not send commands as host %s is not connected", self._host_name)


def get_host(host_name: str) -> YouJiaClient:
    return YOUJIA_HOSTS[host_name]
