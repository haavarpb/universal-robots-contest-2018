import threading
import socket
import Queue
import time

class URServer:
    """ Server program enabling connection to the two UR robots """

    def __init__(self, port):
        self.qi = Queue.Queue()
        self.qo = Queue.Queue()
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.thread_listen = threading.Thread(target = self._listen)
        self.thread_listen.start()
        self.thread_send = threading.Thread(target = self._send)
        self.thread_send.start()

    def _listen(self):
        """ Mailman function """
        self.s.listen(1)
        client_socket, addr = socket.accept()
        while True:
            data = client_socket.recv(1024)
            print "Got message: ", data
            q_in.put(data)

    def _send(self):
        """ Send messages as long as it is available """
        while True:
            if not self.qo.empty():
                payload = self.qo.get_nowait()
                self.socket.send(payload)

	def getMessage(self, target):
		""" Get message from URX X = [1, 2] if any. None if none """
        if not self.qi.empty():
            return self.qi.get_nowait()
        else:
            return None

    def sendMessage(self, target, message):
        """ Send message to target UR """
		self.qo.put(message)
