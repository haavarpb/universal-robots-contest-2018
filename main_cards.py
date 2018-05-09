from Camera2 import Camera
from BTServer2 import BTServer
from socketTest import URSocket

import threading
import time

class MainControl:
	""" Class to control the Camera, the Bluetooth and the R1 & R2 cycles  """


	def __init__(self, debug=True):

		# Set debug
		self.d = debug
		# Constants
        	self.T_SLEEP = 0.1
        	self.AGV1 = 1
        	self.AGV2 = 2
        	self.IMG_DIST = 0
        	self.IMG_COLOR = 1
		# Initialise objects
		self.CAM = Camera(debug=self.d)
		self.BTS = BTServer(debug=self.d)
		self.UR1 = URSocket(23, debug=self.d)
		self.UR2 = URSocket(24, debug=self.d)
		# Thread variables
		self.parallelBTThread = 0 # to be created if needed
		self.R1Thread = threading.Thread(target=self.R1Cycle, name="R1Thread")
		self.R2Thread = threading.Thread(target=self.R2Cycle, name="R2Thread")
		self.R1Thread.daemon = True
		self.R2Thread.daemon = True
		# Cycle variables
		self.BT1ended = False
		self.BT2ended = False
		self.orderedObjects = []
		self.R2PickEnabled = False
		self.R2ObjectCounter = 0

		# Wait for input and start the cycle
		self.startCycle()


	def startCycle(self):

		# Start the TCP/IP connections with the robots
		self.UR1.startConnection()
		self.UR2.startConnection()
		# Connect to AGV1 via Bluetooth
		self.BTS.updateState(self.AGV1)

		# Wait for start!!!!
		print("[PROGRAM]: Ready to start! Press any key...")
		a = raw_input()

		# Send move message to AGV1
		self.BTS.sendMoveMessage(self.AGV1, True)
		# Start Robot threads
		self.R1Thread.start()
		self.R2Thread.start()
		
		# Do not close until everything ends
		self.R1Thread.join()
		self.R2Thread.join()


	############
	# R1 CYCLE #
	############
	def R1Cycle(self):

		# Repeat four times (0,1,2,3)
		while self.CAM.picturesTaken < 4:

			# 1 - Wait until AGV1 is in P11 -> read from AGV1
			if self.BTS.BTconnected != self.AGV1:
				# If not connected, wait until AGV2 disconnects and connect
				while self.BTS.BTconnected != 0:
					time.sleep(self.T_SLEEP)
				self.BTS.updateState(self.AGV1)
			while self.BTS.stateAGV1 != self.BTS.AGV1_AT_P11:
				time.sleep(self.T_SLEEP)

			# 2 - Take picture and analyze
			
			###################
			# While taking the last picture, to save time,
			# we can run a parallel thread before asking the camera to analyze the picture:
			# the parallel thread disconnects from AGV1 and connects to AGV2.
			# In this way, when we have taken the picture and picked the object,
			# there is no delay before we connect to AGV2
			#
			# Step 2 would be:
			#
			self.UR1.receive() # R1 sends "Ready for picture!"
			if self.CAM.picturesTaken == 3: self.startParallelBTConnect(self.AGV2)
			self.CAM.takePicture(self.IMG_DIST) # here the variable picturesTaken is increased
			###################

			# 3 - If we have taken 4 pictures, send the order of the first 3
			if self.CAM.picturesTaken == 4:
				self.orderedObjects = self.CAM.getOrderedCards()
				ord1 = self.orderedObjects.index(1) + 1
				ord2 = self.orderedObjects.index(2) + 1
				ord3 = self.orderedObjects.index(3) + 1
				# Send message with first 3 commands
				self.UR2.send("(%d,%d,%d)\n" % (ord3, ord1, ord2))

			# 4 - Tell R1 to pick the object
			self.UR1.send("(0)\n") # R1 is waiting for a signal to pick
			self.UR1.receive() # R1 sending "AGV1 cleared!"

			# 5 - If we have not finished, move AGV1 to P10 and disconnect BT
			if self.CAM.picturesTaken < 4:
				self.BTS.sendMoveMessage(self.AGV1, subscribeToState=False)
				self.BTS.disconnect()

			# 6 - Wait until AGV2 is in P20 -> read from AGV1
			if self.BTS.BTconnected != self.AGV2:
				# If not connected, wait until AGV1 disconnects and connect (theoretically already disconnected)
				while self.BTS.BTconnected != 0:
					time.sleep(self.T_SLEEP)
				self.BTS.updateState(self.AGV2)
			while self.BTS.stateAGV2 != self.BTS.AGV2_AT_P20:
				time.sleep(self.T_SLEEP)

			# 7 - Tell R1 to place the object
			self.UR1.send("(0)\n") # R1 is waiting for a signal to place
			self.UR1.receive() # Receive message "AGV2 loaded"

			# 8 - Move AGV2 to P21 without disconnecting and enable R2 pick
			self.BTS.sendMoveMessage(self.AGV2, subscribeToState=True)
			self.R2PickEnabled = True


	############
	# R2 CYCLE #
	############
	def R2Cycle(self):

		# Repeat four times (1,2,3,4)
		while self.CAM.picturesTaken <= 4:

			#1 - Wait until R1 enables us to pick
			while not self.R2PickEnabled:
				time.sleep(self.T_SLEEP)

			# 2 - Wait until AGV2 is in P21 -> read from AGV2
			if self.BTS.BTconnected != self.AGV2:
				# If not connected, wait until AGV1 disconnects and connect (theoretically already connected)
				while self.BTS.BTconnected != 0:
					time.sleep(self.T_SLEEP)
				self.BTS.updateState(self.AGV2)
			while self.BTS.stateAGV2 != self.BTS.AGV2_AT_P21:
				time.sleep(self.T_SLEEP)

			# 3 - Tell R2 to pick the object
			self.UR2.receive() # R2 sends: Ready
			if self.CAM.picturesTaken < 4:
				# If it is not the last object, just send a message to pick
				self.UR2.send("(0)\n")
			else:
				# If it is the last object, send directly its output number
				ord4 = self.orderedObjects.index(4) + 1
				self.UR2.send("(%d)\n" %(ord4))
			self.UR2.receive() # R2 sends: AGV2 cleared

			# 4 -  If we have not finished: move AGV2 to P20, disconnect BT and disable R2Pick until R1 enables it again
			if self.CAM.picturesTaken < 4:
				self.BTS.sendMoveMessage(self.AGV2, subscribeToState=False)
				self.BTS.disconnect()
				self.R2PickEnabled = False


	################################
	# PARALLEL BT CONNECT FUNCTION #
	################################
	def parallelBTConnect(self, AGV_id):
		""" Function to be ran in parallel with the rest of the program """
		self.BTS.disconnect()
		self.BTS.updateState(AGV_id)

	def startParallelBTConnect(self, AGV_id):
		""" Create a parallel BT Thread for connecting to an AGV while the rest of the program is running """
		self.parallelBTThread = threading.Thread(target=self.parallelBTConnect, name="BTThread", args=[AGV_id])
		self.parallelBTThread.daemon = True
		self.parallelBTThread.start()


