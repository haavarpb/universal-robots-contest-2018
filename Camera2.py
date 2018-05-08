# For environment variables
import os
# For analyzing
from computeDistance2 import *
from dominantColors import *
import google.cloud.vision
import googlemaps
# Import camera
from picamera import PiCamera

class Camera:

	def __init__(self, debug=True):
		# Set environment variable of Google Credentials
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/miller/PC-Test/JasonKey/PC/PC-Test-132f522d6015.json"
		# Initialise objects and variables
		self.camera = PiCamera()
		self.sclient = google.cloud.vision.ImageAnnotatorClient()
		self.cards = []
		self.colors = []
		self.debug = debug
		self.picturesTaken = 0
		self.gmaps = googlemaps.Client(key='AIzaSyC0xbKR7oOTPYHlCwo7Os4kKH31naeZDAo')

	def takePicture(self, picType):

		if picType == 0:
			# DISTANCES
			if self.debug: print("[CAMERA]: taking picture: Distances")
			distance = compute_distance(self.camera, self.sclient, self.gmaps)
			self.cards.append([len(self.cards)+1, distance])
		else:
			# DOMINANT COLOR
			if self.debug: print("[CAMERA]: taking picture: Dominant Color")
			piccolors = dominant_color(self.camera, self.sclient)
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
