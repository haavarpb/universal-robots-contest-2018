from Camera import Camera
from BTServer import BTServer
from socketTest import URSocket

import threading
import time

#########
R1_AT_PICTURE_POS = 0
R1_AT_PLACE_POS = 1
R1_MOVING = 2
R2_AT_PICK_POS = 3
R2_MOVING = 4
#########

# Main objects
CAM = Camera()
BTS = BTServer()
UR1 = URSocket(23)
UR2 = URSocket(24)

# Main variables
AGV1_state = BTS.AGV1_MOVING
AGV2_state = BTS.AGV2_MOVING
R1_state = R1_AT_PICTURE_POS
R2_state = R2_AT_PICK_POS
PIC_DISTANCE = 0
PIC_COLOR = 1

R1_picture_ok = False
R1_place_ok = False
R2_ready_to_pick = False

R1_picture_counter = 0
R2_picked_counter = 0

agv1ThreadOn = False
agv2ThreadOn = False

# Functions to be threaded
def takePicture():
	""" Take a picture, update the R1_picture_ok and R1_picture_counter variables and tell R1 to move to Pick Pos """
	global R1_picture_counter, R1_picture_ok, UR1
	# Receive message: UR1 ready
	msg = UR1.receive()
	print("[PROGRAM]: message received from R1: " + msg)
	# Slect which picture to take
	if R1_picture_counter < 4:
		picType = PIC_DISTANCE
	else:
		picType = PIC_COLOR
	print("[PROGRAM]: Taking picture.")
	CAM.takePicture(picType)
	R1_picture_counter += 1
	R1_picture_ok = True
	R1PickObject()

def agv1UpdateState():
	""" Do a BT request to update the state of AGV1 """
	global AGV1_state, agv1ThreadOn, agv2ThreadOn
	print("[BT 1]: Trying to update AGV1 state.")
	t = 0
	while agv2ThreadOn or agv1ThreadOn:
		if t == 0:
			print("[BT 1]: Waiting for BT to stop.")
			t = 1
		else:
			time.sleep(0.1)
	print("[BT 1]: Updating AGV1 state")
	agv1ThreadOn = True
	AGV1_state = BTS.getState(1)
	agv1ThreadOn = False

def agv1SendMoveCommand():
	""" Send a BT message to move AGV1 """
	global agv1ThreadOn, agv2ThreadOn, AGV1_state
	print("[BT 1]: Trying to send move message.")
	t = 0
	while agv2ThreadOn or agv1ThreadOn:
		if t == 0:
			print("[BT 1]: Waiting for BT to stop.")
			t = 1
		else:
			time.sleep(0.1)
	print("[BT 2]: Sending move message.")
	agv1ThreadOn = True
	BTS.sendMoveMessage(1, False)
	AGV1_state = BTS.AGV1_MOVING
	agv1ThreadOn = False


def agv2UpdateState():
	""" Do a BT request to update the state of AGV2 """
	global AGV2_state, agv1ThreadOn, agv2ThreadOn
	print("[BT 2]: Trying to update AGV2 state.")
	t = 0
	while agv1ThreadOn or agv2ThreadOn:
		if t == 0:
			print("[BT 2]: Waiting for BT to stop.")
			t = 1
		else:
			time.sleep(0.1)
	print("[BT 2]: Updating AGV2 state")
	agv2ThreadOn = True
	AGV2_state = BTS.getState(2)
	agv2ThreadOn = False


def agv2SendMoveCommand():
	""" Send a BT message to move AGV2 """
	global agv1ThreadOn, agv2ThreadOn, AGV2_state
	print("[BT 2]: Trying to send move message.")
	t = 0
	while agv1ThreadOn or agv2ThreadOn:
		if t == 0:
			print("[BT 2]: Waiting for BT to stop.")
			t = 1
		else:
			time.sleep(0.1)
	print("[BT 2]: Sending move message.")
	agv2ThreadOn = True
	BTS.sendMoveMessage(2, False)
	AGV2_state = BTS.AGV2_MOVING
	agv2ThreadOn = False


