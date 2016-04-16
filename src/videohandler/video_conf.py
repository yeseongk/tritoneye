# Configuration for video stream procedure

# Option definitions
class CameraType:
	PYCAMERA = 0
	PYCAMERA_ROBUST = 1 # Disable auto control feature
	WEBCAM = 2

# ----------------------------------------
DEF_FRAME_WIDTH = 300
DEF_FRAME_HEIGHT = 200

CAMERA_TYPE = CameraType.PYCAMERA_ROBUST
