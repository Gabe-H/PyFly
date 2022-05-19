import odrive
from odrive.enums import *
import json, time

class ConnectToDrive():
    def __init__(self, serialNumbers):
        self.drives = []
        for i in range(len(serialNumbers)):
            print('Searching for ODrive...')
            self.drives.append(self.DetermineParameters(odrive.find_any(serial_number=serialNumbers[i])))
            print(f'({i + 1}/{len(serialNumbers)}) ODrives Connected...')
        
        # for drive in self.drives:
        #     drive.save_configuration()
        
        print(f'\n{len(self.drives)} connected\n')

    def SetAxisParam(self, axis, pids):
        axis.controller.config.pos_gain = pids['pos_gain']
        axis.controller.config.vel_gain = pids['vel_gain']
        axis.controller.config.vel_integrator_gain = pids['vel_integrator_gain']
        axis.controller.config.vel_limit = pids['vel_limit']
        axis.motor.config.current_lim = pids["current_lim"]

        print(f'Motor settings set.')

    def DetermineParameters(self, drive):
        with open('config.json') as f:
            data = json.load(f)
            self.SetAxisParam(drive.axis0, data['pids'])
            self.SetAxisParam(drive.axis1, data['pids'])
        # with open(f'./motors.json') as f:
        #     data = json.load(f)
            # for setting in data:
                # if setting['serial'] == str(drive.serial_number):
                    # self.SetAxisParam(drive.axis0, setting['pids'][0])
                    # self.SetAxisParam(drive.axis1, setting['pids'][1])

        return drive
    
    def DetermineAxisState(self, motor_ready, enc_ready):
        if motor_ready and enc_ready:
            return AXIS_STATE_IDLE
        if motor_ready and not(enc_ready):
            return AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        if not(motor_ready) and enc_ready:
            return AXIS_STATE_MOTOR_CALIBRATION
        return AXIS_STATE_FULL_CALIBRATION_SEQUENCE

    def CalibrateAxis(self, axis):
        axis.requested_state = self.DetermineAxisState(axis.motor.is_calibrated, axis.encoder.is_ready)
        # axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE

    ## Will calibrate motors based on their current state
    def begin(self, feedrate):
        print('Starting calibration...')
        for i in range(len(self.drives)):
            drive = self.drives[i]
            print(f'Calibrating ({i+1}/{len(self.drives)})')
            self.CalibrateAxis(drive.axis0)
            self.CalibrateAxis(drive.axis1)
        
        while True:
            drivesNotCalibrated = 0
            for drive in self.drives:
                if drive.axis0.current_state != AXIS_STATE_IDLE or drive.axis1.current_state != AXIS_STATE_IDLE:
                    drivesNotCalibrated += 1
            if drivesNotCalibrated == 0:
                break
            time.sleep(0.1)

        time.sleep(1)
            
        for drive in self.drives:
            drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            drive.axis0.controller.config.input_mode = INPUT_MODE_POS_FILTER
            drive.axis1.controller.config.input_mode = INPUT_MODE_POS_FILTER
            drive.axis0.controller.config.input_filter_bandwidth = feedrate
            drive.axis1.controller.config.input_filter_bandwidth = feedrate

        return tuple(self.drives)

    def Stop(self):
        drives = self.drives
        for drive in drives:
            drive.axis0.requested_state = AXIS_STATE_IDLE
            drive.axis1.requested_state = AXIS_STATE_IDLE
        
        print('Drives idle')
