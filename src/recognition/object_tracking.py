import cv2
import imutils
import numpy as np
from collections import deque
import recognition.recognition_conf as conf

# --------------------------------------------------
# Image processing algorithm switcher
bs_selector = { # Background subtration
	conf.BackgroundSubtractor.MOG:	lambda: cv2.bgsegm.createBackgroundSubtractorMOG(), # parameter example: (200, 5, 0.5, 0)
	conf.BackgroundSubtractor.MOG2:	lambda: cv2.createBackgroundSubtractorMOG2(),
	conf.BackgroundSubtractor.GMG:	lambda: cv2.bgsegm.createBackgroundSubtractorGMG(),
}

blur_selector = {
	conf.GapFillingMethod.MEDIAN:		lambda frame: cv2.medianBlur(frame, 5),
	conf.GapFillingMethod.BILATERAL:	lambda frame: cv2.bilateralFilter(frame, 9, 75, 75),
}


# --------------------------------------------------
# Object tracking main class
class TEObjectTracker:
	def __init__(self):
		# background subtraction backend
		self.bs = bs_selector[conf.BG_SUBTRACTOR]()

		# Post processing configuration
		self.noise_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, conf.FILTER_NOISE_SIZE)

		# TODO: Object tracking data structure
		self.tracked_objects = dict() 
		self.recent_contours_info = deque(maxlen=conf.RECENT_FRAMES_TO_TRACK)
		
	def feed_frame(self, frame):
		# 1. Background subtraction
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

		# 3. Object detection
		contours = cv2.findContours(fgmask_post.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		contours = filter(lambda cnt:
				cnt is not None and
				len(cnt) > 0 and
				cv2.contourArea(cnt) < conf.MIN_OBJECT_AREA, contours)
		
		# TODO
		# collect all previous countours with labeled index 
		#previous_countours = dict()
		#for i in xrange(0, len(self.recent_contours_info)):
		#	(countours, index_list) = self.recent_contours_info[i]
		#	for (cnt, index) in zip(countours, index_list):
		#		if index not in previous_countours.keys():
		#			previous_countours[index] = cnt


		return contours, fgmask, fgmask_post

	def flush_objects(self):
		# TODO
		self.tracked_objects = dict()
