import googlemaps
import io
import os
import sys
import google.cloud.vision
import json
from datetime import datetime

from time import sleep
from geotext import GeoText

#camera = PiCamera()
def compute_distance(camera):
	print "Distances"
	#my_file = open('image.jpg', 'wb')
	thereisCity = 0
	thereisText = 0
	while thereisCity == 0:
		while thereisText == 0:
			camera.capture('image.jpg')

			client = google.cloud.vision.ImageAnnotatorClient()

			#image_file_name = '../Images/DSC_2045.JPG'
			image_file_name = 'image.jpg'
			with io.open(image_file_name, 'rb') as image_file:
				content = image_file.read()

			image = google.cloud.vision.types.Image(content=content)

			response = client.text_detection(image=image)
			texts = response.text_annotations
			thereisText = len(texts)
			print thereisText

		#my_file.flush()
		#my_file.close()

		print('Texts:')

		#for text in texts:

		text_total = '"{}"'.format(texts[0].description.encode('utf-8'))

		print text_total
		places = GeoText(text_total)
		thereisCity = len(places.cities)
		print "Lenght city property"
		print thereisCity
		thereisText = thereisCity
	
	city=places.cities[0]
	print "city is:"
	print city
	#print(place)

	gmaps = googlemaps.Client(key='AIzaSyC0xbKR7oOTPYHlCwo7Os4kKH31naeZDAo')


	now = datetime.now()
	directions_result = gmaps.directions(city,
	                                     "Barcelona",
	                                     mode="driving",
	                                     avoid="ferries",
	                                     departure_time=now
	                                    )

	#print(directions_result[0]['legs'][0]['distance']['text'])

	distance = directions_result[0]['legs'][0]['distance']['value']
	#distance = distance[0]
	#distance = float(distance)
	return distance