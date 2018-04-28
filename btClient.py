import bluetooth

HC_08 = "34:15:13:1C:AF:0B";
port = 0

print("Connecting...")
sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((HC_08, port))
print("Connection established.")
sock.send("a")

print(sock.recv(1024))

sock.close()
