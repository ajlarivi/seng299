import socket
import thread
import select
import time

class ClientInfo:

    def __init__(self, clientAddress, startingRoom):
        print("New client added with address %s and room %s" % (clientAddress, startingRoom.getRoomName()))
        self.address = clientAddress
        self.alias = clientAddress
        self.room = startingRoom

    def getAddress(self):
        return self.address

    def getAlias(self):
        return self.alias

    def getRoom(self):
        return self.room

    def setAlias(self, newAlias):
        self.alias = newAlias

    def setRoom(self, newRoom):
        self.room = newRoom


class Room:

    def __init__(self, roomName, roomCreator):
        self.name = roomName
        self.creator = roomCreator
        self.users = [roomCreator]
        self.blockedUsers = []

    def addUser(self, userAlias):
        self.users.append(userAlias)
        return userAlias

    #we were missing this bad boy in the design docs
    def removeUser(self, userAlias):
        self.users.remove(userAlias)
        return userAlias

    #also this bad boy
    def blockUser(self, userALias):
        self.removeUser(userAlias)
        self.blockedUsers.append(userAlias)
        return userAlias

    #oh and this guy
    def unblockUser(self, userAlias):
        self.blockedUsers.remove(userAlias)
        return userAlias

    def getUsers(self):
        return self.users

    def getBlockedUsers(self):
        return self.blockedUsers

    def getRoomName(self):
        return self.name

    def getCreator(self):
        return self.creator


class textHandler:
    def interpretMessage(self, msg, user): #added message and user parameter
        if msg.startswith("/"):
            #message is a command
            msgSplit = msg.split()
            if msgSplit[0] == "/join":
                self.joinChat(msgSplit[1], user) #just realized this passes in  a string and the function expects a room object, we will probably have to add a global list of rooms and users so we can check if the string passed is a valid user and then pass in that object

            elif msgSplit[0] == "/leave":
                self.joinChat(general, user)

            elif msgSplit[0] == "/create":
                self.createRoom(user, msgSplit[1])

            elif msgSplit[0] == "/delete":
                self.deleteRoom(user, msgSplit[1]) #same problem as above

            elif msgSplit[0] == "/set_alias":
                self.setAlias(msgSplit[1], user)

            elif msgSplit[0] == "/block_user": #and again here
                self.blockUser(user, msgSplit[1], msgSplit[2])

            elif msgSplit[0] == "/unblock_user": #and here
                self.unblockUser(user, msgSplit[1], msgSplit[2])

            else:
                halp()
        else:
            sendMessage(msg, user.getRoom())

    def sendMessage(self, msg, currRoom):
        pass #socket shit, send a standard message

    def joinChat(self, room, user):
        user.getRoom.removeUser(user)
        room.addUser(user)
        user.setRoom(room)
        print(user.getAlias() + " joined " + room.getRoomName())

    def setAlias(self, newAlias, user):
        print(user.getAlias() + " changed their alias to " + newAlias)
        user.setAlias(newAlias) #do we want to add something to check for duplicate alias's?

    def blockUser(self, blockingUser, blockedUser, room): #added the room parameter
        if blockingUser == room.getCreator():
            room.blockUser(blockedUser)
            if blockedUser.getRoom() == room:
                blockedUser.setRoom(general)
            print(blockingUser.getAlias() + " blocked " + blockedUser.getAlias() + " from " + room.getRoomName())
        else:
            print("ERROR: " + blockingUser.getAlias() + " attempted to block " + blockedUser.getAlias() + " from " + room.getRoomName() + " but is not the creator of the room")

    def unblockUser(self, unblockingUser, unblockedUser, room): #added the room parameter
        if unblockingUser == room.getCreator():
            room.unblockUser(unblockedUser)
            print(unblockingUser.getAlias() + " unblocked " + unblockedUser.getAlias() + " from " + room.getRoomName())
        else:
            print("ERROR: " + unblockingUser.getAlias() + " attempted to unblock " + unblockedUser.getAlias() + " from " + room.getRoomName() + " but is not the creator of the room")

    def createRoom(self, creatingUser, roomName):
        roomName = Room(roomName, creatingUser) #this does not feel right, how does python even work?
        return roomName

    def deleteRoom(self, deletingUser, room): #changed from roomName to room as it will be the actual room object
        if deletingUser == room.getCreator():
            print(deletingUser.getAlias() + " deleted their room " + room.getRoomName() + ", moving all current users to general...")
            for user in room.users:
                self.joinChat(general, user) #this smells real bad as well, removing users from the list as you iterate over it and also just a weird nesting of calls
            del room
        else:
            print("ERROR: " + deletingUser.getAlias() + " attempted to delete the room " + room.getRoomName() + " but is not the creator of the room")

    def halp(self):
        print("ya done fucked up")
        pass

class RequestHandler:

    def __init__(self, clientList, roomList):
        self.listOfClients = clientList
        self.listOfRooms = roomList

    def handleRequest(self):
        pass

def add_users(soket_obj, user_list):
    while(1):
        client, addr = server_socket.accept()
        new_client = ClientInfo([client, addr], generalRoom)
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

generalRoom = Room('general', 'default')

thread.start_new_thread(add_users, (server_socket, socket_list))

while True:

    for sockets in socket_list:
        try:
            sockets.setblocking(0)
            data = sockets.recv(1024)
            sockets.setblocking(1)
            if data > 0:
                for x in client_list:
                    if x[0] == sockets:
                        print('%s:%s says: %s' % (x[1][0], x[1][1], data))

        except socket.error:
            pass
            
        except:
            sockets.close()
            socket_list.remove(sockets)
            for x in client_list:
                    if x[0] == sockets:
                        client_list.remove(x)
