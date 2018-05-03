import threading
import socket
import Queue
import time

class ur:
    """ Server program enabling connection to the two UR robots """

    def __init__(self, port):
        self.qi = Queue.Queue()
        self.qo = Queue.Queue()
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", self.port))
        self.socket.listen(1)
        client_socket, addr = self.socket.accept()
        self.client_socket = client_socket
        self.thread_listen = threading.Thread(target = self._listen)
        self.thread_listen.start()
        self.thread_send = threading.Thread(target = self._send)
        self.thread_send.start()

    def _listen(self):
        """ Mailman function """
        while True:
            data = self.client_socket.recv(1024)
            self.qi.put(data)

    def _send(self):
        """ Send messages as long as it is available """
        while True:
            if not self.qo.empty():
                payload = self.qo.get_nowait()
                self.client_socket.send(payload)

    def getMessage(self):
        """ Get message from URX X = [1, 2] if any. None if none """
        if not self.qi.empty():
            message = self.qi.get_nowait()
            return message
        else:
            return False

    def sendMessage(self, message):
        """ Send message to target UR """
        self.qo.put(message)
