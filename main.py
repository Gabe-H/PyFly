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
support.MotorCalibration([d for d in drives])

# Run one-time encoder calibration. Saves values to board
support.EncoderIndexCalibration([d for d in drives])

# Enable automatic motor, encoder, homing, and closed loop control on startup
support.EnableAutomaticStartup([d for d in drives])

print('------------------------------------------')
print("-                                        -")
print("- !! MUST MANUALLY SAVE ODRIVE CONFIG !! -")
print("-                                        -")
print('------------------------------------------')
