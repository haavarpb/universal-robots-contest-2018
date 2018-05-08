import socket
import time
import sys

class URSocket:
	"""A class supporting a socket server."""

	TCP_IP = "172.16.17.3"

	def __init__(self, port, debug=True):
		"""Define the port of the socket and start the connection"""
		self.TCP_PORT = port
		self.debug = debug
		
	def startConnection(self):
		"""Create the socket and wait for a connection request"""
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		server_address = (self.TCP_IP, self.TCP_PORT)
		if self.debug: print("[TCP/IP %d]: starting up on %s port %s" %(self.TCP_PORT, server_address))
		self.sock.bind(server_address)
		self.sock.listen(1)
		if self.debug: print("[TCP/IP %d]: waiting for a connection" %(self.TCP_PORT))
		self.connection, self.client_address = self.sock.accept()
		
	def receive(self):
		"""Receive data"""
		data = self.connection.recv(32)
		if self.debug: print("[TCP/IP %d]: received data: %s" %(self.TCP_PORT, data))
		return data
		
	def send(self, data):
		"""Send data"""
		if self.debug: print("[TCP/IP %d]: sending data: %d" %(data))
		self.connection.sendall(data)
		
	def closeConnection(self):
		"""Close the socket"""
		if self.debug: print("[TCP/IP %d]: Closing connection" %(self.TCP_PORT))
		self.connection.close()
		
	def __del__(self):
		"""Close the socket when deleting the object"""
		if self.debug: print("[TCP/IP %d]: Deleting object" %(self.TCP_PORT))
		self.closeConnection()