import socket
import thread
import select
import string
from time import sleep

helpMessage = '''List of Valid Commands:

/join [chatroom_name] - joins the chatroom [chatroom_name]

/leave - leaves the current chatroom and join the general chatroom

/create [chatroom_name] - creates a chatroom with the name [chatroom_name] and moves you to this room, you can block and unblock users from this room as well as delete the room

/delete [chatroom_name] - deletes the chatroom [chatroom_name] and moves all users to the general chatroom if you are the creator of this chatroom

/set_alias [alias] - changes your alias displayed to other users. Maximum 15 characters

/block [user_alias] - blocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/unblock [user_alias] - unblocks a user with the alias [user_alias] from the chatroom you are currently in if you are the creator of this chatroom

/rooms - displays a list of active rooms

/help - displays this message\n'''

class ClientInfo:

    def __init__(self, clientSocketObj, address, startingRoom):

        self.socket_obj = clientSocketObj
        self.address = address
        self.alias = address[0] + ":" + str(address[1])
        self.room = startingRoom
        self.room.addUser(self)

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
        self.users = []
        self.blockedUsers = []

    def addUser(self, user):
        self.users.append(user)
        return user

    #we were missing this bad boy in the design docs
    def removeUser(self, user):
        if user in self.users:
            self.users.remove(user)
        return user

    #also this bad boy
    def blockUser(self, user):
        self.removeUser(user)
        self.blockedUsers.append(user)
        return user

    #oh and this guy
    def unblockUser(self, user):
        self.blockedUsers.remove(user)
        return user

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

            if len(msgSplit) == 2 or msgSplit[0] == "/leave" or msgSplit[0] == "/rooms":
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
                    if user.getRoom() != generalRoom:
                        self.joinChat(generalRoom, user)
                    else:
                        feedbackMsg = "You cannot leave the general chatroom, you can only leave other rooms."
                        self.sendFeedback(feedbackMsg, user)

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
                    for individual in client_list:
                        if individual == user:
                            argValid = True
                            feedbackMsg = "You cannot block yourself."
                            self.sendFeedback(feedbackMsg, user)
                            break

                        elif individual.getAlias() == msgSplit[1]:
                            argValid = True
                            self.blockUser(user, individual)
                            break

                    if not argValid:
                        feedbackMsg = "That alias is currently not in use"
                        self.sendFeedback(feedbackMsg, user)

                elif msgSplit[0] == "/unblock":
                    for individual in client_list:
                        if individual.getAlias() == msgSplit[1]:
                            argValid = True
                            self.unblockUser(user, individual, )
                            break

                    if not argValid:
                        feedbackMsg = "that alias is currently not in use"
                        self.sendFeedback(feedbackMsg, user)

                elif msgSplit[0] == "/rooms":
                    feedbackMsg = "These are the active rooms: "
                    for room in room_list:
                        feedbackMsg = feedbackMsg + str(room.getRoomName()) + ", "
                    feedbackMsg = feedbackMsg[:-2]
                    self.sendFeedback(feedbackMsg, user)

                else:
                    self.halp(user)
            else:
                self.halp(user)
        else:
            self.sendMessage(msg, user)

    def sendFeedback(self, msg, user):
        sleep(0.01)
        user.getSocketObj().send(msg)

    def notify(self, msg, user):
        clientsInRoom = user.getRoom().getUsers()
        for client in clientsInRoom:
            if client != user:
                handleText.sendFeedback(msg, client)

    def sendMessage(self, msg, user):
        destinationClients = user.getRoom().getUsers()
        msg = user.getAlias() + ": " + msg

        for individual in destinationClients:
            if individual == user:
                continue

            individual.getSocketObj().send(msg)


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

        if len(newAlias) > 15:
            feedbackMsg = "Specified alias exceeds 15 character limit. Please choose a shorter alias."
            self.sendFeedback(feedbackMsg, user)

            return

        print(user.getAlias() + " changed their alias to " + newAlias)

        feedbackMsg = "You changed your alias to " + newAlias
        self.sendFeedback(feedbackMsg, user)

        roomMessage = "** Changed alias to " + newAlias + " **"
        self.sendMessage(roomMessage, user)

        user.setAlias(newAlias)


    def blockUser(self, blockingUser, blockedUser):
        if blockingUser == blockingUser.getRoom().getCreator() and blockedUser not in blockingUser.getRoom().getBlockedUsers():
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
            return

        elif blockingUser != blockingUser.getRoom().getCreator():
            print("ERROR: " + blockingUser.getAlias() + " attempted to block " + blockedUser.getAlias() + " from " + blockingUser.getRoom().getRoomName() + " but is not the creator of the room")

            feedbackMsg = "You cannot block someone unless you are the room creator."

        else:
            print("ERROR: " + blockingUser.getAlias() + " attempted to block " + blockedUser.getAlias() + " from " + blockingUser.getRoom().getRoomName() + " but they have already been blocked")

            feedbackMsg = "This user has already been blocked from this room."

        self.sendFeedback(feedbackMsg, blockingUser)

    def unblockUser(self, unblockingUser, unblockedUser):
        if unblockingUser == unblockingUser.getRoom().getCreator() and unblockedUser in unblockingUser.getRoom().getBlockedUsers(): # Don't worry about it
            unblockingUser.getRoom().unblockUser(unblockedUser)
            print(unblockingUser.getAlias() + " unblocked " + unblockedUser.getAlias() + " from " + unblockingUser.getRoom().getRoomName())

            feedbackMsg = "You unblocked " + unblockedUser.getAlias() + " from your current room."
            self.sendFeedback(feedbackMsg, unblockingUser)

            unblockedMsg = unblockingUser.getAlias() + " unblocked you from the chatroom " + unblockingUser.getRoom().getRoomName() + '\n'
            self.sendFeedback(unblockedMsg, unblockedUser)

            roomMessage = "** Unblocked " + unblockedUser.getAlias() + " from the room. **"
            self.sendMessage(roomMessage, unblockingUser)

            return

        elif unblockingUser != unblockingUser.getRoom().getCreator():
            print("ERROR: " + unblockingUser.getAlias() + " attempted to unblock " + unblockedUser.getAlias() + " from " + unblockingUser.getRoom().getRoomName() + " but is not the creator of the room")

            feedbackMsg = "You cannot unblock someone unless you are the room creator."
        else:
            print("ERROR: " + unblockingUser.getAlias() + " attempted to unblock " + unblockedUser.getAlias() + " from " + unblockingUser.getRoom().getRoomName() + " but they were not blocked before")

            feedbackMsg = "This user was not blocked from this room."

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

            feedbackMsg = "You deleted the chatroom " + room.getRoomName()
            self.sendFeedback(feedbackMsg, deletingUser)

            roomMessage = "** Deleted the chatroom " + room.getRoomName() + " **"
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

        while 1:

            try:
                # select.select() returns lists of readable, writeable, and error sockets
                # when given lists of sockets. if a socket is 'readable', it means it has
                # sent a message that is ready to be received
                sockets_with_sent_messages, empty, empty = select.select(socket_list, [], [], 0.1)

                # Iterate through the sockets that have sent messages and receive them
                for existing_socket in sockets_with_sent_messages:
                    data = existing_socket.recv(1024)

                    # If data is valid, figure out who it came from by matching the socket to its
                    # corresponding clientInfo object and pass it along to the textHandler object
                    # to be redistributed or executed in the case where it is a command
                    if data:
                        for individual in client_list:
                            if individual.getSocketObj() == existing_socket:
                                print('%s:%s says: %s' % (individual.getAddress()[0], individual.getAddress()[1], data))
                                handleText.interpretMessage(data, individual)

                    # When a client socket is unexpectedly shut down (keyboard interrupt)
                    # it gets marked 'readable' so it gets appended into sockets_with_sent_messages.
                    # However, nothing will be received from it, so 'if data' will evaluate to false.
                    # In this case, we can shut down the socket and remove it and its associated
                    # user from any lists they may belong to.
                    else:
                        for individual in client_list:
                            if individual.getSocketObj() == existing_socket:

                                disconnectMsg = "** " +individual.getAlias() + " has disconnected. **"
                                handleText.notify(disconnectMsg, individual)

                                # shutdown and close the disconnected socket
                                individual.getSocketObj().shutdown(socket.SHUT_WR)
                                individual.getSocketObj().close()

                                # remove the client and/or its associated socket from their room, client list, and socket list
                                individual.getRoom().removeUser(individual)
                                client_list.remove(individual)
                                socket_list.remove(individual.getSocketObj())

            except socket.error, e:
                print("exception raised")

