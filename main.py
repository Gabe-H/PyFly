import time

from odrive.enums import *
import DriveSupport
import socket
from constants import *


# serialNumbers = ["205435783056", "206535823056", "207535863056"]
serialNumbers = ["206535823056", "205435783056", "207535863056"]
sock_idle = True
last_axes = []
last_time = time.time()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

support = DriveSupport.ConnectToDrive(serialNumbers)

def parse(data):
  global last_axes
  axes = [0, 0, 0, 0, 0, 0]

  for i in range(6):
    raw_axis = data.split(b'&')[i]
    val = float(raw_axis)
    val = val + (TOTAL_LENGTH / 2)
    val = val / BALL_SCREW_PITCH
    axes[i] = val
  last_axes = axes

  return axes

def moveToMid(rate):
  for axis in odrv_axes:
    axis.controller.config.input_filter_bandwidth = 0.5
  for axis in odrv_axes:
    axis.controller.input_pos = 40
  for axis in odrv_axes:
    axis.controller.config.input_filter_bandwidth = rate

def loop():
  global sock_idle, last_time
  data, _addr = sock.recvfrom(128) # buffer size is 1024 bytes
  
  if sock_idle:
    if data == b'START':
      print("Start!")
      for i in range(6):
        odrv_axes[i].requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
      sock_idle = False

  else:
    if data == b'STOP':
      print("Stop!")
      sock_idle = True
      for axis in odrv_axes:
        axis.controller.config.input_filter_bandwidth = 0.1
      for axis in odrv_axes:
        axis.controller.input_pos = 0
      for axis in odrv_axes:
        axis.controller.config.input_filter_bandwidth = 1000/(INTERVAL_LOOPS*2)
      time.sleep(5)
      for axis in odrv_axes:
        axis.requested_state = AXIS_STATE_IDLE

      return
    
    axes = parse(data)

    for i in range(6):
      if (axes[i] >=0) and (axes[i] <= TOTAL_LENGTH/BALL_SCREW_PITCH):
        odrv_axes[i].controller.input_pos = axes[i]
    
    now = time.time()
    time.sleep(0.01)
    print("Loop time: ", now-last_time)
    last_time = now

if __name__ == "__main__":
  odrv0, odrv1, odrv2 = support.begin(1000/(INTERVAL_LOOPS*2))
  
  odrv_axes = [
    odrv0.axis0,
    odrv0.axis1,
    odrv1.axis0,
    odrv1.axis1,
    odrv2.axis0,
    odrv2.axis1
  ]
  moveToMid(1000/(INTERVAL_LOOPS*2))
  
  done = False
  while not done:
    print("Are all motors centered? (y/n): ")
    a = input()
    if (a=='y') or (a=='Y'):
      done = True
    elif (a=='n') or (a=='N'):
      done = False
    else:
      print("Invalid response, try again")
      done = False 

  print("Ready")
  while True:
    loop()