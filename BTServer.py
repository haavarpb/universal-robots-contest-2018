import time
import binascii
import pygatt


class BTServer:
	"""A multiprotocol server class supporting TCP/IP and Bluetooth."""

	# Bluetooth addresses
	AGV_1_LILA = "34:15:13:1C:AF:0B"
	AGV_2_GREEN = "34:15:13:1C:6C:E6"

	# Bluetooth messages and commands
	AGV1_AT_P10 = 0
	AGV1_AT_P11 = 1
	COMMAND_MOVE_AGV1 = bytearray([0x32])
	AGV1_MOVING = 3
	AGV2_AT_P20 = 4
	AGV2_AT_P21 = 5
	COMMAND_MOVE_AGV2 = bytearray([0x36])
	AGV2_MOVING = 7

	# Bluetooth address type
	ADDRESS_TYPE = pygatt.BLEAddressType.public

	def __init__(self):
		# State variables
		self.stateAGV1 = self.AGV1_AT_P10
		self.stateAGV2 = self.AGV2_AT_P20

		# Connection variables
		self.adapter = 0
		self.device = 0
		self.receivedMsg = 0
		self.msgToSend = 0
		self.msgreceived = False

	def getState(self, AGV_id):
		""" Creates a connection with the selected AGV and reads the latest state it published """

		# 1 - Select which one to connect
		if AGV_id == 1:
			AGVaddress = self.AGV_1_LILA
		else:
			AGVaddress = self.AGV_2_GREEN

		# 2 - Create the connection
		self.adapter = pygatt.GATTToolBackend()
		self.adapter.start()
		self.device = self.adapter.connect(AGVaddress, address_type=self.ADDRESS_TYPE)
		print("[BT %d]: Connected." %(AGV_id))

		# 3 - Subscribe to the device to listen for info
		self.msgreceived = False
		subscribed = False
		while not subscribed:
			try:
				print("[BT %d]: Subscribing for info." %(AGV_id))
				self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg)
				print("[BT %d]: Subscribed to." %(AGV_id))
				subscribed = True
			except:
				print("[BT %d]: Unable to subscribe, trying again." %(AGV_id))
				time.sleep(0.2)

		# 4 - Wait until we receive the message
		while not self.msgreceived:
			continue

		# 5 - If we have received a message, close the connection and return
		self.adapter.stop()
		print("[BT %d]: Disconnected." %(AGV_id))
		return self.receivedMsg


	def handle_msg(self, handle, value):
		""" Handle and incoming message: get the last message """

		print("[BT]: Received data: %s" % (value.decode("utf-8")))

		# 1 - Get the data as ASCII and take the last value
		data_str = value.decode("utf-8")
		newest_value = int(data_str[-1])

		self.receivedMsg = newest_value

		# 2 - Set msgreceived to True
		self.msgreceived = True


	def sendMoveMessage(self, AGV_id, waitResponse):
		""" Creates a connection with the selected AGV and reads the latest state it published """

		# 1 - Select which one to connect
		if AGV_id == 1:
			AGVaddress = self.AGV_1_LILA
			msg = self.COMMAND_MOVE_AGV1
			ok = self.AGV1_MOVING
		else:
			AGVaddress = self.AGV_2_GREEN
			msg = self.COMMAND_MOVE_AGV2
			ok = self.AGV2_MOVING

		# 2 - Create the connection
		self.adapter = pygatt.GATTToolBackend()
		self.adapter.start()
		time.sleep(0.2)
		self.device = self.adapter.connect(AGVaddress, address_type=self.ADDRESS_TYPE)
		print("[BT %d]: Connected." %(AGV_id))

		# 3 - Send the message
		sent = False
		while not sent:
			try:
				print("[BT %d]: Sending data." %(AGV_id))
				self.device.char_write("0000ffe1-0000-1000-8000-00805f9b34fb", msg)
				print("[BT %d] Sent data:  %s" % (AGV_id, msg.decode("utf-8")))
				sent = True
			except:
				print("[BT %d]: Unable to send, trying again." %(AGV_id))

		if waitResponse:
			# 4 - Subscribe to the device to listen for info
			self.msgreceived = False
			subscribed = False
			while not subscribed:
				try:
					print("[BT %d]: Subscribing for info." %(AGV_id))
					self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg)
					print("[BT %d]: Subscribed." %(AGV_id))
					subscribed = True
				except:
					print("[BT %d]: Unable to subscribe, trying again." %(AGV_id))

			# 4 - Wait until we receive the message
			while not self.msgreceived:
				continue

			# 5 - Wait until the message is correct
			while self.receivedMsg != ok:
				continue

		# 5 - If we have the correct response, close the connection and return
		self.adapter.stop()
		print("[BT %d]: Disconnected." %(AGV_id))
		return True



# device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE_AGV1)
# print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE_AGV1), COMMAND_MOVE_AGV1.decode("utf-8")))