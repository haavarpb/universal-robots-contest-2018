# For files
import io
import os
import sys
# For analyzing
from computeDistance import *
from dominantColors import *
# Import camera
from picamera import PiCamera

class Camera:

	def __init__(self):
		self.camera = PiCamera()
		self.cards = []
		self.colors = []

	def takePicture(self, picType):
		if picType == 0:
			#DISTANCES
			print('Init Distance')
			distance = compute_distance(self.camera)
			self.cards.append([len(self.cards), distance])
		else:
			#DOMINANT COLOR
			print('Init Dominant Color')
			piccolors = dominant_color(self.camera)
			self.colors.append([len(self.colors), piccolors])

	def getOrderedCards(self):
		self.cards.sort(key=lambda x: x[1])
		objectOrder = [x[0] for x in self.cards]
		return objectOrder

			#for i in range (0,N):
			#	if(Card[i][0] == 0):
			#		print "Go to 1"
			#	elif(Card[i][0] == 1):
			#		print "Go to 2"
			#	elif(Card[i][0] == 2):
			#		print "Go to 3"
			#	else:
			#		print "Go to 4"
				#print ('Movement ',f(str(Card[i][0])))

	def getOrderedColors(self):
			self.colors.sort(key=lambda x: x[1])
			objectOrder = [x[0] for x in self.colors]
			return objectOrder

			#for i in range (0,N):
			#	if (Color[i][0] == 0):
			#		print "Go to 1"
			#	elif (Color[i][0] == 1):
			#		print "Go to 2"
			#	elif (Color[i][0] == 2):
			#		print "Go to 3"
			#	else:
			#		print "Go to 4"
