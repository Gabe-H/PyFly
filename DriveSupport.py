import odrive
from odrive.enums import *
import json
import time


class ConnectToDrive():
    # Establish connection to ODrives based on serial number(s)
    def __init__(self):
        with open('config.json') as f:
            self.serialNumbers = json.load(f)['serial_numbers']

    def Connect(self):
        drives = []  # Init array of drives
        for i in range(len(self.serialNumbers)):
            print('Searching for ODrive...')
            drives.append(
                odrive.find_any(serial_number=self.serialNumbers[i])
            )
            print(
                f'ODrive #{self.boardNumber(drives[i].serial_number)} ({drives[i].serial_number}) connected.')

        return drives

    # Set parameters to a given odrive
    def SetODriveParams(self, drive, config):
        # Brake resistor
        drive.config.enable_brake_resistor = config['enable_brake_resistor']
        drive.config.brake_resistance = config['brake_resistance']
        drive.config.dc_max_negative_current = config['dc_max_negative_current']

        # Endstop configuration
        drive.axis0.min_endstop.config.gpio_num = config['min_endstop_axis0']['gpio_num']
        drive.axis0.min_endstop.config.is_active_high = config[
            'min_endstop_axis0']['is_active_high']
        drive.axis0.min_endstop.config.enabled = config['min_endstop_axis0']['enabled']
        drive.axis0.min_endstop.config.offset = config['min_endstop_axis0']['offset']

        drive.axis1.min_endstop.config.gpio_num = config['min_endstop_axis1']['gpio_num']
        drive.axis1.min_endstop.config.is_active_high = config[
            'min_endstop_axis1']['is_active_high']
        drive.axis1.min_endstop.config.enabled = config['min_endstop_axis1']['enabled']
        drive.axis1.min_endstop.config.offset = config['min_endstop_axis1']['offset']

        # Encoder pin config
        gpio_modes = [drive.config.gpio1_mode, drive.config.gpio2_mode, drive.config.gpio3_mode,
                      drive.config.gpio4_mode, drive.config.gpio5_mode, drive.config.gpio6_mode, drive.config.gpio7_mode, drive.config.gpio8_mode]

        gpio_modes[config['min_endstop_axis0']
                   ['gpio_num'] - 1] = GpioMode.DIGITAL_PULL_UP
        gpio_modes[config['min_endstop_axis1']
                   ['gpio_num'] - 1] = GpioMode.DIGITAL_PULL_UP

        print(
            f'\tODrive #{self.boardNumber(drive.serial_number)} parameters set.')

    # Set parameters to both axes of a drive
    def SetAxesParams(self, drive, config):
        # Set to POS_FILTER so that we can use the 'input_filter_bandwidth' option later
        axes = [drive.axis0, drive.axis1]
        for i in range(2):
            axis = axes[i]  # Get axis

            axis.controller.config.input_mode = InputMode.POS_FILTER

            # Axis controller and motor configuration
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
            print(
                f'\tODrive #{self.boardNumber(drive.serial_number)} Axis{i} parameters set.')

    # Open config file and apply settings to the axes of the specified ODrive
    def ConfigureBoards(self, drives):
        with open('config.json') as f:
            data = json.load(f)

            for drive in drives:
                print(
                    f'Configuring ODrive #{self.boardNumber(drive.serial_number)}...')
                self.SetODriveParams(drive, data['odrive_config'])
                self.SetAxesParams(drive, data['motor_config'])

                # Clear any existing errors to start in a stable state
                # Changing certain settings (such as enabling the brake resistor) will leave the ODrive in an errored state until
                # we either reboot the entire ODrive (which I would like to do but haven't been able to do without crashing the
                # entire Python script) or call drive.clear_errors(). This *will* clear any legitimate errors too but hopefully
                # any actual errors will just reappear as soon as we try to move the motors.
                drive.clear_errors()

    def MotorCalibration(self, drive):
        axes = [drive.axis0, drive.axis1]
        for i in range(2):
            axis = axes[i]  # Get axis

            axis.requested_state = AxisState.MOTOR_CALIBRATION

            self.waitForIdle(axis)

            if (axis.error != 0):
                print(
                    f'ERROR (AxisError.{AxisError(axis.error).name}) occurred during motor calibration (ODrive #{self.boardNumber(drive.serial_number)} Axis{i}))')
                return

            axis.motor.config.pre_calibrated = True

            print(
                f'Motor calibration complete (ODrive #{self.boardNumber(drive.serial_number)} Axis{i})')

    # Function to be called once "ever" to configure the encoder and index offsets
    def EncoderIndexCalibration(self, drive):
        axes = [drive.axis0, drive.axis1]
        for i in range(2):
            axis = axes[i]  # Get axis

            axis.encoder.config.use_index = True

            # Custom ramping/velocity control during calibration
            # axis.config.calibration_lockin.vel = 1
            # axis.config.calibration_lockin.accel = 0
            # axis.config.calibration_lockin.ramp_distance = 0.5

            axis.requested_state = AxisState.ENCODER_INDEX_SEARCH
            self.waitForIdle(axis)

            axis.requested_state = AxisState.ENCODER_OFFSET_CALIBRATION
            self.waitForIdle(axis)

            if (axis.error != 0):
                print(
                    f'ERROR (AxisError.{AxisError(axis.error).name}) occurred during encoder calibration (ODrive #{self.boardNumber(drive.serial_number)} Axis{i}))')
                return

            if (abs(axis.encoder.config.direction) != 1):  # Should be 1 or -1
                print(
                    f'Encoder direction not set correctly (ODrive #{self.boardNumber(drive.serial_number)} Axis{i}))')
                return

            axis.encoder.config.pre_calibrated = True

            print(
                f'Encoder index calibration complete (ODrive #{self.boardNumber(drive.serial_number)} Axis{i})')

    def EnableAutomaticStartup(self, drive, state=True):
        axes = [drive.axis0, drive.axis1]
        for i in range(2):
            axis = axes[i]  # Get axis

            axis.config.startup_encoder_index_search = state
            axis.config.startup_homing = state
            axis.config.startup_closed_loop_control = state

            print(
                f'ODrive #{self.boardNumber(drive.serial_number)} Axis{i} automatic startup: {"Enabled" if state else "Disabled"}')

    def waitForIdle(self, axis):
        while axis.current_state != AxisState.IDLE:
            time.sleep(0.1)

    def boardNumber(self, serialNumber):
        return self.serialNumbers.index(hex(serialNumber)[2:].upper()) + 1
