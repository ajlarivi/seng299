import socket
import thread
import select
import string

helpMessage = '''List of Valid Commands:

/join [chatroom_name] - join the chatroom [chatroom_name]

/leave [chatroom_name] - leave the chatroom [chatroom_name] and join the general chatroom

/create [chatroom_name] - creates a chatroom with the name [chatroom_name] and moves you to this room, you can block and unblock users from this room as well as delete the room

/delete [chatroom_name] - deletes the chatroom [chatroom_name] and moves all users to the general chatroom if you are the creator of this chatroom

/set_alias [alias] - changes your alias displayed to other users

/block [user_alias] - blocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/unblock [user_alias] - unblocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/help - displays this message\n'''

class ClientInfo:

    def __init__(self, clientSocketObj, address, startingRoom):

        self.socket_obj = clientSocketObj
        # address = (host, port)
        self.address = address
        self.alias = address[0] + ":" + str(address[1])
        self.room = startingRoom
        self.room.addUser(self)
        #print self.room.getUsers()

    def getAddress(self):
        return self.address

    def getSocketObj(self):
        return self.socket_obj

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
        #if roomCreator:
            #self.users = [roomCreator]
        #else:
        self.users = []
        self.blockedUsers = []

    def addUser(self, userAlias):
        self.users.append(userAlias)
        return userAlias

    #we were missing this bad boy in the design docs
    def removeUser(self, userAlias):
        if userAlias in self.users:
            self.users.remove(userAlias)
        return userAlias

    #also this bad boy
    def blockUser(self, userAlias):
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
            if len(msgSplit) == 2 or msgSplit[0] == "/leave":
                argValid = False
                if msgSplit[0] == "/join":
                    for room in room_list:
                        if room.getRoomName() == msgSplit[1]:
                            argValid = True
                            self.joinChat(room, user)
                            break
                    if not argValid:
                        feedbackMsg = "That room does not exist."
                        self.sendFeedback(feedbackMsg, user)

                elif msgSplit[0] == "/leave":
                    self.joinChat(generalRoom, user)

                elif msgSplit[0] == "/create":
                    for room in room_list:
                        if room.getRoomName() == msgSplit[1]:
                            feedbackMsg = "The room " + room.getRoomName() + " already exists"
                            self.sendFeedback(feedbackMsg, user)
                            return
                    self.createRoom(user, msgSplit[1])

                elif msgSplit[0] == "/delete":
                    for room in room_list:
                        if room.getRoomName() == msgSplit[1]:
                            argValid = True
                            self.deleteRoom(user, room)
                            break
                    if not argValid:
                        feedbackMsg = "that room does not exist"
                        self.sendFeedback(feedbackMsg, user)

                elif msgSplit[0] == "/set_alias":
                    self.setAlias(msgSplit[1], user)

                elif msgSplit[0] == "/block": #and again here
                    for robot in client_list:
                        if robot.getAlias() == msgSplit[1]:
                            argValid = True
                            self.blockUser(user, robot)
                            break
                    if not argValid:
                        feedbackMsg = "that alias is currently not in use"
                        self.sendFeedback(feedbackMsg, user)

                elif msgSplit[0] == "/unblock":
                    for robot in client_list:
                        if robot.getAlias() == msgSplit[1]:
                            argValid = True
                            self.unblockUser(user, robot, )
                            break
                    if not argValid:
                        feedbackMsg = "that alias is currently not in use"
                        self.sendFeedback(feedbackMsg, user)

                else:
                    self.halp(user)
            else:
                self.halp(user)
        else:
            self.sendMessage(msg, user)

    def sendFeedback(self, msg, user):
        user.getSocketObj().send(msg)

    def sendMessage(self, msg, user):
        destinationClients = user.getRoom().getUsers()
        msg = user.getAlias() + ": " + msg
        for robot in destinationClients:
            if robot == user:
                continue
            robot.getSocketObj().send(msg)


    def joinChat(self, room, user):
        if user not in room.blockedUsers:
            feedbackMsg = "You left " + user.getRoom().getRoomName()
            self.sendFeedback(feedbackMsg, user)
            roomMessage = "** Left the room. **"
            self.sendMessage(roomMessage, user)
            user.getRoom().removeUser(user)
            room.addUser(user)
            user.setRoom(room)
            print(user.getAlias() + " joined " + room.getRoomName())
            feedbackMsg = "You joined the chatroom " + room.getRoomName()
            self.sendFeedback(feedbackMsg, user)
            roomMessage = "** Joined the room **"
            self.sendMessage(roomMessage, user)
        else:
            print ("User " + str(user.getAddress()) + " attempted to join " + room.getRoomName() + " but is blocked.")
            feedbackMsg = "You attempted to join the chatroom " + room.getRoomName() + " but you are blocked from this room."
            self.sendFeedback(feedbackMsg, user)

    def setAlias(self, newAlias, user):
        for client in client_list:
            if newAlias == client.getAlias():
                print(user.getAddress(), " attempted to take the alias " + newAlias + " but it was taken by another user.")
                feedbackMsg = "The alias " + newAlias + " is taken by another user. Please choose another one."
                self.sendFeedback(feedbackMsg, user)
                return
        print(user.getAlias() + " changed their alias to " + newAlias)
        feedbackMsg = "You changed your alias to " + newAlias
        self.sendFeedback(feedbackMsg, user)
        roomMessage = "** Changed alias to " + newAlias + " **"
        self.sendMessage(roomMessage, user)
        user.setAlias(newAlias)


    def blockUser(self, blockingUser, blockedUser):
        if blockingUser == blockingUser.getRoom().getCreator():
            blockingUser.getRoom().blockUser(blockedUser)
            print(blockingUser.getAlias() + " blocked " + blockedUser.getAlias() + " from " + blockingUser.getRoom().getRoomName())
            feedbackMsg = "You blocked " + blockedUser.getAlias() + " from your current room."
            self.sendFeedback(feedbackMsg, blockingUser)
            blockedMsg = blockingUser.getAlias() + " blocked you from the chatroom " + blockingUser.getRoom().getRoomName()
            self.sendFeedback(blockedMsg, blockedUser)
            roomMessage = "** Blocked " + blockedUser.getAlias() + " from the room. **"
            self.sendMessage(roomMessage, blockingUser)
            if blockedUser.getRoom() == blockingUser.getRoom():
                self.joinChat(generalRoom, blockedUser)
        else:
            print("ERROR: " + blockingUser.getAlias() + " attempted to block " + blockedUser.getAlias() + " from " + blockingUser.getRoom().getRoomName() + " but is not the creator of the room")
            feedbackMsg = "You cannot block someone unless you are the room creator."
            self.sendFeedback(feedbackMsg, blockingUser)

    def unblockUser(self, unblockingUser, unblockedUser):
        if unblockingUser == unblockingUser.getRoom().getCreator():
            unblockingUser.getRoom().unblockUser(unblockedUser)
            print(unblockingUser.getAlias() + " unblocked " + unblockedUser.getAlias() + " from " + unblockingUser.getRoom().getRoomName())
            feedbackMsg = "You unblocked " + unblockedUser.getAlias() + " from your current room."
            self.sendFeedback(feedbackMsg, unblockingUser)
            unblockedMsg = unblockingUser.getAlias() + " unblocked you from the chatroom " + unblockingUser.getRoom().getRoomName() + '\n'
            self.sendFeedback(unblockedMsg, unblockedUser)
            roomMessage = "** Unblocked " + unblockedUser.getAlias() + " from the room. **"
            self.sendMessage(roomMessage, unblockingUser)
        else:
            print("ERROR: " + unblockingUser.getAlias() + " attempted to unblock " + unblockedUser.getAlias() + " from " + unblockingUser.getRoom().getRoomName() + " but is not the creator of the room")
            feedbackMsg = "You cannot unblock someone unless you are the room creator."
            self.sendFeedback(feedbackMsg, unblockingUser)

    def createRoom(self, creatingUser, roomName):
        newRoom = Room(roomName, creatingUser)
        room_list.append(newRoom)
        feedbackMsg = "You created the chatroom " + roomName
        self.sendFeedback(feedbackMsg, creatingUser)
        self.joinChat(newRoom, creatingUser)
        return newRoom

    def deleteRoom(self, deletingUser, room):
        if deletingUser == room.getCreator():
            print(deletingUser.getAlias() + " deleted their room " + room.getRoomName() + ", moving all current users to general...")
            feedbackMsg = "You deleted the chatroom " + deletingUser.getRoom().getRoomName()
            self.sendFeedback(feedbackMsg, deletingUser)
            roomMessage = "** Deleted the chatroom " + deletingUser.getRoom().getRoomName() + " **"
            self.sendMessage(roomMessage, deletingUser)
            room_list.remove(room)
            while (len(room.users) != 0):
                self.joinChat(generalRoom, room.users[0])
            del room
        else:
            print("ERROR: " + deletingUser.getAlias() + " attempted to delete the room " + room.getRoomName() + " but is not the creator of the room")
            feedbackMsg = "You cannot delete a chatroom unless you are its creator."
            self.sendFeedback(feedbackMsg, deletingUser)

    def halp(self, user):
        print("help called")
        self.sendFeedback(helpMessage, user)


