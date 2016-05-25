import cv2
import imutils
import numpy as np
import math 
import operator
from collections import deque
import recognition.recognition_conf as conf

# --------------------------------------------------
# Image processing algorithm switcher
bs_selector = { # Background subtration
	conf.BackgroundSubtractor.MOG:	lambda: cv2.bgsegm.createBackgroundSubtractorMOG(50,30,0.9,5), # parameter example: (200, 5, 0.5, 0)
	conf.BackgroundSubtractor.MOG2:	lambda: cv2.createBackgroundSubtractorMOG2(varThreshold=50),
	conf.BackgroundSubtractor.GMG:	lambda: cv2.bgsegm.createBackgroundSubtractorGMG(),
}

blur_selector = { # Blur method to fill gaps between close contours
	conf.GapFillingMethod.MEDIAN:		lambda frame: cv2.medianBlur(frame, 5),
	conf.GapFillingMethod.BILATERAL:	lambda frame: cv2.bilateralFilter(frame, 9, 75, 75),
}


# --------------------------------------------------
# Useful functions
def calc_center_of_mass(cnt):
	M = cv2.moments(cnt)
	cx = int(M['m10'] / M['m00'])
	cy = int(M['m01'] / M['m00'])

	return (cx, cy)


def calc_dist(pos1, pos2):
	return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])
	#return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def calc_dist_line_point(line_start, line_end, point):
	normal_length = math.hypot(line_end[0] - line_start[0], line_end[1] - line_start[1]) 
	rel_distance = (point[0] - line_start[0]) * (line_end[1] - line_start[1]) - \
		(point[1] - line_start[1]) * (line_end[0] - line_start[0])
	return rel_distance / normal_length

# --------------------------------------------------
# Class definition
# Single object information 
class SingleObjectInfo:
	def __init__(self, ID):
		self.ID = ID
		self.starting_point = None
		self.prev_contour = None
		self.prev_min_rect = None
		self.prev_cnt_area = None
		self.position_list = deque(maxlen=conf.NUM_FRAMES_TO_TRACK_PATH)
		self.last_actual_update = 0 # How many frames are expired after actual detection
		self.num_actual_updates = 0

	def update_movement(self, cnt, is_actual):
		# store contour and update position (based on center of mass)
		center_of_mass = calc_center_of_mass(cnt)
		if self.starting_point is None:
			self.starting_point = center_of_mass

		self.prev_contour = cnt
		self.prev_min_rect = cv2.minAreaRect(cnt)
		self.prev_cnt_area = cv2.contourArea(cnt)
		self.position_list.append(center_of_mass)

		if is_actual:
			self.last_actual_update = 0
			self.num_actual_updates += 1

	def __repr__(self):
		return "'" + self.ID + " -> " + str(self.last_actual_update) + "'"

