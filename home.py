import time
from odrive.enums import *
import DriveSupport
from constants import *


# serialNumbers = ['205435783056', '206535823056', '207535863056']
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


for odrv in support.drives:
    requestAxisStates(odrv, AXIS_STATE_FULL_CALIBRATION_SEQUENCE)
print('Calibrating')

time.sleep(1)

waitForIdle()

for odrv in support.drives:
    requestAxisStates(odrv, AXIS_STATE_CLOSED_LOOP_CONTROL)


for odrv in support.drives:
    incAxes(odrv, 1)

input('Remove actuator blocks, then press enter')

# print('Move motors until they are near level with each other')
# while True:
#     move_cmd = input('Enter axis (cancel: x): ')
#     if move_cmd == 'x':
#         print('Offset quit')
#         break

#     drive_cmd = int(move_cmd)
#     if drive_cmd < 0 and drive_cmd > 2:
#         print('Invalid drive index')
#         continue

#     while True:
#         inc = 0
#         move_inc = input('Increment (+/-/x): ')
#         if move_inc == 'x':
#             break
#         inc += move_inc.count('+')
#         inc -= move_inc.count('-')
#         incAxes(support.drives[drive_cmd], inc)

for odrv in support.drives:
    requestAxisStates(odrv, AXIS_STATE_HOMING)
print('Homing...')

waitForIdle()

for odrv in support.drives:
    requestAxisStates(odrv, AXIS_STATE_CLOSED_LOOP_CONTROL)
print('Axes at 0')

for odrv in support.drives:
        odrv.axis0.controller.config.input_filter_bandwidth = 1000/(INTERVAL_LOOPS*2)
        odrv.axis1.controller.config.input_filter_bandwidth = 1000/(INTERVAL_LOOPS*2)

print('Done')