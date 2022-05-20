import time
from odrive.enums import *
import DriveSupport
from constants import *


serialNumbers = ['206535823056', '205435783056', '207535863056']

support = DriveSupport.ConnectToDrive(serialNumbers)

def requestAxisStates(odrv, state):
    odrv.axis0.requested_state = state
    odrv.axis1.requested_state = state

def waitForIdle():
    while True:
        drivesNotCalibrated = 0
        for odrv in support.drives:
            if odrv.axis0.current_state != AXIS_STATE_IDLE or odrv.axis1.current_state != AXIS_STATE_IDLE:
                drivesNotCalibrated += 1
        if drivesNotCalibrated == 0:
            print('All axes IDLE')
            break
        time.sleep(0.1)

def incAxes(odrv, inc):
    odrv.axis0.controller.input_pos += inc
    odrv.axis1.controller.input_pos += inc

print('Setting to closed loop control')
for odrv in support.drives:
    requestAxisStates(odrv, AXIS_STATE_CLOSED_LOOP_CONTROL)

print('Moving to -39.5 (home is 40)')
for odrv in support.drives:
    odrv.axis0.controller.input_pos = -39.5
    odrv.axis1.controller.input_pos = -39.5