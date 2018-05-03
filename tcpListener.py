import socket
import time


TCP_IP = ""
TCP_PORT = 2222
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address:', addr
print conn.recv(1024)
time.sleep(0.1)
conn.send("(0)\n")
conn.close()