def R1PickObject():
	""" Send pick order to R1 and wait for response, then tell AGV1 to move """
	global R1_state, R1_pick_ok, UR1
	# Send message to pick
	print("[PROGRAM]: Sending pick message to R1.")
	UR1.send("(0)\n")
	R1_state = R1_MOVING
	# Receive message AGV1 cleared
	msg = UR1.receive()
	print("[PROGRAM]: message received from R1: " + msg)
	# interpret message...
	R1_state = R1_AT_PLACE_POS
	R1_pick_ok = True
	# Tell AGV1 to move
	print("[PROGRAM]: Sending Move Command to AGV1.")
	agv1SendMoveCommand()


def R1PlaceObject():
	""" Send place order to R1 and wait for response, then tell AGV2 to move """
	global R1_state, R1_place_ok, UR1
	# Send message to place object
	print("[PROGRAM]: Sending place message to R1.")
	UR1.send("(0)\n")
	R1_state = R1_MOVING
	# Receive message "AGV2 loaded"
	msg = UR1.receive()
	print("[PROGRAM]: message received from R1: " + msg)
	# interpret message...
	R1_state = R1_AT_PICTURE_POS
	R1_place_ok = True
	# Tell AGV2 to move
	print("[PROGRAM]: Sending Move Command to AGV2.")
	agv2SendMoveCommand()


def R2PickObject():
	""" Send pick order to R2 and wait for response, then tell AGV2 to move """
	global R2_state, R2_picked_counter, UR2
	# Receive message: UR2 ready
	msg = UR2.receive()
	print("[PROGRAM]: message received from R2: " + msg)
	# Send message to pick object
	UR2.send("(0)\n")
	R2_state = R2_MOVING
	# Receive message: AGV2 cleared
	msg = UR2.receive()
	print("[PROGRAM]: message received from R2: " + msg)
	# interpret message...
	R2_state = R2_AT_PICK_POS
	R2_picked_counter += 1
	# Tell AGV2 to move
	agv2SendMoveCommand()

def R2PlaceObjects(orderedObjects):
	""" Send place order to R2 and wait for response, then tell AGV2 to move """
	global R2_state
	ord1 = orderedObjects.index(0) + 1;
	ord2 = orderedObjects.index(1) + 1;
	ord3 = orderedObjects.index(2) + 1;
	ord4 = orderedObjects.index(3) + 1;
	R2_state = R2_MOVING
	# Send message with first command
	UR2.send("(%d)\n" % (ord4))
	# Receive message: first output done
	UR2.receive()
	# Receive message: buffer1 cleared
	UR2.receive()
	# Send message with second command
	UR2.send("(%d)\n" % (ord1))
	# Receive message: second output done
	UR2.receive()
	# Receive message: buffer2 cleared
	UR2.receive()
	# Send message with third command
	UR2.send("(%d)\n" % (ord2))
	# Receive message: third output done
	UR2.receive()
	# Receive message: buffer3 cleared
	UR2.receive()
	# Send message with fourth command
	UR2.send("(%d)\n" % (ord3))
	# Receive message: fourth output done
	UR2.receive()
	# interpret message...
	R2_state = R2_AT_PICK_POS


# Threads
pict_thread = 0 # thread will be created when needed
r1_thread = 0 # thread will be created when needed
r2_thread = 0 # thread will be created when needed
agv1_bt_thread = 0 # thread will be created when needed
agv2_bt_thread = 0 # thread will be created when needed