class RequestHandler:
    def handleRequest(self):
        while True:

            sockets_with_sent_messages, empty, empty = select.select(socket_list, [], [], 0.1)
            try:
                for existing_socket in sockets_with_sent_messages:
                    data = existing_socket.recv(1024)
                    if data:
                        for robot in client_list:
                            if robot.getSocketObj() == existing_socket:
                                print('%s:%s says: %s' % (robot.getAddress()[0], robot.getAddress()[1], data))
                                handleText.interpretMessage(data, robot)

            except socket.error, e:
                if e.errno == 54:
                    for robot in client_list:
                        if robot.getSocketObj() == existing_socket:
                            disconnectMsg = "** has disconnected **"
                            handleText.sendMessage(disconnectMsg, robot)
                            client_list.remove(robot)

def add_users(soket_obj, user_list):
    while(1):
        client, addr = server_socket.accept()
        new_client = ClientInfo(client, addr, generalRoom)
        print("New client added with address %s:%s and room %s" % (addr[0], addr[1], generalRoom.getRoomName()))
        socket_list.append(client)
        client_list.append(new_client)

'''~~~~~~~~~~~~~~~~~~~~~MAIN~~~~~~~~~~~~~~~~~~~~~'''
server_socket = socket.socket()
host = ''#socket.gethostname()
port = 9999

print('Starting Server...')
server_socket.bind((host, port))
server_socket.listen(5)
# List of active socket objects, useful for the select.select() function
socket_list = []
#list of active clientInfo objects
client_list = []

generalRoom = Room('general', None)

room_list = [generalRoom]

handleText = textHandler()

thread.start_new_thread(add_users, (server_socket, socket_list))

requesting = RequestHandler()

requesting.handleRequest()
