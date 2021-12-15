import socket


UDP_IP = "127.0.0.1"
UDP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

sock_idle = True

while True:
  data, _addr = sock.recvfrom(1024) # buffer size is 1024 bytes
  axes = []
  for i in range(6):
    raw_axis = data.split(b'&')[i]
    cmd = raw_axis[0]
    val = float(raw_axis[1:])
    axes.append(val)

  print(axes)