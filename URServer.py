import socket
import time
import sys

# class URServer:
    # """ Server program enabling connection to the two UR robots """

    # def __init__(self):
        


    # def getMessage(self, target):
        # """ Get message from URX X = [1, 2] if any. None if none """

    # def sendMessage(self, target, message):
        # """ Send message to target UR """

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
TCP_IP = "172.16.17.3"
TCP_PORT = 777
server_address = (TCP_IP, TCP_PORT)
print sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)

while True:
    # Wait for a connection
	print (sys.stderr, 'waiting for a connection')
	connection, client_address = sock.accept()
	try:
		print (sys.stderr, 'connection from', client_address)
		# Receive the data in small chunks and retransmit it
		while True:
			data = connection.recv(16)
			print sys.stderr, 'received "%s"' % data
			if data:
				print sys.stderr, 'sending data back to the client'
				connection.sendall(data)
			else:
				print >>sys.stderr, 'no more data from', client_address
				break
	finally:
		# Clean up the connection
		connection.close()