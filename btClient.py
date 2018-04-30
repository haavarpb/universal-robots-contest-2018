import bluetooth

HC_08 = "34:15:13:1C:AF:0B"
ASUS = "28:E3:47:90:A4:05"

print("Connecting...")
sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((ASUS, 3))
print("Connection established.")
sock.send("Hello")

print(sock.recv(1024))

sock.close()
