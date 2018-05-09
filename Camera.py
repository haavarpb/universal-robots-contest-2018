import pexpect
# For analyzing
from computeDistance import *
from dominantColors import *
import google.cloud.vision
import os
# Import camera
from picamera import PiCamera
from subprocess import call



class Camera:

	def __init__(self, debug=True):

		# pexpect.run('export GOOGLE_APPLICATION_CREDENTIALS=~miller/PC-Test/JasonKey/PC/PC-Test-132f522d6015.json')
		# pexpect.run('export GOOGLE_APPLICATION_CREDENTIALS=/home/pi/miller/PC-Test/JasonKey/PC/PC-Test-132f522d6015.json')
		os.system('export GOOGLE_APPLICATION_CREDENTIALS=/home/pi/miller/PC-TEST/JasonKey/PC/PC-Test-132f522d6015.json')
		self.camera = PiCamera()
		self.client = google.cloud.vision.ImageAnnotatorClient()
		self.cards = []
		self.colors = []
		self.debug = debug
		self.picturesTaken = 0

	def takePicture(self, picType):

		if picType == 0:
			# DISTANCES
			if self.debug: print("[CAMERA]: taking picture: Distances")
			distance = compute_distance(self.camera, self.client)
			self.cards.append([len(self.cards)+1, distance])
		else:
			# DOMINANT COLOR
			if self.debug: print("[CAMERA]: taking picture: Dominant Color")
			piccolors = dominant_color(self.camera, self.client)
			self.colors.append([len(self.colors)+1, piccolors])

		self.picturesTaken += 1


	def getOrderedCards(self):

		self.cards.sort(key=lambda x: x[1])
		objectOrder = [x[0] for x in self.cards]
		return objectOrder


	def getOrderedColors(self):

		objectOrder = []
		# 1 - Picture with most R
		self.colors.sort(key=lambda x: x[1][0])
		objectOrder.append(self.colors.pop()[0])
		# 2 - Picture with most G (of the remainig ones)
		self.colors.sort(key=lambda x: x[1][1])
		objectOrder.append(self.colors.pop()[0])
		# 3 - Picture with most B (of the remainig ones)
		self.colors.sort(key=lambda x: x[1][2])
		objectOrder.append(self.colors.pop()[0])
		# 4 - Remaining picture
		objectOrder.append(self.colors.pop()[0])

		return objectOrder
