import DriveSupport
import socket
from constants import *


serialNumbers = ["205435783056", "206535823056", "207535863056"]
sock_idle = True
last_axes = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

support = DriveSupport.ConnectToDrive(serialNumbers)

def parse(data):
  global last_axes
  axes = [0, 0, 0, 0, 0, 0]

  try:
    for i in range(6):
      raw_axis = data.split(b'&')[i]
      val = float(raw_axis)
      val = val + (TOTAL_LENGTH / 2)
      val = val / BALL_SCREW_PITCH
      axes[i] = val
    last_axes = axes

  except:
    axes = last_axes

  return axes

def loop():
  global sock_idle
  data, _addr = sock.recvfrom(1024) # buffer size is 1024 bytes
  
  if sock_idle:
    if data == b'START':
      print("Start!")
      sock_idle = False

  else:
    if data == b'STOP':
      print("Stop!")
      sock_idle = True
      return
    
    axes = parse(data)

    for i in range(6):
      try:
        odrv_axes[i].controller.input_pos = axes[i]
      except:
        odrv_axes[i].controller.input_pos = last_axes[i]
    # print(axes)

if __name__ == "__main__":

  odrv0, odrv1, odrv2 = support.begin(FEEDRATE)
  
  odrv_axes = [
    odrv0.axis0,
    odrv0.axis1,
    odrv1.axis0,
    odrv1.axis1,
    odrv2.axis0,
    odrv2.axis1
  ]

  while True:
    loop()