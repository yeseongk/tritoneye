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

# Tracking algorithm related
NUM_FRAMES_TO_TRACK_PATH = 30
NUM_FRAMES_TO_REMOVE_OBJECTS = 5
NUM_FRAMES_TO_CONFIRM_OBJECTS = 5