MC = MainControl()

# #############
# # CONSTANTS #
# #############
# R1_AT_PICTURE_POS = 0
# R1_AT_PLACE_POS = 1
# R1_MOVING = 2
# R2_AT_PICK_POS = 3
# R2_MOVING = 4

# PIC_DISTANCE = 0
# PIC_COLOR = 1

# ###########
# # OBJECTS #
# ###########

# CAM = Camera()
# BTS = BTServer()
# UR1 = URSocket(23)
# UR2 = URSocket(24)


# #############
# # VARIABLES #
# #############

# AGV1_state = BTS.AGV1_MOVING
# AGV2_state = BTS.AGV2_MOVING
# R1_state = R1_AT_PICTURE_POS
# R2_state = R2_AT_PICK_POS

# R1_picture_ok = False
# R1_pick_ok = False
# R1_place_ok = False
# R2_ready_to_pick = False
# R2_placed_ordered = False

# R1_picture_counter = 0
# R2_picked_counter = 0

# agv1ThreadOn = False
# agv2ThreadOn = False

# colorOrder = 0

# #############
# # FUNCTIONS #
# #############

# # Functions to be threaded
# def takePicture():
# 	""" Take a picture, update the R1_picture_ok and R1_picture_counter variables and tell R1 to move to Pick Pos """
# 	global R1_picture_counter, R1_picture_ok, UR1, colorOrder
# 	# Receive message: UR1 ready
# 	msg = UR1.receive()
# 	print("[PROGRAM]: message received from R1: " + msg)
# 	# Slect which picture to take
# 	picType = PIC_COLOR
# 	print("[PROGRAM]: Taking picture.")
# 	CAM.takePicture(picType)
# 	R1_picture_counter += 1
# 	R1_picture_ok = True
# 	# Final actions
# 	if R1_picture_counter < 4:
# 		R1PickObject()
# 	elif R1_picture_counter == 4:
# 		colorOrder = CAM.getOrderedColors()
# 		ord1 = colorOrder.index(1) + 1
# 		ord2 = colorOrder.index(2) + 1
# 		ord3 = colorOrder.index(3) + 1
# 		# Send message with first 3 commands
# 		print("[PROGRAM]: Sending ordered colors.")
# 		UR2.send("(%d,%d,%d)\n" % (ord3, ord1, ord2))
# 		# Tell R1 to pick the object from AGV1
# 		R1PickObject(False)

