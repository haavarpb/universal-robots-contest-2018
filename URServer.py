import threading
import socket
import Queue
import time

class URServer:
    """ Server program enabling connection to the two UR robots """

    def __init__(self):
        print "Initiating server..."
        self._ur1_qi = Queue.Queue()
        self._ur1_qo = Queue.Queue()
        self._ur1_port = 7777
        self._ur1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ur1_socket.bind(("", self._ur1_port))
        self._ur1_thread = threading.Thread(target = self._serve, name = "UR1 server", args=(self._ur1_qi, self._ur1_qo, self._ur1_socket))
        self._ur1_thread.daemon = True
        self._ur1_thread.start()

        self._ur2_qi = Queue.Queue()
        self._ur2_qo = Queue.Queue()
        self._ur2_port = 8888
        self._ur2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ur2_socket.bind(("", self._ur2_port))
        self._ur2_thread = threading.Thread(target = self._serve, name = "UR2 server", args=(self._ur2_qi, self._ur2_qo, self._ur2_socket))
        self._ur2_thread.daemon = True
        self._ur2_thread.start()

    def _serve(self, q_in, q_out, socket):
        """ Mailman function """
        socket.listen(1)
        client_socket, addr = socket.accept()
        print "Connected to client [%s / %s]" %client_socket

        while True:
            try:
                client_socket.send(q_out.get())
            except queue.Empty:
                q_in = client_socket.recv(1024)

    def getMessage(self, target):
        """ Get message from URX X = [1, 2] if any. None if none """
        try:
            if target == "UR1":
                return self._ur1_qi.get()
            elif target == "UR2":
                return self._ur2_qi.get()
        except Queue.Empty:
            return None

    def sendMessage(self, target, message):
        """ Send message to target UR """
        if target == "UR1":
            self._ur1_qo.put(message)
        elif target == "UR2":
            self._ur2_qo.put(message)
