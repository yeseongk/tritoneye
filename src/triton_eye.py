import cv2
import argparse

from videohandler.videoutil import *
from recognition.object_tracking import *
import recognition.recognition_conf as recg_conf

if __name__ == '__main__':
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
	record_track = args.get("record_track", False)

	# Setup VideoStream (camera or video file) & Writer
	video_handler = TEVideoHandler()
	if args.get("video", False): # if a video path was not supplied, grab the reference to the picamera
		video_handler.initialize_with_file(args["video"])
	else:
		video_handler.initialize_with_configured_cam()

	video_writer = TEVideoWriter()
	if (args.get("record_video", False)): # to record a video
		video_writer.open(args["record_video"])

	# Setup image processing classes
	object_tracker = TEObjectTracker()
	#tracker2 = cv2.Tracker_create("TLD")
	init_once = False

	# keep looping
	num_frames = 0
	while True:
		# READING STREAM
		try:
			frame = video_handler.read()
		except TEInvalidFrameException as e:
			print("Invalid frame exception: maybe it reaches to the end of the file.")
			break

		# make a copy of the original frame
		original_frame = frame.copy()

		# PROCESSING
		# set reference frame
		#if object_tracker.get_reference_frame() is None:
		#	object_tracker.set_reference_frame(frame)

		# find object
		contours, frame_mask, frame_post = object_tracker.feed_frame(frame)
		frame_mask = cv2.cvtColor(frame_mask, cv2.COLOR_GRAY2BGR) 
		frame_post = cv2.cvtColor(frame_post, cv2.COLOR_GRAY2BGR) 

		for cnt in contours:
			rect = cv2.minAreaRect(cnt)
			box = cv2.boxPoints(rect)
			box_draw = np.int0(box)
			cv2.drawContours(frame, [box_draw], 0, (0, 0, 255), 2)
			cv2.drawContours(frame_mask, [box_draw], 0, (0, 0, 255), 2)
			cv2.drawContours(frame_post, [box_draw], 0, (0, 0, 255), 2)
			cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

			#if init_once == False and i > 20:
				#tracker2.init(frame, cv2.boundingRect(cnt))
				#print("!!")
				#rect = cv2.boundingRect(cnt)
				#track_window = rect
				#roi = frame[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
				#mask = fgmask[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
				#hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
				#roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
				#cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
				#term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
				#init_once = True

		if init_once == True:
			print("!?")
			hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
			dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
			ret, track_window = cv2.meanShift(dst, track_window, term_crit)
			newbox = track_window
			p1 = (int(newbox[0]), int(newbox[1]))
			p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
			cv2.rectangle(frame2, p1, p2, (0, 255, 0))


		#found, newbox = tracker2.update(frame)
		#if found:
			#print(newbox)
			#newbox = np.int0(newbox)
			#print(newbox)
			#cv2.drawContours(frame, [newbox], 0, (0, 255, 0), 2)
			#cv2.drawContours(frame2, [newbox], 0, (0, 255, 0), 2)

			#p1 = (int(newbox[0]), int(newbox[1]))
			#p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
			#cv2.rectangle(frame2, p1, p2, (0, 255, 0))

			#(x, y, w, h) = cv2.boundingRect(cnt)
			#cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

		print(num_frames)
		num_frames += 1

		# POST PROCESSING
		# show the frame to our screen
		cv2.imshow("Original", frame)
		cv2.imshow("BS Mask", frame_mask)
		cv2.imshow("Post", frame_post)

		# record video
		if video_writer.isopened():
			if record_track:
				video_writer.record(frame)
			else:
				video_writer.record(original_frame)

		# if the 'q' key is pressed, stop the loop
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break

	# After pressing q (or the end of the frame)
	# cleanup the camera and close any open windows
	video_handler.release()
	video_writer.release()
	cv2.destroyAllWindows()
