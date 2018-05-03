import socket

class TCPClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = "10.192.252.9"
        self.host_port = 2222
        self.s.connect((self.host_ip, self.host_port))
        print "Connected to", s.gethostbyname()

    def run(self):
        while True:
            print "Waiting for incoming message"
            data = self.s.recv(1024)
            print "Got message: ", data
            self.s.send(data)
            print "Echoed message"

client = TCPClient()
client.run()
