import cv2
import argparse

from videohandler.videoutil import *
from recognition.object_tracking import *
import recognition.recognition_conf as recg_conf

# Merge frames into a single frame to display
def merge_2x2frames(frame_list): # If # of frames > 4, ignored
	global h, w
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

# Convert points to the frame wise
def convert_points_on_2x2_frame(x, y):
	global h, w # Set in merge_2x2frames

	if x > w:
		x -= w
	if y > h:
		y -= h

	return (x, y)

# Draw path with lines
def draw_path(frame, path):
	for i in xrange(1, len(path)):
		cv2.line(frame, path[i - 1], path[i], (0, 0, 255), 1)

# Mouse handler for the window
def mouse_handler(event, x, y, flags, param):
	global line_start, line_end, line_based_counter

	if event == cv2.EVENT_LBUTTONDOWN:
		line_end = None
		line_based_counter.set_reference_line(None)
		line_start = convert_points_on_2x2_frame(x, y)

	if event == cv2.EVENT_LBUTTONUP:
		line_end = convert_points_on_2x2_frame(x, y)

if __name__ == '__main__':
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-r", "--record_video",
		help="path to the video file to write (optional)")
	ap.add_argument("-t", "--record_track", action='store_true',
		help="record video with the tracking result (valid only if -r is given, optional)", required=False)
	ap.add_argument("-f", "--print_verbose", action='store_true',
		help="print the frame number, optional)", required=False)

	args = vars(ap.parse_args())
	record_track = args.get("record_track", False)
	print_verbose = args.get("print_verbose", False)

	# Setup VideoStream (camera or video file) & Writer
	video_handler = TEVideoHandler()
	if args.get("video", False): # if a video path was not supplied, grab the reference to the picamera
		video_handler.initialize_with_file(args["video"])
	else:
		video_handler.initialize_with_configured_cam()

	video_writer = TEVideoWriter()
	if (args.get("record_video", False)): # to record a video
		video_writer.open(args["record_video"])

	# Setup user interface
	line_start = None
	line_end = None
	WINDOW_NAME = "Triton Eye"
	cv2.namedWindow(WINDOW_NAME)
	cv2.setMouseCallback(WINDOW_NAME, mouse_handler)

	# Setup image processing classes
	object_tracker = TEObjectTracker()
	line_based_counter = TELineBasedCounter()
	count_in = 0
	count_out = 0

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
			cv2.putText(frame_result, sobj.ID, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

		# Update line counter
		if line_start is not None and line_end is not None and not line_based_counter.is_line_set():
			line_based_counter.set_reference_line((line_start, line_end))
		crossing_objects = line_based_counter.feed_objects(tracked_objects)
		if len(crossing_objects) > 0:
			if print_verbose:
				print(crossing_objects)

			for co in crossing_objects:
				if co[1] == True:
					count_in += 1
				else:
					count_out += 1

		# Draw user-defined line
		if line_start is not None and line_end is not None:
			cv2.line(frame_result, line_start, line_end, (0, 255, 255), 2)

		# After PROCESSING: show the frame to our screen
		merged_frame = merge_2x2frames([frame, frame_mask, frame_post, frame_result])
		if count_in > 0 or count_out > 0:
			cv2.putText(merged_frame, "IN: " + str(count_in) + " OUT: " + str(count_out),
				(20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
		cv2.imshow(WINDOW_NAME, merged_frame)

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

		if print_verbose:
			print(num_frames)
		num_frames += 1

	# After pressing q (or the end of the frame)
	# cleanup the camera and close any open windows
	video_handler.release()
	video_writer.release()
	cv2.destroyAllWindows()
