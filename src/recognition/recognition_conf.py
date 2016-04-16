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
NEGLECT_SHADOW = True
FILTER_NOISE_SIZE = (2,2)
GAP_FILLING_METHOD = GapFillingMethod.MEDIAN
MIN_OBJECT_AREA = 150 # Note: It is strongly related to the frame size.

# Tracking heuristic related
RECENT_FRAMES_TO_TRACK = 4 
