import cv2
import argparse

from videohandler.videoutil import *
from recognition.object_tracking import *
import recognition.recognition_conf as recg_conf

def merge_2x2frames(frame_list): # If # of frames > 4, ignored
	(h, w) = frame_list[0].shape[:2]
	zeros = np.zeros((h, w, 3), dtype="uint8")

	f = []
	for idx in xrange(4):
		if idx < len(frame_list):
			f.append(frame_list[idx])
		else:
			f.append(zeros)

	merged = np.zeros((h*2, w*2, 3), dtype="uint8")
	merged[0:h, 0:w] = f[0]
	merged[0:h, w:w*2] = f[1]
	merged[h:h*2, 0:w] = f[2]
	merged[h:h*2, w:w*2] = f[3]

	return merged

def draw_path(frame, path):
	for i in xrange(1, len(path)):
		cv2.line(frame, path[i - 1], path[i], (0, 0, 255), 1)

if __name__ == '__main__':
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-r", "--record_video",
		help="path to the video file to write (optional)")
	ap.add_argument("-t", "--record_track", action='store_true',
		help="record video with the tracking result (valid only if -r is given, optional)", required=False)
	ap.add_argument("-f", "--print_framenumber", action='store_true',
		help="print the frame number, optional)", required=False)

	args = vars(ap.parse_args())
	record_track = args.get("record_track", False)
	print_fn = args.get("print_framenumber", False)

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

	# Frame stream processing
	num_frames = 0
	while True:
		# READING STREAM
		try:
			frame = video_handler.read()
		except TEInvalidFrameException as e:
			print("Invalid frame exception: maybe it reaches to the end of the file.")
			break

		# Make a copy of the original frame
		original_frame = frame.copy()
		frame_result = frame.copy()

		# Find objects & show into the frame
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

		# Draw the result frame with paths
		tracked_objects = object_tracker.get_tracked_objects()
		for sobj in tracked_objects:
			draw_path(frame_result, sobj.position_list)
			cv2.drawContours(frame_result, [sobj.prev_contour], -1, (0, 255, 0), 2)
			pos = sobj.position_list[-1]
			cv2.putText(frame_result, sobj.ID, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


		# After PROCESSING: show the frame to our screen
		merged_frame = merge_2x2frames([frame, frame_mask, frame_post, frame_result])
		cv2.imshow("Triton Eye", merged_frame)

		# record video
		if video_writer.isopened():
			if record_track:
				video_writer.record(merged_frame)
			else:
				video_writer.record(original_frame)

		# if the 'q' key is pressed, stop the loop
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break

		if print_fn:
			print(num_frames)
		num_frames += 1

	# After pressing q (or the end of the frame)
	# cleanup the camera and close any open windows
	video_handler.release()
	video_writer.release()
	cv2.destroyAllWindows()
