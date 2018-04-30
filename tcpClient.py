import socket

class TCPClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = "192.168.1.101"
        self.host_port = 8888
        self.s.connect((self.host_ip, self.host_port))
        s.sendall("Hello world through TCP")
        s.close()

client = TCPClient()
