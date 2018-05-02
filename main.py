#import googlemaps
import io
import os
import sys
#import google.cloud.vision
import json
import random
#from datetime import datetime
#from picamera import PiCamera
#from time import sleep
from computeDistance import *
from dominantColors import *

def f(x):
    return {
         '0' : 1,
         '1' : 2,
         '2' : 3,
         '3' : 4,
    }[x]


print sys.argv[1]
camera = PiCamera()

#distance = compute_distance()
#print distance
#random.randint(0,5)*10

if int(sys.argv[1]) == 0:
	#DISTANCES
	print('Init Distance')
	N = 4
	Card = []
	raw_input("Press Enter to start...")
	for i in range(0,N):
		distance = compute_distance(camera)
		Card.append([i, distance])
		print Card
		raw_input("Press Enter to continue...")

	print(Card)
	Card.sort(key=lambda x: x[1])
	print(Card)

	for i in range (0,N):
		if(Card[i][0] == 0):
			print "Go to 1"
		elif(Card[i][0] == 1):
			print "Go to 2"
		elif(Card[i][0] == 2):
			print "Go to 3"
		else:
			print "Go to 4"
		#print ('Movement ',f(str(Card[i][0])))

else:
	#DOMINANT COLOR
	print('Init Dominant Color')
	N = 4
	Color = []
	raw_input("Press Enter to start...")
	for i in range(0,N):
		colors = dominant_color(camera)
		Color.append([i, colors])
		print Color
		raw_input("Press Enter to continue...")

	print(Color)
	Color.sort(key=lambda x: x[1])
	print(Color)

	for i in range (0,N):
		if (Color[i][0] == 0):
			print "Go to 1"
		elif (Color[i][0] == 1):
			print "Go to 2"
		elif (Color[i][0] == 2):
			print "Go to 3"
		else:
			print "Go to 4"
