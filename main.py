from Camera import Camera
from BTServer import BTServer
from URServer import URServer

import threading

#########
R1_AT_PICTURE_POS = 0
R1_AT_PICK_POS = 1
R1_AT_PLACE_POS = 2
R1_MOVING = 3
R2_AT_PICK_POS = 4
R2_MOVING = 5
#########

# Main objects
CAM = Camera()
BTS = BTServer()
URS = URServer()

# Main variables
AGV1_state = BTS.AGV1_MOVING
AGV2_state = BTS.AGV2_MOVING
R1_state = R1_AT_PICTURE_POS
R2_state = R2_AT_PICK_POS
PIC_DISTANCE = 0
PIC_COLOR = 1

R1_picture_ok = False
R1_pick_ok = False
R1_place_ok = False

R1_picture_counter = 0
R2_picked_counter = 0

# Functions to be threaded
def takePicture():
	""" Take a picture, update the R1_picture_ok and R1_picture_counter variables and tell R1 to move to Pick Pos """
	if R1_picture_counter < 4:
		picType = PIC_DISTANCE
	else:
		picType = PIC_COLOR
	CAM.takePicture(picType)
	R1_picture_counter += 1
	R1_picture_ok = True

def agv1UpdateState():
	""" Do a BT request to update the state of AGV1 """
	if agv2_bt_thread.is_alive():
		agv2_bt_thread.join() # wait for the bt of agv2 to end
	AGV1_state = BTS.getState(1)

def agv1SendMoveCommand():
	""" Send a BT message to move AGV1 """
	if agv2_bt_thread.is_alive():
		agv2_bt_thread.join() # wait for the bt of agv2 to end
	BTS.sendMoveMessage(1)

def agv2UpdateState():
	""" Do a BT request to update the state of AGV2 """
	if agv1_bt_thread.is_alive():
		agv1_bt_thread.join() # wait for the bt of agv1 to end
	AGV2_state = BTS.getState(2)

def agv2SendMoveCommand():
	""" Send a BT message to move AGV2 """
	if agv1_bt_thread.is_alive():
		agv1_bt_thread.join() # wait for the bt of agv1 to end
	BTS.sendMoveMessage(2)

def R1MoveToPick():
	""" Send move order to R1 and wait for response """
	# URS.sendMessage("UR1","(0)")
	R1_state = R1_MOVING
	# URS.getMessage("UR1")
	# interpret message...
	R1_state = R1_AT_PICK_POS

def R1PickObject():
	""" Send pick order to R1 and wait for response, then tell AGV1 to move """
	# URS.sendMessage("UR1","(0)")
	R1_state = R1_MOVING
	# URS.getMessage("UR1")
	# interpret message...
	R1_state = R1_AT_PLACE_POS
	R1_pick_ok = True
	# Tell AGV1 to move
	agv1_bt_thread = threading.Thread(target=agv1SendMoveCommand, name="agv1Thread")
	agv1_bt_thread.daemon = True
	agv1_bt_thread.start();

def R1PlaceObject():
	""" Send place order to R1 and wait for response, then tell AGV2 to move """
	# URS.sendMessage("UR1","(0)")
	R1_state = R1_MOVING
	# URS.getMessage("UR1")
	# interpret message...
	R1_state = R1_AT_PICTURE_POS
	R1_place_ok = True
	# Tell AGV2 to move
	agv2_bt_thread = threading.Thread(target=agv2SendMoveCommand, name="agv2Thread")
	agv2_bt_thread.daemon = True
	agv2_bt_thread.start();

def R2PickObject():
	""" Send pick order to R2 and wait for response, then tell AGV2 to move """
	# URS.sendMessage("UR2","(0)")
	R2_state = R2_MOVING
	# URS.getMessage("UR2")
	# interpret message...
	R2_state = R2_AT_PICK_POS
	R2_picked_counter += 1
	# Tell AGV2 to move
	if agv2_bt_thread.is_alive():
		agv2_bt_thread.join() # wait for the bt of agv2 to end
	agv2_bt_thread = threading.Thread(target=agv2SendMoveCommand, name="agv2Thread")
	agv2_bt_thread.daemon = True
	agv2_bt_thread.start();

