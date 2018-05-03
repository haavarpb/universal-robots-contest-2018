import threading
import socket
import Queue
import time

class URServer:
    """ Server program enabling connection to the two UR robots """

    def __init__(self):
        self.qi = Queue.Queue()
        self.qo = Queue.Queue()
        self.port = 2222
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.thread_listen = threading.Thread(target = self._listen)
        self.thread_listen.start()


    def _serve(self):
        """ Mailman function """
        self.s.listen(1)
        client_socket, addr = socket.accept()
        while True:
            if not q_out.empty():
                payload = q_out.get_nowait()
                print "Payload ready ",payload
                client_socket.send(payload)
                print "Payload sent"
            data = client_socket.recv(1024)
            print data
            q_in.put(data)

	def getMessage(self, target):
		""" Get message from URX X = [1, 2] if any. None if none """
        if not self._ur1_qi.empty():
            return self._ur1_qi.get_nowait()
        else:
            return None

    def sendMessage(self, target, message):
        """ Send message to target UR """
		self._ur1_qo.put(message)

