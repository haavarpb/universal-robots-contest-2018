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
        self._ur1_port = 2222
        self._ur1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ur1_socket.bind(("", self._ur1_port))
        self._ur1_thread = threading.Thread(target = self._serve, name = "UR1 server", args=(self._ur1_qi, self._ur1_qo, self._ur1_socket))
        self._ur1_thread.start()

        # self._ur2_qi = Queue.Queue()
        # self._ur2_qo = Queue.Queue()
        # self._ur2_port = 8888
        # self._ur2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._ur2_socket.bind(("", self._ur2_port))
        # self._ur2_thread = threading.Thread(target = self._serve, name = "UR2 server", args=(self._ur2_qi, self._ur2_qo, self._ur2_socket))
        # self._ur2_thread.start()

    def _serve(self, q_in, q_out, socket):
        """ Mailman function """
        socket.listen(1)
        client_socket, addr = socket.accept()
        while True:
            while q_out.empty():
                time.sleep(0.5)
            payload = q_out.get_nowait()
            print "Payload ready ",payload
            client_socket.send(payload)
            print "Payload sent"
            data = client_socket.recv(1024)
            q_in.put(data)

	def getMessage(self, target):
		""" Get message from URX X = [1, 2] if any. None if none """
        if target == "UR1":
            if not self._ur1_qi.empty():
                return self._ur1_qi.get_nowait()
        #elif target == "UR2":
            #if not self._ur2_qi.empty()
                # return self._ur2_qi.get_nowait()
        else:
            return None

    def sendMessage(self, target, message):
        """ Send message to target UR """
        if target == "UR1":
			self._ur1_qo.put(message)
        #elif target == "UR2":
            # self._ur2_qo.put(message)
