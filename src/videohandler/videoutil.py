import cv2
import imutils
import time
from imutils.video import VideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera

import videohandler.video_conf as conf

# Custom Exception class
class TEVideoException(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

# 
class TEInvalidFrameException(Exception):
	def __init__(self):
		self.value = "Invalid Frame"

	def __str__(self):
		return self.value

# Video Handler
# This class generate stream by either reading a file or streaming from a camera
class TEVideoHandler:
	def __init__(self):
		self.FRAME_WIDTH = conf.DEF_FRAME_WIDTH
		self.FRAME_HEIGHT = conf.DEF_FRAME_HEIGHT

		# devices
		self.video_file = None
		self.camera = None
		self.picamera = None
		
	def set_frame_size(w, h):
		if self.video_file is not None or self.camera is not None or self.picamera is not None:
			raise TEVideoException("Frame size need to be set before initialization")

		self.FRAME_WIDTH = w
		self.FRAME_HEIGHT = h

	def initialize_with_file(self, filename):
		if self.video_file is not None or self.camera is not None or self.picamera is not None:
			raise TEVideoException("Already Initialized")

		self.video_file = cv2.VideoCapture(filename)

	def initialize_with_configured_cam(self):
		cam_selector = {
			conf.CameraType.PYCAMERA:			lambda: self.initialize_with_pycamera(),
			conf.CameraType.PYCAMERA_ROBUST:	lambda: self.initialize_with_pycamera2(),
			conf.CameraType.WEBCAM:				lambda: self.initialize_with_webcam(),
		}

		cam_selector[conf.CAMERA_TYPE]()


	def initialize_with_pycamera(self):
		if self.video_file is not None or self.camera is not None or self.picamera is not None:
			raise TEVideoException("Already Initialized")

		self.camera = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)

	# It uses picamera library to disable auto control feature
	def initialize_with_pycamera2(self):
		if self.video_file is not None or self.camera is not None or self.picamera is not None:
			raise TEVideoException("Already Initialized")

		self.picamera = PiCamera()
		self.picamera.resolution = (self.FRAME_WIDTH, self.FRAME_HEIGHT)
		self.picamera.framerate = 30
		self.rawCapture = PiRGBArray(self.picamera, size=(self.FRAME_WIDTH, self.FRAME_HEIGHT))

		time.sleep(0.1)

		self.picamera.shutter_speed = self.picamera.exposure_speed
		self.picamera.exposure_mode = 'off'
		g = self.picamera.awb_gains
		self.picamera.awb_mode = 'off'
		self.picamera.awb_gains = g
		self.stream = self.picamera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)


	# Tested with a monitor webcam, but didn't checked with the webcam macbook
	def initialize_with_webcam(self):
		if self.video_file is not None or self.camera is not None or self.picamera is not None:
			raise TEVideoException("Already Initialized")

		self.camera = VideoStream().start()
		time.sleep(2.0)

	# Read a frame	
	# Return: frame (pixel array)
	# Note: if not grapped (for video file), raise exception
	def read(self):
		frame = None
		if self.video_file is not None:
			(grabbed, frame) = self.video_file.read()
			if not grabbed:
				raise TEInvalidFrameException()
		elif self.camera is not None:
			frame = self.camera.read()
		elif self.picamera is not None:
			data = self.stream.next()
			frame = data.array
			self.rawCapture.truncate(0)

		# If still null frame,
		if frame is None:
			raise TEInvalidFrameException()

		# resize the frame
		frame = imutils.resize(frame, width=self.FRAME_WIDTH)

		return frame

	def release(self):
		if self.video_file is not None:
			self.video_file.release()
		elif self.camera is not None:
			# Pycamera may not have the release function
			if hasattr(self.camera, 'release'): 
				self.camera.release()

class TEVideoWriter:
	def __init__(self):
		self.filename = None
		self.video_writer = None

	def open(self, filename):
		# it defers the actual file open operation,
		# since we don't know yet actual frame size
		self.filename = filename
		
		if not self.filename.endswith(".avi"):
			self.filename += ".avi"

	def isopened(self):
		return self.filename is not None

	def record(self, frame):
		if not self.isopened(): # If not openned, do nothing
			return

		if self.video_writer is None: # create interface here
			(h, w) = frame.shape[:2]
			fourcc = cv2.VideoWriter_fourcc(*'MJPG')
			self.video_writer = cv2.VideoWriter(self.filename, fourcc, 20, (w,h), True)

		self.video_writer.write(frame)

	def release(self):
		if self.video_writer is not None:
			self.video_writer.release()

