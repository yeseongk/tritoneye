import sys, signal
import cv2
import argparse

from videohandler.videoutil import *
from recognition.object_tracking import *
from communication.tcpclient_util import *
import recognition.recognition_conf as recg_conf

# cleanup the camera/communication and close any open windows
def cleanup():
	global video_handler, video_writer, tcpinterface
	if video_handler is not None:
		video_handler.release()
	if video_writer is not None:
		video_writer.release()
	if tcpinterface is not None:
		tcpinterface.close()
	cv2.destroyAllWindows()

	print("All cleaned up")

# SIGINT(Control+C) hanling
def signal_handler(signal, frame):
	print("Pressed Ctrl+C. Clean up")
	cleanup()
	sys.exit(0)

def static_vars(**kwargs):
	def decorate(func):
		for k in kwargs:
			setattr(func, k, kwargs[k])
		return func
	return decorate

# Send over TCP
@static_vars(prev_counters = None)
def comm_counters(tcpinterface, count_in, count_out):
	if (tcpinterface is None):
		return

	if comm_counters.prev_counters is not None: 
		(prev_in, prev_out) = comm_counters.prev_counters
		diff_in = count_in - prev_in
		diff_out = count_out - prev_out

		if diff_in > 0 or diff_out > 0:
			tcpinterface.send_info(diff_in, diff_out)

	comm_counters.prev_counters = (count_in, count_out)
	

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
		print(line_start, line_end)

if __name__ == '__main__':
	# init global classes
	video_handler = None
	video_writer = None
	tcpinterface = None
	signal.signal(signal.SIGINT, signal_handler) # register signal handler

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help="path to the (optional) video file")
	ap.add_argument("-l", "--loop", action='store_true',
		help="loop video or log, optional", required=False)
	ap.add_argument("-r", "--record_video",
		help="path to the video file to write (optional)")
	ap.add_argument("-t", "--record_track", action='store_true',
		help="record video with the tracking result (valid only if -r is given, optional)", required=False)
	ap.add_argument("-f", "--print_verbose", action='store_true',
		help="print the frame number, optional", required=False)
	ap.add_argument("-wl", "--write_logfile", help="write a log file for transfered counts, optional", required=False)
	ap.add_argument("-sl", "--simulate_logfile", help="simulate a log file, optional. If given, no video processing is performed.", required=False)
	ap.add_argument("-ss", "--simulation_speed", help="simulation speed, optional. Default = 1", required=False)
	ap.add_argument("-di", "--device_id", help="device id sent to server, optional", required=False)
	
	args = vars(ap.parse_args())
	record_track = args.get("record_track", False)
	print_verbose = args.get("print_verbose", False)
	loop_procedure = args.get("loop", False)

	simulation_speed = 1
	if args.get("simulation_speed", False):
		simulation_speed = float(args["simulation_speed"])

	# Setup communication
	tcpinterface = TCPIPInterface()
	tcpinterface.connect()
	if args.get("device_id", False):
		tcpinterface.set_device_id(args["device_id"])

	if args.get("write_logfile", False):
		tcpinterface.set_log(args["write_logfile"])

	if args.get("simulate_logfile", False):
		do_simulate = True
		while do_simulate:
			tcpinterface.simulate_logfile(args["simulate_logfile"], simulation_speed)
			do_simulate = loop_procedure

		cleanup()
		sys.exit()

	# Setup VideoStream (camera or video file) & Writer
	video_handler = TEVideoHandler()
	if args.get("video", False): # if a video path was not supplied, grab the reference to the picamera
		video_handler.initialize_with_file(args["video"])
	else:
		video_handler.initialize_with_pycamera2()
		#video_handler.initialize_with_pycamera()

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
			if loop_procedure and args.get("video", False): # If loop is enabled
				print("Loop video")
				video_handler = TEVideoHandler()
				video_handler.initialize_with_file(args["video"])
				object_tracker = TEObjectTracker()
				line_based_counter = TELineBasedCounter()
				line_start = None
				line_end = None
				num_frames = 0
				continue
			break

		num_frames += 1
		#if num_frames % 10 != 0: # Skip frames
		#	continue

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
		if recg_conf.DETECTION_METHOD == recg_conf.DetectionMethod.OBJECT_TRACK:
			tracked_objects = object_tracker.get_tracked_objects()
			for sobj in tracked_objects:
				draw_path(frame_result, sobj.position_list)
				cv2.drawContours(frame_result, [sobj.prev_contour], -1, (0, 255, 0), 2)
				pos = sobj.position_list[-1]
				cv2.putText(frame_result, sobj.ID, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

			# Update line counter
			if line_start is not None and line_end is not None and not line_based_counter.is_line_set():
				object_tracker.set_direction_counter(False)
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
		else: # AREA_TRACK
			box_list_with_occupancy = object_tracker.get_occupied_area_info()
			for ((p1, p2), occ) in box_list_with_occupancy:
				if occ:
					color = (0,0,255)
				else:
					color = (0,255,0)
				cv2.rectangle(frame_result, p1, p2, color, 2)

		# Count info from the object tracker
		cur_in, cur_out = object_tracker.get_in_out_count()
		if cur_in:
			count_in += 1
		if cur_out:
			count_out += 1

		# After PROCESSING: show the frame to our screen
		merged_frame = merge_2x2frames([frame, frame_mask, frame_post, frame_result])
		if count_in > 0 or count_out > 0:
			cv2.putText(merged_frame, "IN: " + str(count_in) + " OUT: " + str(count_out),
				(20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
		cv2.imshow(WINDOW_NAME, merged_frame)

		# Update counts and send the info if required
		comm_counters(tcpinterface, count_in, count_out)

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

	# After pressing q (or the end of the frame)
	# cleanup the camera/communication and close any open windows
	cleanup()
