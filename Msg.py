
class Message:

    msgID = 0
    senderNum = 0
    senderID = ""
    timestamp = [0,0,0,0,0,0,0,0,0,0]
    msgData = ""

    def __init__(self):
        pass

    def setsenderNum(self, senderNum_):
        self.senderNum = senderNum_

    def setMsgID(self, msgID_):
        self.msgID = msgID_
    
    def setSenderID(self, senderID_):
        self.senderID = senderID_

    def setMsgData(self, msgData_):
        self.msgData = msgData_

    def setTimeStamp(self, timestamp_):
        self.timestamp = timestamp_.copy()