# def agv1UpdateState():
# 	""" Do a BT request to update the state of AGV1 """
# 	global agv1ThreadOn, agv2ThreadOn, BTS
# 	print("[BT 1]: Trying to update AGV1 state.")
# 	t = 0
# 	while agv2ThreadOn or agv1ThreadOn:
# 		if t == 0:
# 			print("[BT 1]: Waiting for BT to stop.")
# 			t = 1
# 		else:
# 			time.sleep(0.1)
# 	print("[BT 1]: Updating AGV1 state")
# 	agv1ThreadOn = True
# 	BTS.updateState(1)
# 	agv1ThreadOn = False

# def agv1SendMoveCommand(subscribeToState=False):
# 	""" Send a BT message to move AGV1 """
# 	global agv1ThreadOn, agv2ThreadOn, BTS
# 	print("[BT 1]: Trying to send move message.")
# 	t = 0
# 	while agv2ThreadOn or agv1ThreadOn:
# 		if t == 0:
# 			print("[BT 1]: Waiting for BT to stop.")
# 			t = 1
# 		else:
# 			time.sleep(0.1)
# 	print("[BT 2]: Sending move message.")
# 	agv1ThreadOn = True
# 	BTS.sendMoveMessage(1, subscribeToState)
# 	agv1ThreadOn = False


# def agv2UpdateState():
# 	""" Do a BT request to update the state of AGV2 """
# 	global agv1ThreadOn, agv2ThreadOn, BTS
# 	print("[BT 2]: Trying to update AGV2 state.")
# 	t = 0
# 	while agv1ThreadOn or agv2ThreadOn:
# 		if t == 0:
# 			print("[BT 2]: Waiting for BT to stop.")
# 			t = 1
# 		else:
# 			time.sleep(0.1)
# 	print("[BT 2]: Updating AGV2 state")
# 	agv2ThreadOn = True
# 	BTS.updateState(2)
# 	agv2ThreadOn = False