while True:
	###############
	# R1 workflow #
	###############
	# 1 - If picture is not taken, take picture
	if not R1_picture_ok:
		# If everything is in position, take picture
		if (R1_state == R1_AT_PICTURE_POS) and (AGV1_state == BTS.AGV1_AT_P11):
			if pict_thread == 0:
				pict_thread = threading.Thread(target=takePicture, name="pictThread")
				pict_thread.daemon = True
				pict_thread.start()
			elif not pict_thread.is_alive():
				pict_thread = threading.Thread(target=takePicture, name="pictThread")
				pict_thread.daemon = True
				pict_thread.start()
		# If the problem is AGV, update the position info
		elif AGV1_state != BTS.AGV1_AT_P11:
			#############agv1UpdateState()
			if not agv1ThreadOn and not agv2ThreadOn:
				print("[PROGRAM]: AGV1 not in position: %d" %(AGV1_state))
				agv1_bt_thread = threading.Thread(target=agv1UpdateState, name="agv1Thread")
				agv1_bt_thread.daemon = True
				agv1_bt_thread.start();
		else:
			print("[PROGRAM]: R1 not in position.")
	# 2 - If picture has been taken and object has been picked
	#     If object has not been placed, place object
	elif not R1_place_ok:
		# If everything is in position, place object
		if (R1_state == R1_AT_PLACE_POS) and (AGV2_state == BTS.AGV2_AT_P20):
			if r1_thread == 0:
				r1_thread = threading.Thread(target=R1PlaceObject, name="r1Thread")
				r1_thread.daemon = True
				r1_thread.start()
			elif not r1_thread.is_alive():
				r1_thread = threading.Thread(target=R1PlaceObject, name="r1Thread")
				r1_thread.daemon = True
				r1_thread.start()
		# If the problem is AGV, update the position info
		elif AGV2_state != BTS.AGV2_AT_P20:
			################agv2UpdateState()
			if not agv1ThreadOn and not agv2ThreadOn:
				print("[PROGRAM]: AGV2 not in position: %d" %(AGV2_state))
				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
				agv2_bt_thread.daemon = True
				agv2_bt_thread.start();
	# 3 - If object has been placed, reset cycle
	else:
		print("[PROGRAM]: Resetting R1 cycle. Enabling R2 pick.")
		R1_picture_ok = False
		R1_place_ok = False
		R2_ready_to_pick = True

	###############
	# R2 workflow #
	###############
	# 1 - If we have picked 4, send distance place commands
	if R2_picked_counter == 4:
		print("[PROGRAM]: Trying to order R2 cards.")
		if not r2_thread.is_alive():
			r2_thread = threading.Thread(target=R2PlaceObjects, name="r2Thread", args=([CAM.getOrderedCards()]))
			r2_thread.daemon = True
			r2_thread.start()
	# 2 - If we have picked 8, send color place commands
	elif R2_picked_counter == 8:
		print("[PROGRAM]: Trying to order R2 colors.")
		if not r2_thread.is_alive():
			r2_thread = threading.Thread(target=R2PlaceObjects, name="r2Thread", args=([CAM.getOrderedColors()]))
			r2_thread.daemon = True
			r2_thread.start()
	# 3 - Else, pick another object if R1 has placed it
	elif R2_ready_to_pick:
		# If everything is in position, pick object
		if (R2_state == R2_AT_PICK_POS) and (AGV2_state == BTS.AGV2_AT_P21):
			if r2_thread == 0:
				r2_thread = threading.Thread(target=R2PickObject, name="r2Thread")
				r2_thread.daemon = True
				r2_thread.start()
				R2_ready_to_pick = False
			elif not r2_thread.is_alive():
				r2_thread = threading.Thread(target=R2PickObject, name="r2Thread")
				r2_thread.daemon = True
				r2_thread.start()
				R2_ready_to_pick = False
					
		# If the problem is AGV, update the position info
		elif AGV2_state != BTS.AGV2_AT_P21:
			print("[PROGRAM]: AGV2 not in position: %d" %(AGV2_state))
			################3agv2UpdateState()
			if not agv1ThreadOn and not agv2ThreadOn:
				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
				agv2_bt_thread.daemon = True
				agv2_bt_thread.start();

	time.sleep(0.2)
