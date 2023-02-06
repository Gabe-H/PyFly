import time
from odrive.enums import *
import DriveSupport
from constants import *
#from odrive.utils import dump_errors

support = DriveSupport.ConnectToDrive()

# used to quickly request states on both odrive axes
def requestAxisStates(odrv, state):
    odrv.axis0.requested_state = state
    odrv.axis1.requested_state = state

# wait until all odrives have homed and are now idle
def waitForIdle():
    while True:
        drivesNotCalibrated = 0
        for odrv in support.drives:
            if odrv.axis0.current_state != AxisState.IDLE or odrv.axis1.current_state != AxisState.IDLE:
                drivesNotCalibrated += 1
        if drivesNotCalibrated == 0:
            print('All axes idle')
            break
        time.sleep(0.1)

# Increment the axes position
def incAxes(odrv, inc):
    odrv.axis0.controller.input_pos += inc
    odrv.axis1.controller.input_pos += inc

# Enable or disable the endstops
def setEndstops(enabled):
    for odrv in support.drives:
        for axis in [odrv.axis0, odrv.axis1]:
            axis.min_endstop.config.enabled = enabled

##########################
##     MAIN CONTROL     ##
##########################

# Disable the endstops before homing. Prevents endstop errors
# if the endstops are already depressed from the actuators being
# at zero.
setEndstops(False)
print('Endstops disabled')

time.sleep(1)

# Run setup on all odrive boards
drives = support.begin()

"""
# Request full calibration on all axes
for odrv in support.drives:
    requestAxisStates(odrv, AxisState.FULL_CALIBRATION_SEQUENCE)
print('Calibrating')

time.sleep(1)

# Wait until all axes are idle
waitForIdle()

# Enable closed loop control on all axes
for odrv in support.drives:
    requestAxisStates(odrv, AxisState.CLOSED_LOOP_CONTROL)

# Re-enable endstops
# setEndstops(True)
# print('Endstops enabled')
"""

#####################################################################
## !! This can be used to move the motors by keyboard before homing !!
""" # Comment or uncomment to disable or enable the code section
 input('Press enter to move motors by keyboard control')

 print('Move motors until they are near level with each other')
 while True:
     move_cmd = input('Enter axis (cancel: x): ')
     if move_cmd == 'x':
         print('Offset quit')
         break

     drive_cmd = int(move_cmd)
     # Catch bad controller selection
     if drive_cmd < 0 and drive_cmd > 2:
         print('Invalid drive index')
         continue

     while True:
         inc = 0
         move_inc = input('Increment (+/-/x): ')
         if move_inc == 'x':
             break
         inc += move_inc.count('+')
         inc -= move_inc.count('-')
         incAxes(support.drives[drive_cmd], inc)
# """ # Don't bother removing this line. It allows the opening block comment line to be enabled/disabled
#####################################################################

# Home all axes
# for odrv in support.drives:
    # requestAxisStates(odrv, AxisState.HOMING)
# print('Homing...')

# Wait until all motors are idle after homing
# waitForIdle()

# Re-enable closed loop control for actual simulator input
#for odrv in support.drives:
#    requestAxisStates(odrv, AxisState.CLOSED_LOOP_CONTROL)
#print('Axes at 0')

print('Done')
