#########################
##CS425 Spring 2019 MP1##
#########################


# import libraries
import socket
import threading
import sys
import time
from random import randint

# import other files
import Msg
import function_lib
import getaddress



class Server:

    connections = []
    peers = []
    Msgarray = []
    Msgcount = 0
    thrflag = 0
    connection_dict = {}
    username_dict = {}
    newstrflag = False
    inputstring = ""


    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', p2p.port))
        sock.listen(1)

        print("Server running ...")

        iThread = threading.Thread(target = self.sendMsg)
        iThread.daemon = True
        iThread.start()

        dThread = threading.Thread(target = self.show_message_or_not)
        dThread.daemon = True
        dThread.start()


        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target = self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()


            self.connections.append(c)

            print(str(a[0] + ": " + str(a[1]) + "connected!"))
            data = sock.recv(1024)
            if not data:
                break

    def handler(self, c, a):
        while True:
            # Receive and print message
            data = c.recv(1024)
            
            if not data:
                print(str(a[0]) + ": " + str(a[1]) + "disconnected!")
                self.connections.remove(c)
                c.close()

                self.thrflag = 1
                sys.exit(0)
                break

            data1 = str(data, 'utf-8')
            data1 = function_lib.StringtoMessage(data1)

            torf = self.accept_or_deny(data1)
            if(torf == True):
                print(data1.senderID, ": ", data1.msgData)
                p2p.timestamp[data1.senderNum - 1] += 1

            else:
                if (data1.timestamp[data1.senderNum-1] == p2p.timestamp[data1.senderNum-1] + 1):
                    p2p.Msg_hold_back.append(data1)
            
            self.connection_dict[c] = data1.senderID
            self.username_dict[data1.senderID] = c

            for connection in self.connections:
                if(connection != c):
                    connection.send(bytes(data))
                
            #insert element to connection dict

    def sendMsg(self):

        while True:
            if(self.thrflag == 1):
                sys.exit(0)
            MsgContent = ""

            if (p2p.string_update == True):
                MsgContent = p2p.string_to_use
                p2p.string_update = False
            else:
                time.sleep(0.3)
                if(self.thrflag == 1):
                    sys.exit(0)
                continue

            MsgtoSend = Msg.Message()
            MsgtoSend.setSenderID(p2p.name)
            self.Msgcount += 1
            p2p.timestamp[p2p.UserNum - 1] += 1
            MsgtoSend.setsenderNum(p2p.UserNum)
            MsgtoSend.setTimeStamp(p2p.timestamp)
            MsgtoSend.setMsgID(self.Msgcount)
            MsgtoSend.setMsgData(MsgContent)
            finMsg = function_lib.MessagetoString(MsgtoSend)
            for connection in self.connections:
                connection.send(bytes(finMsg, 'utf-8'))

    def accept_or_deny(self, Message):
        if (Message.timestamp[Message.senderNum-1] != p2p.timestamp[Message.senderNum-1] + 1):
            return False
        else:
            for i in range(len(Message.timestamp)):
                if (i != Message.senderNum - 1 & Message.timestamp[i] > p2p.timestamp[i]):
                    return False

        return True

    def show_message_or_not(self):
        while True:
            delivered = []

            for i in range(len(p2p.Msg_hold_back)):
                torf = self.accept_or_deny(p2p.Msg_hold_back[i])
                if (torf == True):
                    print(p2p.Msg_hold_back[i].senderID, ": ", p2p.Msg_hold_back[i].msgData)
                    p2p.timestamp[p2p.Msg_hold_back[i].senderNum - 1] += 1
                    delivered.append(p2p.Msg_hold_back[i])
            for i in range(len(delivered)):
                p2p.Msg_hold_back.remove(delivered[i])
            time.sleep(0.3)
            if(self.thrflag == 1):
                sys.exit(0)



