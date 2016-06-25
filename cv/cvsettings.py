# Camera parameters
AWB_MODE = 'off'
# AWB_MODE choices: 'off','auto','sunlight','cloudy','shade','tungsten','fluorescent','incandescent','flash','horizon'
EXPOSURE_MODE = 'off'
# Exposure mode choices: 'off','auto','night','nightpreview','backlight','spotlight','sports','snow','beach','verylong','fixedfps','antishake','fireworks'

AWB_GAINS = (1.4, 2.2) # If too green/pink  adjust this (pink, green)
SATURATION = 10 #
EXPOSURE_COMPENSATION = 0
SHUTTER = 85000  # measured in picoseconds?
VIDEO_STABALIZATION = True
ROTATION = 0
CAMERA_WIDTH = 1088
CAMERA_HEIGHT = 480
ISO = 0
CONTRAST = 0
BRIGHTNESS = 60
PROP_FORMAT = 1

# Thresholding parameters
BLUE_HSV_RANGE = [([80, 60, 65], [125, 105, 125])]  # [([30, 30, 60], [80, 80, 90])]
YELLOW_HSV_RANGE = [([20, 20, 120], [50, 100, 180])]  # [([25, 230, 230], [50, 255, 255])]

HEIGHT_PADDING_BOTTOM = int(CAMERA_HEIGHT / 1.55) # Where the bottom image ROI is gonna ba
HEIGHT_PADDING_TOP = int(CAMERA_HEIGHT / 1.8) # Where the top image ROI is gonna be

WIDTH_PADDING = 0

IMG_ROI_HEIGHT = 20

FRAMES = 100  # How many frames to do CV for
