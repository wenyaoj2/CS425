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


    thrflag = 0
    Msgcount = 0
    socketlst = []
    connections = []
    connect_iplst = []
    name_updated = []
    username_dict = {}



    def __init__(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((p2p.address, p2p.port))
        sock.listen(1)

        #print("Server running ...")

        iThread = threading.Thread(target = self.sendMsg)
        iThread.daemon = True
        iThread.start()

        dThread = threading.Thread(target = self.show_message_or_not)
        dThread.daemon = True
        dThread.start()

        for i in range(10):
            self.socketlst.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

        sThread = threading.Thread(target = self.trytoconnect, args = (self.socketlst, ))
        sThread.daemon = True
        sThread.start()

        cThread = threading.Thread(target = self.check_if_ready)
        cThread.daemon = True
        cThread.start()

        uThread = threading.Thread(target = self.update_username)
        uThread.daemon = True
        uThread.start()


        while True:

            c, a = sock.accept()
            cThread = threading.Thread(target = self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()

            self.connections.append(c)
            #print(str(a[0] + ": " + str(a[1]) + "connected!"))


    def trytoconnect(self, socketlst):

        while True:
            for i in range(len(p2p.peers)):
                if((p2p.peers[i] != p2p.address) & (p2p.peers[i] not in self.connect_iplst)):
                    socketlst[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    err_flag = socketlst[i].connect_ex((p2p.peers[i], p2p.port))
                    if(err_flag == 0):
                        self.connect_iplst.append(p2p.peers[i])
                        #print(self.connect_iplst)
                        #print(self.connections)
                    time.sleep(0.3)


    def handler(self, c, a):

        while True:
            # Receive and print message
            data = ""
            try:
                data = c.recv(1024)
            except:
                pass

            if not data:
                print(self.username_dict[a[0]] + " has" + " left")
                self.connections.remove(c)
                self.connect_iplst.remove(a[0])
                self.name_updated.remove(a[0])
                idx = p2p.peers.index(a[0])
                p2p.timestamp[idx] = 0
                c.close()

                self.thrflag = 1
                sys.exit(0)
                break
            elif (data[0:1] == b'\x12'):
                self.username_dict[a[0]] = str(data[1:], 'utf-8')
                #print(self.username_dict)

            else:
                # convert data from bytes to message()
                data1 = str(data, 'utf-8')
                data1 = function_lib.StringtoMessage(data1)

                # check is data fits causal order
                torf = self.accept_or_deny(data1)
                #print(torf)
                # if true, print and update timestamp of this client
                if(torf == True):
                    print(data1.senderID + ": " + data1.msgData)
                    p2p.timestamp[data1.senderNum - 1] += 1
                    for i in range(len(self.socketlst)):
                        if(p2p.peers[i] in self.connect_iplst):
                            self.socketlst[i].send(data)

                # if not, check if the data is qualified to be added to hold_back queue
                else:
                    if (data1.timestamp[data1.senderNum-1] == p2p.timestamp[data1.senderNum-1] + 1):
                        p2p.Msg_hold_back.append(data1)
                        for i in range(len(self.socketlst)):
                            if(p2p.peers[i] in self.connect_iplst):
                                self.socketlst[i].send(data)
                

    def sendMsg(self):

        while True:
            # Get Input
            MsgContent = input()
            # New message class instance
            MsgtoSend = Msg.Message()
            # Set properties for message
            MsgtoSend.setSenderID(p2p.name)
            self.Msgcount += 1
            p2p.timestamp[p2p.UserNum - 1] += 1
            MsgtoSend.setsenderNum(p2p.UserNum)
            MsgtoSend.setTimeStamp(p2p.timestamp)
            MsgtoSend.setMsgID(self.Msgcount)
            MsgtoSend.setMsgData(MsgContent)
            # Call helper function to change message to string
            finMsg = function_lib.MessagetoString(MsgtoSend)
            for i in range(len(self.socketlst)):
                if(p2p.peers[i] in self.connect_iplst):
                    self.socketlst[i].send(bytes(finMsg, 'utf-8'))


    def accept_or_deny(self, Message):

        if (Message.timestamp[Message.senderNum-1] != p2p.timestamp[Message.senderNum-1] + 1):
            #print(Message.timestamp, p2p.timestamp)
            return False
        else:
            for i in range(len(Message.timestamp)):
                if ((i != Message.senderNum - 1) & (Message.timestamp[i] > p2p.timestamp[i])):
                    return False

        return True


    def show_message_or_not(self):

        while True:
            delivered = []

            for i in range(len(p2p.Msg_hold_back)):
                torf = self.accept_or_deny(p2p.Msg_hold_back[i])
                if (torf == True):
                    print(p2p.Msg_hold_back[i].senderID + ": " + p2p.Msg_hold_back[i].msgData)
                    p2p.timestamp[p2p.Msg_hold_back[i].senderNum - 1] += 1
                    delivered.append(p2p.Msg_hold_back[i])
            for i in range(len(delivered)):
                p2p.Msg_hold_back.remove(delivered[i])
            time.sleep(0.3)
            if(self.thrflag == 1):
                sys.exit(0)


    def check_if_ready(self):

        readynum = p2p.Usercount - 1
        while True:
            if((len(self.connections) == readynum) & (len(self.connect_iplst) == readynum)):
                print("READY")
                sys.exit(0)
            time.sleep(0.1)

    # The header for username_dict updating message is '\x12'
    def update_username(self):

        while True:
            for i in range(len(p2p.peers)):
                if ((p2p.peers[i] in self.connect_iplst) & (p2p.peers[i] not in self.name_updated)):
                    str_name = '\x12'
                    str_name += p2p.name
                    self.name_updated.append(p2p.peers[i])
                    self.socketlst[i].send(bytes(str_name, 'utf-8'))
            time.sleep(0.3)




class p2pclass:

    # Basic information of each user
    peers = []
    name = "Bob"
    UserNum = 0
    Usercount = 0
    timestamp = [0,0,0,0,0,0,0,0,0,0]
    address = '127.0.0.1'
    port = 0

    # list for hold back queue
    Msg_hold_back = []



global p2p
p2p = p2pclass()

def main():

    url_list = getaddress.get_ip().get_url_list()
    ip_list = getaddress.get_ip().get_ip_list()
    
    if(len(sys.argv) >= 4):
        try:
            p2p.name = str(sys.argv[1])
            p2p.port = int(sys.argv[2])
            p2p.Usercount = int(sys.argv[3])
            #print("Usercount: ", p2p.Usercount)
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
            server = Server()

        except KeyboardInterrupt:
            sys.exit(0)
        time.sleep(0.4)


main()
