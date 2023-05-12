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

for d in drives:

    # Run one-time motor calibration. Saves values to board
    support.MotorCalibration(d)

    # Run one-time encoder calibration. Saves values to board
    support.EncoderIndexCalibration(d)

    # Enable automatic motor, encoder, homing, and closed loop control on startup
    support.EnableAutomaticStartup(d)
    # support.EnableAutomaticStartup([d for d in drives], state=False)

print('------------------------------------------')
print("-                                        -")
print("- !! MUST MANUALLY SAVE ODRIVE CONFIG !! -")
print("-     use odrv#.save_configuration()     -")
print("-                                        -")
print('------------------------------------------')
