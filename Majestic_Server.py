import socket
import thread
import select

class ClientInfo:
    address
    alias
    room

    def __init__(self, clientAddress):


    def getAddress(self):
        return self.address

    def getAlias(self):
        return self.alias

    def getRoom(self):
        return self.room

    def setAlias(self, newAlias):
        self.alias = newAlias # Is this how Python works?
        pass

    def setRoom(self, newRoom):
        self.room = newRoom # I really hope this actually works
        pass


class Room:
    users
    blockedUsers
    name
    creator

    def __init__(self, roomName, roomCreator):
        self.name = roomName
        self.creator = roomCreator

    def addUser(self, userAlias):

    def getUsers(self):
        return users

    def getBlockedUsers(self):
        return blockedUsers

    def getRoomName(self):
        return name

    def getCreator(self):
        return creator


class textHandler:
    def interpretMessage(self):
        pass
    def sendMessage(self, msg, currRoom):
        pass
    def joinChat(self, room, user):
        pass
    def setAlias(self, newAlias, user):
        pass
    def blockUser(self, blockingUser, blockedUser):
        pass
    def unblockUser(self, unblockingUser, unblockedUser):
        pass
    def createRoom(self, creatingUser, roomName):
        pass
    def deleteRoom(self, deletingUser, roomName):
        pass
    def halp(self):
        pass

class RequestHandler:
    ClientList
    RoomList

    def handleRequest(self):
        pass

def add_users(soket_obj, user_list):
    while(1):
        client, addr = server_socket.accept()
        print("Client '", addr[0], "' added on port ", addr[1])
        socket_list.append(client)
        client_list.append([client, addr])

'''~~~~~~~~~~~~~~~~~~~~~MAIN~~~~~~~~~~~~~~~~~~~~~'''
server_socket = socket.socket()
host = socket.gethostname()
port = 9999

print('Starting Server...')
server_socket.bind((host, port))
server_socket.listen(5)
socket_list = []
client_list = []

thread.start_new_thread(add_users, (server_socket, socket_list))

while True:

    clients_with_sent_messages, empty, emptier = select.select(socket_list, [], [], 0.1)

    for existing_client in clients_with_sent_messages:
        try:
            data = existing_client.recv(1024)
            if data:
                for x in client_list:
                    if x[0] == existing_client:
                        print('%s:%s says: %s' % (x[1][0], x[1][1], data))

        except:
            existing_client.close()
            socket_list.remove(existing_client)
            for x in client_list:
                    if x[0] == existing_client:
                        client_list.remove(x)