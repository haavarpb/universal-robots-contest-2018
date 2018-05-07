# For files
import io
import os
import sys
import pexpect
# For analyzing
from computeDistance import *
from dominantColors import *
# Import camera
from picamera import PiCamera

class Camera:

	def __init__(self):
		# pexpect.run('export GOOGLE_APPLICATION_CREDENTIALS=~miller/PC-Test/JasonKey/PC/PC-Test-132f522d6015.json')
		self.camera = PiCamera()
		self.cards = []
		self.colors = []

	def takePicture(self, picType):
		if picType == 0:
			#DISTANCES
			print('Init Distance')
			distance = compute_distance(self.camera)
			self.cards.append([len(self.cards)+1, distance])
		else:
			#DOMINANT COLOR
			print('Init Dominant Color')
			piccolors = dominant_color(self.camera)
			self.colors.append([len(self.colors)+1, piccolors])

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
			objectOrder = []
			# 1 - Picture with most R
			self.colors.sort(key=lambda x: x[1][0])
			objectOrder.append(self.colors.pop()[0])
			# 2 - Picture with most G (of the remainig ones)
			self.colors.sort(key=lambda x: x[1][1])
			objectOrder.append(self.colors.pop()[0])
			# 3 - Picture with most G (of the remainig ones)
			self.colors.sort(key=lambda x: x[1][2])
			objectOrder.append(self.colors.pop()[0])
			# 4 - Remaining picture
			objectOrder.append(self.colors.pop()[0])

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