class Client:

    # how many messages have been sent by one user
    Msgcount = 0
    # flags to terminate some threads
    thrflag = 0

    # Constructor
    # Input: address that will be hard-coded to this user
    def __init__(self, address):

        # Establish TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, p2p.port))

        # Starting new thread for message sending
        iThread = threading.Thread(target = self.sendMsg, args = (sock, ))
        iThread.daemon = True 
        iThread.start()

        # Starting new thread for checking if any message in hold_back queue can be delivered
        dThread = threading.Thread(target = self.show_message_or_not)
        dThread.daemon = True
        dThread.start()

        # Loop of Constructor
        while True:

            # keep receving data from server
            data = sock.recv(1024)

            # if not receiving data, raise flag and break loop
            if not data:
                self.thrflag = 1
                break
            
            # if not, the data should be messages
            else:

                # convert data from bytes to message()
                data1 = str(data, 'utf-8')
                data1 = function_lib.StringtoMessage(data1)

                # check is data fits causal order
                torf = self.accept_or_deny(data1)
                
                # if true, print and update timestamp of this client
                if(torf == True):
                    print(data1.senderID, ": ", data1.msgData)
                    p2p.timestamp[data1.senderNum - 1] += 1
                    sock.send(data)

                # if not, check if the data is qualified to be added to hold_back queue
                else:
                    if (data1.timestamp[data1.senderNum-1] == p2p.timestamp[data1.senderNum-1] + 1):
                        p2p.Msg_hold_back.append(data1)


    def sendMsg(self, sock):

        while True:
            MsgContent = ""
            if (p2p.string_update == True):
                MsgContent = p2p.string_to_use
                p2p.string_update = False
            else:
                time.sleep(0.3)
                if(self.thrflag == 1):
                    sys.exit(0)
                continue
            MsgtoSend = Msg.Message()
            p2p.timestamp[p2p.UserNum - 1] += 1
            MsgtoSend.setsenderNum(p2p.UserNum)
            MsgtoSend.setSenderID(p2p.name)
            self.Msgcount += 1
            MsgtoSend.setTimeStamp(p2p.timestamp)
            MsgtoSend.setMsgID(self.Msgcount)
            MsgtoSend.setMsgData(MsgContent)
            finMsg = function_lib.MessagetoString(MsgtoSend)
            sock.send(bytes(finMsg, 'utf-8'))
            if(self.thrflag == 1):
                sys.exit(0)

    def accept_or_deny(self, Message):
        if (Message.timestamp[Message.senderNum-1] != p2p.timestamp[Message.senderNum-1] + 1):
            return False
        else:
            for i in range(len(Message.timestamp)):
                if (i != Message.senderNum - 1 & Message.timestamp[i] > p2p.timestamp[i]):
                    return False

        return True

    def show_message_or_not(self):
        while True:
            delivered = []
            for i in range(len(p2p.Msg_hold_back)):
                torf = self.accept_or_deny(p2p.Msg_hold_back[i])
                if (torf == True):
                    print(p2p.Msg_hold_back[i].senderID, ": ", p2p.Msg_hold_back[i].msgData)
                    p2p.timestamp[p2p.Msg_hold_back[i].senderNum - 1] += 1
                    delivered.append(p2p.Msg_hold_back[i])
            for i in range(len(delivered)):
                p2p.Msg_hold_back.remove(delivered[i])
            time.sleep(0.3)
            if(self.thrflag == 1):
                sys.exit(0)

class p2pclass:

    # Basic information of each user
    peers = []
    name = "Bob"
    UserNum = 0
    Usercount = 0
    timestamp = [0,0,0,0,0,0,0,0]
    address = '127.0.0.1'
    port = 0
    
    # global variables for recording input values 
    string_to_use = ""
    string_update = False

    # list for hold back queue
    Msg_hold_back = []



def inputstr():
    while (True):
        p2p.string_to_use = input()
        p2p.string_update = True

global p2p
p2p = p2pclass()

def main():

    url_list = getaddress.get_ip().get_url_list()
    ip_list = getaddress.get_ip().get_ip_list()
    
    # Thread for receive input values
    inThread = threading.Thread(target = inputstr)
    inThread.daemon = True
    inThread.start()

    if(len(sys.argv) >= 4):
        try:
            p2p.name = str(sys.argv[1])
            p2p.port = int(sys.argv[2])
            p2p.Usercount = int(sys.argv[3])
        except:
            print("# Wrong input format!")
            sys.exit(0)
    else:
        print("# Wrong input format!")
        sys.exit(0)

    # get ip address and update peer list in p2p
    p2p.address = socket.gethostbyname(socket.gethostname())

    for i in range(len(ip_list)):
        if(p2p.address == ip_list[i]):
            p2p.UserNum = i + 1

    p2p.peers = ip_list


    while True:
        try:
            print("Try to connect ...")

            for i in range(len(p2p.peers)):
                try:
                    client = Client(p2p.peers[i])
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass
                
                time.sleep(float(randint(1,5)) / 2)
                if (randint(1, 20) == 1):
                    try:
                        s = socket.socket()
                        time.sleep(float(randint(1,5)) / 20)
                        s.settimeout(0.5)
                        judge = s.connect_ex(('localhost', p2p.port)) != 0
                        if judge == 1:
                            server = Server()
                        s.close()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    except:
                        print("Couldn't start the server ...")

        except KeyboardInterrupt:
            sys.exit(0)


main()