# def agv2SendMoveCommand(subscribeToState=False):
# 	""" Send a BT message to move AGV2 """
# 	global agv1ThreadOn, agv2ThreadOn, BTS
# 	print("[BT 2]: Trying to send move message.")
# 	t = 0
# 	while agv1ThreadOn or agv2ThreadOn:
# 		if t == 0:
# 			print("[BT 2]: Waiting for BT to stop.")
# 			t = 1
# 		else:
# 			time.sleep(0.1)
# 	print("[BT 2]: Sending move message.")
# 	agv2ThreadOn = True
# 	BTS.sendMoveMessage(2, subscribeToState)
# 	agv2ThreadOn = False


# def R1PickObject(moveAGV1=True):
# 	""" Send pick order to R1 and wait for response, then tell AGV1 to move """
# 	global R1_state, R1_pick_ok, UR1
# 	# Send message to pick
# 	print("[PROGRAM]: Sending pick message to R1.")
# 	UR1.send("(0)\n")
# 	R1_state = R1_MOVING
# 	# Receive message AGV1 cleared
# 	msg = UR1.receive()
# 	print("[PROGRAM]: message received from R1: " + msg)
# 	# interpret message...
# 	R1_state = R1_AT_PLACE_POS
# 	# Tell AGV1 to move
# 	if moveAGV1:
# 		print("[PROGRAM]: Sending Move Command to AGV1.")
# 		agv1SendMoveCommand()
# 	# Action ended
# 	R1_pick_ok = True


# def R1PlaceObject():
# 	""" Send place order to R1 and wait for response, then tell AGV2 to move """
# 	global R1_state, R1_place_ok, UR1
# 	# Send message to place object
# 	print("[PROGRAM]: Sending place message to R1.")
# 	UR1.send("(0)\n")
# 	R1_state = R1_MOVING
# 	# Receive message "AGV2 loaded"
# 	msg = UR1.receive()
# 	print("[PROGRAM]: message received from R1: " + msg)
# 	# interpret message...
# 	R1_state = R1_AT_PICTURE_POS
# 	# Tell AGV2 to move
# 	print("[PROGRAM]: Sending Move Command to AGV2.")
# 	agv2SendMoveCommand()
# 	# Action ended
# 	R1_place_ok = True


# def R2PickObject():
# 	""" Send pick order to R2 and wait for response, then tell AGV2 to move """
# 	global R2_state, R2_picked_counter, UR2, colorOrder
# 	# Receive message: UR2 ready
# 	msg = UR2.receive()
# 	print("[PROGRAM]: message received from R2: " + msg)
# 	# Send message to pick object
# 	if R1_picture_counter < 4:
# 		UR2.send("(0)\n")
# 	elif R1_picture_counter == 4:
# 		ord4 = colorOrder.index(4) + 1
# 		UR2.send("(%d)\n" %(ord4))
# 	R2_state = R2_MOVING
# 	# Receive message: AGV2 cleared
# 	msg = UR2.receive()
# 	print("[PROGRAM]: message received from R2: " + msg)
# 	# interpret message...
# 	R2_state = R2_AT_PICK_POS
# 	R2_picked_counter += 1
# 	# Tell AGV2 to move if we have not ended
# 	if R2_picked_counter < 4:
# 		print("[PROGRAM]: Sending Move Command to AGV2.")
# 		agv2SendMoveCommand()


# ###########
# # THREADS #
# ###########
# pict_thread = 0 # thread will be created when needed
# r1_thread = 0 # thread will be created when needed
# r2_thread = 0 # thread will be created when needed
# agv1_bt_thread = 0 # thread will be created when needed
# agv2_bt_thread = 0 # thread will be created when needed

# ####################
# # SARTING SEQUENCE #
# ####################
# UR1.startConnection()
# UR2.startConnection()

# # Connect to AGV1
# BTS.updateState(1)

# # Wait for start!!!!
# print("[PROGRAM]: Ready to start! Press any key...")
# a = raw_input()

# BTS.sendMoveMessage(1, True)

# #############
# # MAIN LOOP #
# #############

