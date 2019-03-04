from Msg import Message




def timeStamptoString(timeStamp):

    tsStr = ""
    for i in range(len(timeStamp)):
        tsStr += str(timeStamp[i])
        if (i != len(timeStamp) - 1):
            tsStr += " "
    
    return tsStr


def StringtotimeStamp(tsStr):

    timeStamp = tsStr.split(' ')
    for i in range(len(timeStamp)):
        timeStamp[i] = int(timeStamp[i])
    
    return timeStamp


def MessagetoString(Message):

    MsgStr = str(Message.msgID)
    MsgStr += ','
    MsgStr += str(Message.senderNum)
    MsgStr += ','
    MsgStr += str(Message.senderID)
    MsgStr += ','
    MsgStr += timeStamptoString(Message.timestamp)
    MsgStr += ','
    MsgStr += str(Message.msgData)

    return MsgStr


def StringtoMessage(MsgStr):
    Msglist = MsgStr.split(',', 4)
    Msgts = StringtotimeStamp(Msglist[3])
    Mes = Message()
    Mes.setMsgID(int(Msglist[0]))
    Mes.setsenderNum(int(Msglist[1]))
    Mes.setSenderID(Msglist[2])
    Mes.setTimeStamp(Msgts)
    Mes.setMsgData(Msglist[4])
    
    return Mes