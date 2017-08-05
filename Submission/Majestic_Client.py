'''=========================================='''
'''Logan Macdonald      loganm      V00832812'''
'''Scott Andreen        sandreen    V00816349'''
'''Andrew LaRiviere     ajlarivi    V00853200'''
'''Richard Cruikshank   rcruiksh    V00844041'''
'''=========================================='''

import sys
import socket
import thread
import select

helpMessage = '''Welcome to Majestic MesSENGer!

List of Valid Commands:

/join [chatroom_name] - joins the chatroom [chatroom_name]

/leave - leaves the current chatroom and join the general chatroom

/create [chatroom_name] - creates a chatroom with the name [chatroom_name] and moves you to this room, you can block and unblock users from this room as well as delete the room

/delete [chatroom_name] - deletes the chatroom [chatroom_name] and moves all users to the general chatroom if you are the creator of this chatroom

/set_alias [alias] - changes your alias displayed to other users. Maximum 15 characters

/block [user_alias] - blocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/unblock [user_alias] - unblocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/rooms - displays a list of active rooms

/help - displays this message\n'''

class client:
    def __init__(self):
        self.clientSocket = socket.socket()
        self.host = ''
        self.port = 9999
        self.address = (self.host, self.port)
        self.clientSocket.connect(self.address)

    def run(self):
        print helpMessage
        while (1):
        	readList = [sys.stdin, self.clientSocket]
        	sockets, empty1, empty2 = select.select(readList, [], [])
        	for sock in sockets:
        		if sock == self.clientSocket:
        			data = sock.recv(1024)
        			if data:
        				print(data)
        		else:
        			msg = raw_input()
        			self.clientSocket.send(msg)

clientObj = client()
clientObj.run()