# while True:
# 	###############
# 	# R1 workflow #
# 	###############
# 	# 1 - If picture is not taken, take picture
# 	if not R1_picture_ok:
# 		# If everything is in position, take picture
# 		if (R1_state == R1_AT_PICTURE_POS) and (BTS.stateAGV1 == BTS.AGV1_AT_P11):
# 			if pict_thread == 0:
# 				pict_thread = threading.Thread(target=takePicture, name="pictThread")
# 				pict_thread.daemon = True
# 				pict_thread.start()
# 			elif not pict_thread.is_alive():
# 				pict_thread = threading.Thread(target=takePicture, name="pictThread")
# 				pict_thread.daemon = True
# 				pict_thread.start()
# 		# If the problem is AGV, update the position info
# 		elif BTS.stateAGV1 != BTS.AGV1_AT_P11:
# 			if not agv1ThreadOn and not agv2ThreadOn:
# 				print("[PROGRAM]: AGV1 not in position: %d" %(BTS.stateAGV1))
# 				agv1_bt_thread = threading.Thread(target=agv1UpdateState, name="agv1Thread")
# 				agv1_bt_thread.daemon = True
# 				agv1_bt_thread.start();
# 		else:
# 			print("[PROGRAM]: R1 not in position.")
# 	# 2 - If picture has been taken and object has been picked
# 	#     If object has not been placed, place object
# 	elif R1_pick_ok and not R1_place_ok:
# 		# If everything is in position, place object
# 		if (R1_state == R1_AT_PLACE_POS) and (BTS.stateAGV2 == BTS.AGV2_AT_P20):
# 			if r1_thread == 0:
# 				r1_thread = threading.Thread(target=R1PlaceObject, name="r1Thread")
# 				r1_thread.daemon = True
# 				r1_thread.start()
# 			elif not r1_thread.is_alive():
# 				r1_thread = threading.Thread(target=R1PlaceObject, name="r1Thread")
# 				r1_thread.daemon = True
# 				r1_thread.start()
# 		# If the problem is AGV, update the position info
# 		elif BTS.stateAGV2 != BTS.AGV2_AT_P20:
# 			if not agv1ThreadOn and not agv2ThreadOn:
# 				print("[PROGRAM]: AGV2 not in position: %d" %(BTS.stateAGV2))
# 				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
# 				agv2_bt_thread.daemon = True
# 				agv2_bt_thread.start();
# 	# 3 - If object has been placed, reset cycle
# 	elif R1_place_ok:
# 		print("[PROGRAM]: Resetting R1 cycle. Enabling R2 pick.")
# 		R1_picture_ok = False
# 		R1_pick_ok = False
# 		R1_place_ok = False
# 		R2_ready_to_pick = True

# 	###############
# 	# R2 workflow #
# 	###############
# 	# 3 - Pick an object if R1 has placed it
# 	if R2_ready_to_pick:
# 		# If everything is in position, pick object
# 		if (R2_state == R2_AT_PICK_POS) and (BTS.stateAGV2 == BTS.AGV2_AT_P21):
# 			if r2_thread == 0:
# 				r2_thread = threading.Thread(target=R2PickObject, name="r2Thread")
# 				r2_thread.daemon = True
# 				r2_thread.start()
# 				R2_ready_to_pick = False
# 			elif not r2_thread.is_alive():
# 				r2_thread = threading.Thread(target=R2PickObject, name="r2Thread")
# 				r2_thread.daemon = True
# 				r2_thread.start()
# 				R2_ready_to_pick = False

# 		# If the problem is the AGV, update the position info
# 		elif BTS.stateAGV2 != BTS.AGV2_AT_P21:
# 			print("[PROGRAM]: AGV2 not in position: %d" %(BTS.stateAGV2))
# 			if not agv1ThreadOn and not agv2ThreadOn:
# 				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
# 				agv2_bt_thread.daemon = True
# 				agv2_bt_thread.start();

# 	###########################
# 	# SLEEP BEFORE NEXT LOOP? #
# 	###########################
# 	time.sleep(0.1)