# Object tracking main class
class TEObjectTracker:
	def __init__(self):
		# background subtraction backend
		self.bs = bs_selector[conf.BG_SUBTRACTOR]()

		# Post processing configuration
		self.noise_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, conf.FILTER_NOISE_SIZE)

		# Object tracking data structure (list of SingleObjectInfo)
		self.total_seen_objects = 0
		self.tracked_objects = []
		self.use_direction_counter = conf.USE_DEFAULT_DIRECTION_COUNTING 
		
		# Area based tracking
		self.occ_lst = None 
		self.occ_history = deque(maxlen=conf.OCCUPANCY_HISTORY_LEN)
		self.checkout_occ = None
		self.cur_in = False
		self.cur_out = False
		self.last_report_iter = 0

		# frame related variables
		self.blank = None # blank image (to be used for contours)
		self.frame_size = None
		self.iteration = 0
		
	# Main member function for updating with a new frame
	def feed_frame(self, frame):
		# 0. Initialize data structures (only once)
		if self.blank is None:
			self.blank = np.zeros(frame.shape[0:2])
		if self.frame_size is None:
			self.frame_size = frame.shape[0:2]
		self.iteration += 1

		# 1. Background subtraction
		#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
		fgmask = self.bs.apply(frame)
		fgmask_post = fgmask.copy()

		# 2. Post processing
		# 2a. shadow handling (optional)
		if conf.NEGLECT_SHADOW:
			fgmask_post = cv2.threshold(fgmask_post, self.bs.getShadowValue() + 1, 255, cv2.THRESH_BINARY)[1] 

		# 2b. Remove noise (small sparse pixels)
		fgmask_post = cv2.morphologyEx(fgmask_post, cv2.MORPH_OPEN, self.noise_kernel)

		# 2c. Fill gaps
		fgmask_post = blur_selector[conf.GAP_FILLING_METHOD](fgmask_post)

		if conf.DETECTION_METHOD == conf.DetectionMethod.OBJECT_TRACK:
			return self.object_based_track(fgmask_post), fgmask, fgmask_post
		else: # conf.DetectionMethod.AREA_TRACK
			self.area_based_track(fgmask_post)
			return [], fgmask, fgmask_post

	# Object identification and track the path
	def object_based_track(self, frame):
		# 3. Object detection
		contours = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		contours = filter(lambda cnt:
				cnt is not None and
				len(cnt) > 0 and
				cv2.contourArea(cnt) > conf.MIN_OBJECT_AREA and
				cv2.contourArea(cnt) < conf.MAX_OBJECT_AREA, contours)

		# 4. Sudden change verification
		if conf.CHECK_SUDDEN_CHANGE and self.verify_sudden_change(contours):
			return contours

		# 5. Track objects
		self.track_objects_from_contours(contours)

		return contours

	# Area based tracking related
	def occ_in_history(self, occ_history, idx):
		return any(map(lambda x: x[idx], occ_history))

	def area_based_track(self, frame):
		# 3. count # of moved pixels to compute occupancy
		# 3a. subsampling
		box = conf.TARGET_AREA
		(H, W) = frame.shape[:2]
		if conf.SUBSAMPLING_SCALE > 1:
			frame = imutils.resize(frame, width=W/conf.SUBSAMPLING_SCALE)
			box = list(map(lambda (x,y): (x/conf.SUBSAMPLING_SCALE, y/conf.SUBSAMPLING_SCALE), box))
			(H, W) = frame.shape[:2]
		box_height = box[1][1] - box[0][1]
		box_width = box[1][0] - box[0][0]
		box_area = box_height * box_width

		# 3b. check sudden change
		if conf.CHECK_SUDDEN_CHANGE and cv2.countNonZero(frame) > (W*H) * conf.SUDDEN_CHANGE_RATIO:
			print("Sudden change detected")
			self.flush_objects()
			return []

		# 3c. Split frame into 3 parts and compute occupancy of each
		count_lst = []
		for i in range(3):
			y_pos = box[0][1] + box_height*i/3
			f = frame[y_pos:y_pos + box_height/3, box[0][0]:box[1][0]]
			count_lst.append(cv2.countNonZero(f))
		occ_lst = list(map(lambda c: (c / float(box_area/3)) > conf.OCCUPIED_RATIO, count_lst))

		#print(count_lst[0], count_lst[1], count_lst[2])
		#print(occ_lst)

		# 4. Check crossed objects
		self.cur_in = False
		self.cur_out = False
		if self.occ_lst is not None and self.iteration - self.last_report_iter > conf.MIN_REPORT_INTERVAL:
			if self.occ_lst[1] == True and occ_lst[1] == False:
				if any(occ_lst): 
					self.checkout_occ = (self.iteration, occ_lst, list(self.occ_history))
				else: # quick change -> Use previous frame
					self.checkout_occ = (self.iteration, list(self.occ_lst), list(self.occ_history))

		# After noisy frames
		if self.checkout_occ is not None and self.iteration - self.checkout_occ[0] > conf.MIN_NOISY_INTERVAL:
			oc = self.checkout_occ[1]
			oh = self.checkout_occ[2]
			#print("!!!", oc, oh)

			if oc[0] == True and self.occ_in_history(oh, 2):
				self.cur_in = True
			if oc[2] == True and self.occ_in_history(oh, 0):
				self.cur_out = True

			if self.cur_in or self.cur_out:
				self.last_report_iter = self.checkout_occ[0]
				#print("C", self.cur_in, self.cur_out)
			self.checkout_occ = None

		self.occ_lst = occ_lst
		self.occ_history.append(occ_lst)

		return []

	# Sudden change detection
	# * If sudden change appears in screen,
	# any BS algorithm couldn't detect object contours correctly.
	# In this case, reset the background subtractor so that we could proceed the processing
	def verify_sudden_change(self, contours):
		area_sum = sum(map(lambda cnt: cv2.contourArea(cnt), contours))

		if area_sum > conf.SUDDEN_CHANGE_AREA:
			print("Sudden change detected")
			self.bs = bs_selector[conf.BG_SUBTRACTOR]()
			return True

		return False

	# return if the two countours intersect each other
	def check_intersection_from_contours(self, cnt1, cnt2):
		img1 = cv2.drawContours(self.blank.copy(), [cnt1], -1, 1)
		img2 = cv2.drawContours(self.blank.copy(), [cnt2], -1, 1)

		intersection = np.logical_and(img1, img2)
		return np.count_nonzero(intersection) > 0

	# return if the two countours intersect each other using rotated rect
	# (slight inaccurate but much faster)
	def check_intersection_from_rect(self, rect1, rect2):
		#print(rect1, rect2)
		ret, _ = cv2.rotatedRectangleIntersection(rect1, rect2)
		return ret != cv2.INTERSECT_NONE

	# return if the two countour sizes are similar
	def check_area_size_similarity(self, area1, area2):
		return abs(1 - (area1 / area2)) < conf.MAX_RATIO_OF_AREA_CHANGE

	# Sub function to track by identifying same objects (mainly private use)
	def track_objects_from_contours(self, contours):
		# 1. Update the number of frames from the last actual update
		for sobj in self.tracked_objects:
			sobj.last_actual_update += 1

		# 2. Update movement for each object (with adding new objects)
		for new_cnt in contours:
			pos = calc_center_of_mass(new_cnt)
			rect = cv2.minAreaRect(new_cnt)
			area = cv2.contourArea(new_cnt)

			# Get the list of objects intersected with distance
			inter_objects = []
			for sobj in self.tracked_objects:
				#if self.check_intersection_from_contours(new_cnt, sobj.prev_contour):
				if self.check_intersection_from_rect(rect, sobj.prev_min_rect) and \
					self.check_area_size_similarity(area, sobj.prev_cnt_area):
					dist = calc_dist(pos, sobj.position_list[-1])
					inter_objects.append((sobj, dist))

			# Find closest points
			if len(inter_objects) > 0:
				min_sobj = min(inter_objects, key=operator.itemgetter(1))[0]
				min_sobj.update_movement(new_cnt, True)
			else:
				# No intersected object. Regard as a new object
				new_sobj = SingleObjectInfo("ID" + str(self.total_seen_objects))
				new_sobj.update_movement(new_cnt, True)
				self.tracked_objects.append(new_sobj)
				self.total_seen_objects += 1

		# 3. Remove old objects
		if self.use_direction_counter: # for removed objects, check the valid direction
			self.cur_in = False
			self.cur_out = False
			candidate_objects = filter(
					lambda sobj: sobj.last_actual_update >= conf.NUM_FRAMES_TO_REMOVE_OBJECTS and \
					sobj.num_actual_updates > conf.NUM_FRAMES_TO_CONFIRM_OBJECTS,
					self.tracked_objects)

			for sobj in candidate_objects:
				start_x = sobj.starting_point[0]
				(last_x, _) = sobj.position_list[-1]
				(_, W) = self.frame_size
				#print(start_x, last_x, W)

				if start_x < W * conf.DIRECTION_RELATIVE_POSITION and last_x > W * (1 - conf.DIRECTION_RELATIVE_POSITION):
					self.cur_in = True
				elif last_x < W * conf.DIRECTION_RELATIVE_POSITION and start_x > W * (1 - conf.DIRECTION_RELATIVE_POSITION):
					self.cur_out = True

		self.tracked_objects = filter(
				lambda sobj: sobj.last_actual_update < conf.NUM_FRAMES_TO_REMOVE_OBJECTS,
				self.tracked_objects)

		# 4. Update not-found object position
		for sobj in self.tracked_objects:
			if sobj.last_actual_update == 0:
				continue

			# Just assume that it's not moving
			# predict new position based on kalman filter
			sobj.update_movement(sobj.prev_contour, False)

	# Get all tracked-confirmed objects - for object track based
	def get_tracked_objects(self, only_now_seen_objects = False):
		confirmed_objects = filter(
				lambda sobj: sobj.num_actual_updates > conf.NUM_FRAMES_TO_CONFIRM_OBJECTS,
				self.tracked_objects)

		if only_now_seen_objects:
			return filter(lambda sobj: sobj.last_actual_update == 0, confirmed_objects)

		return confirmed_objects

	# Occupied area
	def get_occupied_area_info(self):
		if self.occ_lst is None:
			return []

		box = conf.TARGET_AREA
		box_height = box[1][1] - box[0][1]

		box_list_with_occupancy = []
		for i in range(3):
			y_pos = box[0][1] + box_height*i/3
			area = ((box[0][0], y_pos), (box[1][0], (y_pos + box_height/3)))
			box_list_with_occupancy.append((area, self.occ_lst[i]))

		return box_list_with_occupancy

	# Get in/out state of internal counting (area or direction)
	def get_in_out_count(self):
		return self.cur_in, self.cur_out

	# Set direction counter - for object track based
	def set_direction_counter(self, val):
		self.use_direction_counter = val

	# Delete all tracked objects to newly start
	def flush_objects(self):
		self.tracked_objects = []
		self.total_seen_objects = 0
		self.occ_lst = None
		self.checkout_occ = None
		self.occ_history = deque(maxlen=conf.OCCUPANCY_HISTORY_LEN)
		self.cur_in = False
		self.cur_out = False