def R2PlaceObjects(orderedObjects):
	""" Send place order to R2 and wait for response, then tell AGV2 to move """
	ord1 = orderedObjects.index(0) + 1;
	ord2 = orderedObjects.index(1) + 1;
	ord3 = orderedObjects.index(2) + 1;
	ord4 = orderedObjects.index(3) + 1;
	# URS.sendMessage("UR2","(%d,%d,%d,%d)" % (ord4, ord1, ord2, ord3))
	R2_state = R2_MOVING
	# URS.getMessage("UR2")
	# interpret message...
	R2_state = R2_AT_PICK_POS


# Threads
pict_thread = 0 # thread will be created when needed
r1_thread = 0 # thread will be created when needed
agv1_bt_thread = threading.Thread(target=agv1UpdateState, name="agv1Thread")
agv1_bt_thread.daemon = True
agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
agv1_bt_thread.daemon = True
agv1_bt_thread.start();
agv2_bt_thread.start();

while True:
	###############
	# R1 workflow #
	###############
	# 1 - If picture is not taken, take picture
	if not R1_picture_ok:
		# If everything is in position, take picture
		if (R1_state == R1_AT_PICTURE_POS) and (AGV1_state == BTS.AGV1_AT_P10):
			if not pict_thread.is_alive():
				pict_thread = threading.Thread(target=takePicture, name="pictThread")
				pict_thread.daemon = True
				pict_thread.start()
		# If the problem is AGV, update the position info
		elif AGV1_state != BTS.AGV1_AT_P10:
			if not agv1_bt_thread.is_alive():
				agv1_bt_thread = threading.Thread(target=agv1UpdateState, name="agv1Thread")
				agv1_bt_thread.daemon = True
				agv1_bt_thread.start();
	# 2 - If picture has been taken
	#     If object has not been picked, pick object
	elif not R1_pick_ok:
		# If everything is in position, pick object
		if (R1_state == R1_AT_PICK_POS) and (AGV1_state == BTS.AGV1_AT_P10):
			if not r1_thread.is_alive():
				r1_thread = threading.Thread(target=R1PickObject, name="r1Thread")
				r1_thread.daemon = True
				r1_thread.start()
	# 3 - If object has been picked
	#     If object has not been placed, place object
	elif not R1_place_ok:
		# If everything is in position, place object
		if (R1_state == R1_AT_PLACE_POS) and (AGV2_state == BTS.AGV2_AT_P20):
			if not r1_thread.is_alive():
				r1_thread = threading.Thread(target=R1PlaceObject, name="r1Thread")
				r1_thread.daemon = True
				r1_thread.start()
		# If the problem is AGV, update the position info
		elif AGV2_state != BTS.AGV2_AT_P20:
			if not agv2_bt_thread.is_alive():
				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
				agv2_bt_thread.daemon = True
				agv2_bt_thread.start();
	# 4 - If object has been placed, reset cycle
	else:
		R1_picture_ok = False
		R1_pick_ok = False
		R1_place_ok = False

	###############
	# R2 workflow #
	###############
	# 1 - If we have picked 4, send distance place commands
	if R2_picked_counter == 4:
		if not r2_thread.is_alive():
			r2_thread = threading.Thread(target=R2PlaceObjects, name="r2Thread", args=(CAM.getOrderedCards()))
			r2_thread.daemon = True
			r2_thread.start()
	# 2 - If we have picked 8, send color place commands
	elif R2_picked_counter == 8:
		if not r2_thread.is_alive():
			r2_thread = threading.Thread(target=R2PlaceObjects, name="r2Thread", args=(CAM.getOrderedColors()))
			r2_thread.daemon = True
			r2_thread.start()
	# 3 - Else, pick another object
	else:
		# If everything is in position, pick object
		if (R2_state == R2_AT_PICK_POS) and (AGV2_state == BTS.AGV2_AT_P21):
			if not r2_thread.is_alive():
				r2_thread = threading.Thread(target=R2PickObject, name="r2Thread")
				r2_thread.daemon = True
				r2_thread.start()
		# If the problem is AGV, update the position info
		elif AGV2_state != BTS.AGV2_AT_P21:
			if not agv2_bt_thread.is_alive():
				agv2_bt_thread = threading.Thread(target=agv2UpdateState, name="agv2Thread")
				agv2_bt_thread.daemon = True
				agv2_bt_thread.start();


