# For files
import io
# For analyzing
import googlemaps
import google.cloud.vision
from datetime import datetime
from geotext import GeoText


def compute_distance(camera, client, debug=True):
	"""Take a picture, find text in it, find a city in the text and compute the distance to Barcelona"""
	thereisCity = 0
	thereisText = 0
	# While no city has been detected
	while thereisCity == 0:
		# Take pictures until we detect text
		while thereisText == 0:
			# Take picture
			camera.capture('image.jpg')
			# Upload the picture to google cloud vision and obtain the response
			image_file_name = 'image.jpg'
			with io.open(image_file_name, 'rb') as image_file:
				content = image_file.read()
			image = google.cloud.vision.types.Image(content=content)
			response = client.text_detection(image=image)
			# Get the text detected
			texts = response.text_annotations
			thereisText = len(texts)
			if debug and not thereisText == 0: print("[CAMERA]: no text detected")

		# We have detected text
		text_total = '"{}"'.format(texts[0].description.encode('utf-8'))
		if debug: print("[CAMERA]: text detected: %s" %(text_total))
		# Find a city name in the text
		places = GeoText(text_total)
		thereisCity = len(places.cities)
		if debug and not thereisCity == 0: print("[CAMERA]: no city detected")
		thereisText = thereisCity
	
	# We have found a city
	city=places.cities[0]
	if debug: print("[CAMERA]: city detected: %s" %(city))
	# Find the distance to Barcelona
	gmaps = googlemaps.Client(key='AIzaSyC0xbKR7oOTPYHlCwo7Os4kKH31naeZDAo')
	now = datetime.now()
	directions_result = gmaps.directions(city, "Barcelona", mode="driving", avoid="ferries", departure_time=now)
	distance = directions_result[0]['legs'][0]['distance']['value']

	return distance