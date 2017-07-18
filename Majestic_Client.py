import sys
import socket
import threading
from threading import Thread
import select

clientSocket = socket.socket()
host = socket.gethostname()
port = 9999

address = (host, port)

clientSocket.connect(address)

def recv_msg(clientSocket):
	while True:
		data = clientSocket.recv(1024)
		if data:
			print(data)

def send_msg(clientSocket):
	while True:
		msg = raw_input()
		clientSocket.send(msg)


t1=threading.Thread(target=recv_msg,args=(clientSocket,))
t1.setDaemon(True)
t1.start()

t2=threading.Thread(target=send_msg,args=(clientSocket,))
t2.setDaemon(True)
t2.start()

while True:
	pass
