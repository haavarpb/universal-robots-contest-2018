import socket
import time
import sys

class URSocket:

	TCP_IP = "172.16.17.3"

	def __init__(self, port):
		self.TCP_PORT = port
		self.startConnection()
		
	def startConnection(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		server_address = (self.TCP_IP, self.TCP_PORT)
		print sys.stderr, 'starting up on %s port %s' % server_address
		self.sock.bind(server_address)
		self.sock.listen(1)
		print (sys.stderr, 'waiting for a connection')
		self.connection, self.client_address = self.sock.accept()
		
	def receive(self):
		data = self.connection.recv(16)
		print sys.stderr, 'received "%s"' % data
		return data
		
	def send(self, data):
		print sys.stderr, 'sending data back to the client'
		self.connection.sendall(data)
		
	def closeConnection(self):
		print("Closing connection")
		self.connection.close()
		
	def __del__(self):
		print("Deleting object")
		self.closeConnection()