# Object counting class 1. line-based
class TELineBasedCounter:
	def __init__(self):
		self.reference_line = None
		self.object_counter = dict() # store if an object was online at least once

	# Is line set?
	def is_line_set(self):
		return self.reference_line is not None

	# Set reference line
	def set_reference_line(self, line):
		self.reference_line = line
		if line is None:
			self.flush_objects()

	# Profess tracked objects for each frame
	def feed_objects(self, tracked_objects, remove_untracked_object = True):
		if self.reference_line is None:
			return []

		(line_start, line_end) = self.reference_line

		# NOTE: it works correctly only if
		# the tracked objects is given when "only_now_seen_objects" is true 
		if remove_untracked_object: 
			trackable_object_counter = dict()
			for sobj in tracked_objects:
				if sobj.ID in self.object_counter.keys():
					trackable_object_counter[sobj.ID] = self.object_counter[sobj.ID]

			self.object_counter = trackable_object_counter

		# Check line-crossing for each object
		crossing_objects = []
		for sobj in tracked_objects:
			last_pos = sobj.position_list[-1]
			dist = calc_dist_line_point(line_start, line_end, last_pos)
			abs_dist = abs(dist)

			# If don't have, create as a tracked object
			if sobj.ID not in self.object_counter.keys():
				self.object_counter[sobj.ID] = False

			# Check line crossing
			if abs_dist < conf.MIN_DISTANCE_ON_LINE:
				self.object_counter[sobj.ID] = True
			elif abs_dist > conf.MIN_DISTANCE_CLOSE_TO_LINE and self.object_counter[sobj.ID] == True:
				self.object_counter[sobj.ID] = False # Not to be tracked again
				crossing_objects.append((sobj.ID, dist>0))

		return crossing_objects

	# Delete all tracked objects to newly start
	def flush_objects(self):
		self.object_counter = dict()
