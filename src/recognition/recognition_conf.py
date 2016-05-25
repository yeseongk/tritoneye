# Configuration for recognition algorithms

# Option definitions
class BackgroundSubtractor:
	MOG = 0
	MOG2 = 1
	GMG = 2

class GapFillingMethod:
	MEDIAN = 0
	BILATERAL = 1

class DetectionMethod:
	OBJECT_TRACK = 0
	AREA_TRACK = 1

# --------------------------------------------------
# Tracking method
DETECTION_METHOD = DetectionMethod.OBJECT_TRACK
#DETECTION_METHOD = DetectionMethod.AREA_TRACK

# Image processing algorithm related
BG_SUBTRACTOR = BackgroundSubtractor.MOG2
NEGLECT_SHADOW = True
FILTER_NOISE_SIZE = (2,2)
GAP_FILLING_METHOD = GapFillingMethod.MEDIAN
MIN_OBJECT_AREA = 300 # Note: It is strongly related to the frame size.
MAX_OBJECT_AREA = 40000 # Note: It is strongly related to the frame size.
CHECK_SUDDEN_CHANGE = True
SUDDEN_CHANGE_AREA = 15000 # See verify_sudden_change function

# Tracking algorithm related
NUM_FRAMES_TO_TRACK_PATH = 30
NUM_FRAMES_TO_REMOVE_OBJECTS = 5
NUM_FRAMES_TO_CONFIRM_OBJECTS = 5
MAX_RATIO_OF_AREA_CHANGE = 0.5

# Line counting algorithm related
USE_DEFAULT_DIRECTION_COUNTING = True
DIRECTION_RELATIVE_POSITION = 0.35
MIN_DISTANCE_ON_LINE = 5
MIN_DISTANCE_CLOSE_TO_LINE = 10

# Area based counting algorithm
TARGET_AREA = ((70, 31), (259, 92))
OCCUPIED_RATIO = 0.1
OCCUPANCY_HISTORY_LEN = 15
MIN_REPORT_INTERVAL = 15
MIN_NOISY_INTERVAL = 12 # around two seconds
SUDDEN_CHANGE_RATIO = 0.5
SUBSAMPLING_SCALE = 4 



