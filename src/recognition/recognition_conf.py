# Configuration for recognition algorithms

# Option definitions
class BackgroundSubtractor:
	MOG = 0
	MOG2 = 1
	GMG = 2

class GapFillingMethod:
	MEDIAN = 0
	BILATERAL = 1

# --------------------------------------------------
# Image processing algorithm related
BG_SUBTRACTOR = BackgroundSubtractor.MOG2
NEGLECT_SHADOW = False
FILTER_NOISE_SIZE = (2,2)
GAP_FILLING_METHOD = GapFillingMethod.MEDIAN
MIN_OBJECT_AREA = 100 # Note: It is strongly related to the frame size.
MAX_OBJECT_AREA = 40000 # Note: It is strongly related to the frame size.
SUDDEN_CHANGE_AREA = 15000 # See verify_sudden_change function

# Tracking algorithm related
NUM_FRAMES_TO_TRACK_PATH = 30
NUM_FRAMES_TO_REMOVE_OBJECTS = 5
NUM_FRAMES_TO_CONFIRM_OBJECTS = 5
MAX_RATIO_OF_AREA_CHANGE = 0.5

# Counting algorithm related
MIN_DISTANCE_ON_LINE = 10
MIN_DISTANCE_CLOSE_TO_LINE = 30
