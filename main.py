import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

sock_idle = True

while True:
  data, _addr = sock.recvfrom(1024) # buffer size is 1024 bytes
  if sock_idle:
    if data[0] == 36:
      sock_idle = False
    else:
      print(data[0])
  
  else:
    axes = []
    if (data[0] == 35):
      sock_idle = True

    else:
      for i in range(6):
        msb = data[i*2]
        lsb = data[(i*2)+1]
        axes.append((msb << 8) + lsb)

      print(axes)