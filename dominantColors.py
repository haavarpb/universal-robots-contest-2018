# For files
import io
# For analyzing
import google.cloud.vision



def dominant_color(camera):
	"""Take a picture and find the dominant colors"""

	# Take picture
	camera.capture('image.jpg')
	# Upload the picture to google cloud vision and obtain the response
	client = google.cloud.vision.ImageAnnotatorClient()
	image_file_name = 'image.jpg'
	with io.open(image_file_name, 'rb') as image_file:
		content = image_file.read()
	image = google.cloud.vision.types.Image(content=content)
	response = client.image_properties(image=image)
	# Obtain the dominant colors
	props = response.image_properties_annotation

	rsum = 0.0;
	gsum = 0.0;
	bsum = 0.0;
	once = 1;

	for color in props.dominant_colors.colors:
		rsum += color.score*color.color.red
		gsum += color.score*color.color.green
		bsum += color.score*color.color.blue
	print "rsum: %f gsum: %f bsum: %f" % (rsum,gsum,bsum)
	
	return [rsum, gsum, bsum]

