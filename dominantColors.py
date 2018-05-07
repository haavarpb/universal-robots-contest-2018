import io
import os

import google.cloud.vision

import json

from time import sleep


def dominant_color(camera):
	camera.capture('image.jpg')

	client = google.cloud.vision.ImageAnnotatorClient()

	image_file_name = 'image.jpg'
	with io.open(image_file_name, 'rb') as image_file:
		content = image_file.read()

	image = google.cloud.vision.types.Image(content=content)

	response = client.image_properties(image=image)
	props = response.image_properties_annotation


	rsum = 0.0;
	gsum = 0.0;
	bsum = 0.0;
	once = 1;

	for color in props.dominant_colors.colors:
		rsum += color.pixel_fraction*color.color.red
		gsum += color.pixel_fraction*color.color.green
		bsum += color.pixel_fraction*color.color.blue
	print "rsum: %f gsum: %f bsum: %f" % (rsum,gsum,bsum)
	
	return [rsum, gsum, bsum]
	
	

"""
if (rsum >= 50) and (gsum < 50) and (bsum < 50):
	print('Dominant: red')
elif (rsum < 50) and (gsum >= 50) and (bsum < 50):
	print('Dominant: green')
elif (rsum < 50) and (gsum < 50) and (bsum >= 50):
	print('Dominant: blue')
elif (rsum > 50) and (gsum < rsum*2.0/3.0) and (gsum>50) and (bsum < 50):
	print('Dominant:orange')
elif (rsum > 50) and (gsum > 50) and (bsum < 50):
	print('Dominant: yellow')
else:
	print('Dominant white')
"""

