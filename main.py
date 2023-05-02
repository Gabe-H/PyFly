import DriveSupport

# Initialize DriveSupport class
support = DriveSupport.ConnectToDrive()

# Connect to all drives
drives = support.Connect()

# Set parameters for all drives
support.ConfigureBoards(drives)


############################
## ONE TIME CONFIGURATION ##
############################

# Run one-time motor calibration. Saves values to board
support.MotorCalibration(drives[0])
support.MotorCalibration(drives[1])
support.MotorCalibration(drives[2])

# Run one-time encoder calibration. Saves values to board
support.EncoderIndexCalibration(drives[0])
support.EncoderIndexCalibration(drives[1])
support.EncoderIndexCalibration(drives[2])

# Enable automatic motor, encoder, homing, and closed loop control on startup
support.EnableAutomaticStartup(drives[0])
support.EnableAutomaticStartup(drives[1])
support.EnableAutomaticStartup(drives[2])

print('------------------------------------------')
print("-                                        -")
print("- !! MUST MANUALLY SAVE ODRIVE CONFIG !! -")
print("-                                        -")
print('------------------------------------------')
