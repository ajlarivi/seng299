import sys
import socket
import thread
import select
import getpass

clientSocket = socket.socket()
host = socket.gethostname()
port = 9999

address = (host, port)

clientSocket.connect(address)

while (1):
	readList = [sys.stdin, clientSocket]
	sockets, empty1, empty2 = select.select(readList, [], [])
	for sock in sockets:
		if sock == clientSocket:
			data = sock.recv(1024)
			if data:
				print(data)
		else:
			msg = getpass.getpass("")
			clientSocket.send(msg)
