import socket

s = socket.socket()
host = socket.gethostname()
port = 9999

address = (host, port)

s.connect(address)
while(1):
	msg = raw_input()
	if len(msg) > 1024:
		print("Error: Message too large")
		continue
	s.send(msg)
