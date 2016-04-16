from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g

stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)

#for frame in stream:
while True:
	frame = stream.next()
	image = frame.array

	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF

	rawCapture.truncate(0)

	if key == ord("q"):
		break