class connectionHandler:

    def add_users(self, socketObj, socketList, clientList): # add text handler as optional argument, add socket list to args
        while(1):
            client, addr = socketObj.accept() # change to socket_obj.accept() after demo
            new_client = ClientInfo(client, addr, generalRoom)
            print("New client added with address %s:%s and room %s" % (addr[0], addr[1], generalRoom.getRoomName()))
            handleText.notify(new_client.getAlias() + "** joined room **", new_client)
            socketList.append(client)
            clientList.append(new_client)

    def connectionThread(self, serverSocket, socketList, clientList):
        thread.start_new_thread(self.add_users, (serverSocket, socketList, clientList))

'''~~~~~~~~~~~~~~~~~~~~~MAIN~~~~~~~~~~~~~~~~~~~~~'''
server_socket = socket.socket()
# setting host to '' sets it to the local machine
host = ''
port = 9999
address = (host, port)

print('Starting Server...')
server_socket.bind(address)
server_socket.listen(5)

# List of active socket objects, useful for the select.select() function
socket_list = []
#list of active clientInfo objects
client_list = []

generalRoom = Room('general', None)

room_list = [generalRoom]

connecting = connectionHandler()

handleText = textHandler()

requesting = RequestHandler()

connecting.connectionThread(server_socket, socket_list, client_list)

requesting.handleRequest()
