#!/usr/bin/env python
from __future__ import print_function

import binascii
import pygatt

import time

COMMAND_MOVE = bytearray([0x32])
AGV_AT_P10 = 0
AGV_AT_P11 = 1

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: (HEX) %s, ASCII %s" % (binascii.hexlify(value), value.decode("utf-8")))

    data_str = value.decode("utf-8")
    newest_value = int(data_str[-1])
    
    if newest_value == AGV_AT_P10:
    	print("AGV at P10. Waiting 2 secs.")
    	time.sleep(2)
    	# device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE)
    	# print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE), COMMAND_MOVE.decode("utf-8")))
    elif newest_value == AGV_AT_P11:
    	print("AGV at P11. Waiting 4 secs.")
    	time.sleep(4)
    	# device.char_write('0000ffe1-0000-1000-8000-00805f9b34fb', COMMAND_MOVE)
    	# print("Sent data: (HEX) %s, ASCII %s" % (binascii.hexlify(COMMAND_MOVE), COMMAND_MOVE.decode("utf-8")))


AGV_1_LILA = "34:15:13:1C:AF:0B"
AGV_2_GREEN = "34:15:13:1C:6C:E6"
# Many devices, e.g. Fitbit, use random addressing - this is required to
# connect.
ADDRESS_TYPE = pygatt.BLEAddressType.public

adapter = pygatt.GATTToolBackend()
adapter.start()
device = adapter.connect(AGV_1_LILA, address_type=ADDRESS_TYPE)

#for uuid in device.discover_characteristics().keys():
# 	print("Read UUID %s: %s" % (uuid, binascii.hexlify(device.char_read(uuid))))

device.subscribe("0000ffe1-0000-1000-8000-00805f9b34fb",callback=handle_data)
