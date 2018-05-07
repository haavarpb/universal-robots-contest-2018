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
		self.stateAGV1 = -1
		self.stateAGV2 = -1

		# Connection variables
		self.adapter = 0
		self.device = 0
		self.msgToSend = 0
		self.msgreceived = False

		# BT connection state variables
		self.BTconnected = 0
		self.BTsubscribed = 0

	def updateState(self, AGV_id):
		""" Creates a connection with the selected AGV and reads the latest state it published """

		# 1 - Select which one to connect
		if AGV_id == 1:
			AGVaddress = self.AGV_1_LILA
		elif AGV_id == 2:
			AGVaddress = self.AGV_2_GREEN
		else:
			error('Unknown AGV_id: must be 1 or 2')

		# 2 - If we are not connected: connect
		if self.BTconnected != AGV_id:
			# 2.1 - If there is another connection, close it
			if self.BTconnected != 0:
				self.adapter.stop()
				print("[BT %d]: Disconnected." %(self.BTconnected))
			# 2.2 - Create the connection
			self.adapter = pygatt.GATTToolBackend()
			self.adapter.start()
			while self.BTconnected != AGV_id:
				try:
					print("[BT %d]: Connecting." % (AGV_id))
					self.device = self.adapter.connect(AGVaddress, address_type=self.ADDRESS_TYPE)
					print("[BT %d]: Connected." %(AGV_id))
					self.BTconnected = AGV_id
					self.BTsubscribed = 0
				except:
					print("[BT %d]: Unable to connect, trying again." % (AGV_id))
					time.sleep(0.2)

		# 3 - If we are not subscribed: subscribe
		if self.BTsubscribed != AGV_id:
			# 3.1 - Subscribe to the device to listen for info
			while self.BTsubscribed != AGV_id:
				try:
					print("[BT %d]: Subscribing for info." %(AGV_id))
					if AGV_id == 1:
						self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg_1)
					else:
						self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg_2)
					print("[BT %d]: Subscribed to." %(AGV_id))
					self.BTsubscribed = AGV_id
					self.msgreceived = False
				except:
					print("[BT %d]: Unable to subscribe, trying again." %(AGV_id))
					time.sleep(0.2)

		# 4 - Wait until we receive at least one message
		while not self.msgreceived:
			time.sleep(0.1)
			continue


	def handle_msg_1(self, handle, value):
		""" Handle and incoming message for AGV1: get the last message """

		print("[BT 1]: Received data: %s" % (value.decode("utf-8")))

		# 1 - Get the data as ASCII and take the last value
		data_str = value.decode("utf-8")
		newest_value = int(data_str[-1])

		self.stateAGV1 = newest_value

		self.msgreceived = True


	def handle_msg_2(self, handle, value):
		""" Handle and incoming message for AGV1: get the last message """

		print("[BT 2]: Received data: %s" % (value.decode("utf-8")))

		# 1 - Get the data as ASCII and take the last value
		data_str = value.decode("utf-8")
		newest_value = int(data_str[-1])

		self.stateAGV2 = newest_value

		self.msgreceived = True


	def sendMoveMessage(self, AGV_id, subscribeToState):
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

		# 2 - If we are not connected: connect
		if self.BTconnected != AGV_id:
			# 2.1 - If there is another connection, close it
			if self.BTconnected != 0:
				self.adapter.stop()
				print("[BT %d]: Disconnected." %(self.BTconnected))
			# 2.2 - Create the connection
			self.adapter = pygatt.GATTToolBackend()
			self.adapter.start()
			while self.BTconnected != AGV_id:
				try:
					print("[BT %d]: Connecting." % (AGV_id))
					self.device = self.adapter.connect(AGVaddress, address_type=self.ADDRESS_TYPE)
					print("[BT %d]: Connected." %(AGV_id))
					self.BTconnected = AGV_id
					self.BTsubscribed = 0
				except:
					print("[BT %d]: Unable to connect, trying again." % (AGV_id))
					time.sleep(0.2)

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

		if subscribeToState:
			# 4 - If we are not subscribed: subscribe
			if self.BTsubscribed != AGV_id:
				# 4.1 - Subscribe to the device to listen for info
				while self.BTsubscribed != AGV_id:
					try:
						print("[BT %d]: Subscribing for info." %(AGV_id))
						if AGV_id == 1:
							self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg_1)
						else:
							self.device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb", callback=self.handle_msg_2)
						print("[BT %d]: Subscribed to." %(AGV_id))
						self.BTsubscribed = AGV_id
						self.msgreceived = False
					except:
						print("[BT %d]: Unable to subscribe, trying again." %(AGV_id))
						time.sleep(0.2)

		return True



# device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE_AGV1)
# print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE_AGV1), COMMAND_MOVE_AGV1.decode("utf-8")))
