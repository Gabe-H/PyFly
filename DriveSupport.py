import odrive
from odrive.enums import *
import json, time

class ConnectToDrive():

    # Establish connection to ODrives based on serial number(s)
    def __init__(self):
        with open('config.json') as f:
            self.serialNumbers = json.load(f)['serial_numbers']

        self.drives = [] # Init array of drives
        for i in range(len(self.serialNumbers)):
            print('Searching for ODrive...')
            self.drives.append(self.DetermineParameters(odrive.find_any(serial_number=self.serialNumbers[i])))
            print(f'({i + 1}/{len(self.serialNumbers)}) ODrives Connected...')
        
        print(f'\n{len(self.drives)} connected\n')

    # Set parameters to a given odrive
    def SetODriveParam(self, drive, config):
        drive.config.enable_brake_resistor = config['enable_brake_resistor']
        drive.config.brake_resistance = config['brake_resistance']
        print(drive.config.dc_max_negative_current)
        print(type(drive.config.dc_max_negative_current))

        drive.config.dc_max_negative_current = config['dc_max_negative_current']

        print(drive.config.dc_max_negative_current)
        print(type(drive.config.dc_max_negative_current))

	
        print(f'ODrive settings set.')

    # Set parameters to a given axis
    def SetAxisParam(self, axis, config):
        axis.controller.config.pos_gain = config['pos_gain']
        axis.controller.config.vel_gain = config['vel_gain']
        axis.controller.config.vel_integrator_gain = config['vel_integrator_gain']
        axis.controller.config.vel_limit = config['vel_limit']
        axis.controller.config.input_filter_bandwidth = config['input_filter_bandwidth']
        axis.motor.config.current_lim = config['current_lim']
        axis.motor.config.pole_pairs = config['pole_pairs']
        axis.motor.config.torque_constant = 8.27 / config['motor_kv']
        axis.motor.config.motor_type = config['motor_type']
        axis.encoder.config.cpr = config['encoder_cpr']

        print(f'Motor settings set.')

    # Open config file and apply settings to the axes of the specified ODrive
    def DetermineParameters(self, drive):
        with open('config.json') as f:
            data = json.load(f)
            self.SetODriveParam(drive, data['odrive_config'])
            self.SetAxisParam(drive.axis0, data['motor_config'])
            self.SetAxisParam(drive.axis1, data['motor_config'])

        return drive
    
    # Can be used to make calibration quicker; do not calibrate anything that's already been calibrated
    def DetermineAxisState(self, motor_ready, enc_ready):
        if motor_ready and enc_ready:
            return AxisState.IDLE
        if motor_ready and not(enc_ready):
            return AxisState.ENCODER_OFFSET_CALIBRATION
        if not(motor_ready) and enc_ready:
            return AxisState.MOTOR_CALIBRATION
        return AxisState.FULL_CALIBRATION_SEQUENCE

    # Calibrate specified axis of ODrive.
    # `force_full_calibration` can be enabled to calibrate the axis using FULL_CALIBRATION (motor and encoder)
    def CalibrateAxis(self, axis, force_full_calibration=False):
        if (force_full_calibration):
            axis.requested_state = AxisState.FULL_CALIBRATION_SEQUENCE
        else:
            axis.requested_state = self.DetermineAxisState(axis.motor.is_calibrated, axis.encoder.is_ready)

    # Start the library. Calibrate motors, then configure the control mode
    # Returns a tuple of the calibrated drives.
    def begin(self, feedrate):
        print('Starting calibration...')
        for i in range(len(self.drives)):
            drive = self.drives[i]
            print(f'Calibrating ({i+1}/{len(self.drives)})')
            self.CalibrateAxis(drive.axis0)
            self.CalibrateAxis(drive.axis1)
        
        # Wait for all axes to be idle after homing
        while True:
            drivesNotCalibrated = 0
            for drive in self.drives:
                if drive.axis0.current_state != AxisState.IDLE or drive.axis1.current_state != AxisState.IDLE:
                    drivesNotCalibrated += 1
            if drivesNotCalibrated == 0:
                break
            time.sleep(0.1)

        # Let the boards settle for a second
        time.sleep(1)
            
        for drive in self.drives:
            # Set the controller to use the encoder for closed loop feedback
            drive.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            drive.axis1.requested_state = AxisState.CLOSED_LOOP_CONTROL
            # Set the input mode to position control
            drive.axis0.controller.config.input_mode = InputMode.POS_FILTER
            drive.axis1.controller.config.input_mode = InputMode.POS_FILTER
            # Set the feedrate as requested
            drive.axis0.controller.config.input_filter_bandwidth = feedrate
            drive.axis1.controller.config.input_filter_bandwidth = feedrate

        return tuple(self.drives)

    # Set motors to idle
    def Stop(self):
        drives = self.drives
        for drive in drives:
            drive.axis0.requested_state = AxisState.IDLE
            drive.axis1.requested_state = AxisState.IDLE
        
        print('Drives idle')
