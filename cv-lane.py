print("Initialising...")

import RPi.GPIO as GPIO # Import the GPIO library
GPIO.setmode(GPIO.BOARD) # Required to setup the naming convention
GPIO.setwarnings(False) # Ignore annoying warnings
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Arming pin is input
GPIO.setup(40, GPIO.OUT) # LED pin is output
GPIO.output(40, 1) # Set LED pin to "high" or on

from cv.EyeCanSee import *
from ai.pid import *
from ai.KalmanFilter import *
from controller.controllers import *
import cv2
import math
import time
import cv.settings
import commands
import os
import sys
import threading

output = commands.getoutput('ps -A')
if 'servod' in output:
    print("Servo Blaster process found.")
else:
    print("Servo Blaster process not found. Starting it now.")
    os.system("echo terminator | sudo service servoblaster start")

def map_func(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# Our class instances
camera = EyeCanSee()

# Kalman filter
measurement_standard_deviation = 0
process_variance = 10
estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
kalman_filter = {}

# previous values (in case can't detect line)
# we'll go and continue previous location
previous_values = {}

# PID for each region (if we do decide to add any)
p_ = {'top': 0.02, 'middle': 0.025, 'bottom': 0.185}
i_ = {'top': 0.011, 'middle': 0.027, 'bottom': 0.040}
d_ = {'top': 0.015, 'middle': 0.042, 'bottom': 0.82}
pid = {}

for region in settings.REGIONS_KEYS:
    pid[region] = PID(p=p_[region], i=i_[region], d=d_[region], integrator_max=50, integrator_min=-50)
    previous_values[region] = 0.0
    kalman_filter[region] = KalmanFilter(process_variance, estimated_measurement_variance)

# Controllers
motor = MotorController() # values: -100 <= x <= 100
steering = ServoController() # values: 0 <= x <= 100

motor.stop()
steering.straighten()

# Wait for the switch to be "armed" before starting
# (and blink the LED rapidly so we know)
print("Initialisation complete.")
if (GPIO.input(11) == 1):  
    print("Start the CV by turning the arming switch on.")
    
while(GPIO.input(11) == 1):
    GPIO.output(40, 1)
    time.sleep(0.1)
    GPIO.output(40, 0)
    time.sleep(0.25)

for i in range(0,5):
    GPIO.output(40, 1)
    time.sleep(0.1)
    GPIO.output(40, 0)
    time.sleep(0.25)
    
def status():
    global t
    sys.stdout.write('\r')
    sys.stdout.write(" ")
    sys.stdout.flush()
    t = threading.Timer(1, status).start()
    
status() # Start the first "thread" for blinking dot
time.sleep(0.5) # Leave a 0.5 second delay so it alternates (ie blinks)

def status2():
    global t2
    sys.stdout.write('\r')
    sys.stdout.write(".")
    sys.stdout.flush()
    t2 = threading.Timer(1, status2).start()
    
status2() # start the second "thread" for blinking dot

motor.run_speed(35) # Start moving forward
#camera.debug = True # Show a live view of the video and CV

for i in range(0, settings.FRAMES): # For the amount of frames we want CV on
    while(GPIO.input(11) == 1):
        motor.stop() # Reset throttle
        steering.straighten() # Reset steering
    
    camera.where_lane_be() # Trys and get our lane

    # Pid on each region
    total_pid = 0
    for region in camera.relative_error:
        # If it detects lane, then use that region. Otherwise, use previous value
        if camera.detected_lane[region]:
            # Filters out irregular values
            kalman_filter[region].input_latest_noisy_measurement(camera.relative_error[region])
            filtered_value = kalman_filter[region].get_latest_estimated_measurement()

            # Add pid to previous value and total_pid value
            previous_values[region] = filtered_value
            total_pid += pid[region].update(filtered_value)
        else:
            total_pid += previous_values[region]

    # Negative total_pid = need to turn left
    # Positive total_pid = need to turn right
    # Try to keep pid 0
    if total_pid < 0:
        if total_pid < -100:
            total_pid = -100
        steering.turn_left(abs(total_pid))

    elif total_pid > 0:
        if total_pid > 100:
            total_pid = 100
        steering.turn_right(abs(total_pid))
    
    #Motors slow down around bends
    motor_speed = map_func(abs(total_pid), 0, 100, 20, 35)
    motor.run_speed(motor_speed)

    time.sleep(0.01)
    
#Turn everything off now that we're done and exit the program
steering.straighten()
motor.stop()
GPIO.output(40, 0) #LED
print("Finished running CV.  Now exiting the program.")
os.system('kill $PPID') #Kill the threads from the blinking dot