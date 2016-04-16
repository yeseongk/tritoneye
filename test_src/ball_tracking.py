# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
from imutils.video import VideoStream
import imutils
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
ap.add_argument("-r", "--record_video",
	help="path to the video file to write (optional)")
ap.add_argument("-t", "--record_track", action='store_true',
	help="record video with the tracking result (valid only if -r is given, optional)", required=False)
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space,
# color threshold for ball_tracking_example.mp4
#greenLower = (29, 86, 6)
#greenUpper = (64, 255, 255)
# color threshold for my own blue-green ball
greenLower = (93/2, 17/100*255, 17/100*255)
greenUpper = (163/2, 100/100*255, 100/100*255)

# then initialize the list of tracked points
pts = deque(maxlen=args["buffer"])

# to record a video
record_video = args.get("record_video", False)
record_track = args.get("record_track", False)
video_writer = None

# if a video path was not supplied, grab the reference
# to the picamera
from_vfile = args.get("video", False)

if not from_vfile:
	camera = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)
# otherwise, grab a reference to the video file
else:
	video_file = cv2.VideoCapture(args["video"])

# keep looping
while True:
	# grab the current frame
	if from_vfile:
		(grabbed, frame) = video_file.read()

		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
		if not grabbed:
			break
	else:
		frame = camera.read()


	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)

	# record video
	if record_video:
		if video_writer is None: # create interface
			(h, w) = frame.shape[:2]
			fourcc = cv2.VideoWriter_fourcc(*'MJPG')
			# Note: the extension of the filename must be avi
			video_writer = cv2.VideoWriter(args["record_video"], fourcc, 20, (w,h), True)
			#zeros = np.zeros((h,w), dtype="uint8")

		if not record_track:
			video_writer.write(frame)

		# If we want a color-splitted video (w&h also need to be doubled in creating writer.)
		#(B, G, R) = cv2.split(frame)
		#R = cv2.merge([zeros, zeros, R])
		#G = cv2.merge([zeros, G, zeros])
		#B = cv2.merge([B, zeros, zeros])
		#output = np.zeros((h*2, w*2, 3), dtype="uint8")
		#output[0:h, 0:w] = frame
		#output[0:h, w:w*2] = R
		#output[h:h*2, w:w*2] = G
		#output[h:h*2, 0:w] = B
		#video_writer.write(output)

	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

	# update the points queue
	pts.appendleft(center)

	# loop over the set of tracked points
	for i in xrange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# show the frame to our screen
	cv2.imshow("Frame", frame)

	if record_video and record_track:
		video_writer.write(frame)

	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
if not from_vfile:
	if hasattr(camera, 'release'): # Pycamera may not have the release function
		camera.release()
else:
	video_file.release()

if video_writer is not None:
	video_writer.release()

cv2.destroyAllWindows()

