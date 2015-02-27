# ServerClient.py

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from Globals import *
import Globals
from time import sleep
from random import randint
import socket
from sys import stdout
import Strings

class SignalReceiver(QObject):
    def __init__(self):
        super(SignalReceiver, self).__init__()
        self.eventLoop = QEventLoop(self)
    
class GetMovesFromServerThread(QThread):
    def __init__(self, parent, client, listOfMoves=None, piecesToRemove=None):
        QThread.__init__(self, parent)
        self.client = client
        self.listOfMoves = listOfMoves
        self.piecesToRemove = piecesToRemove
        
    def run(self):
        try:
            if self.listOfMoves == None:
                ServerMoves, ServerPiecesToRemove = self.client.receiveMoves()
            else:
                ServerMoves, ServerPiecesToRemove = self.client.receiveMoves(self.listOfMoves,self.piecesToRemove)
            Globals.Signals["ExecuteMove"].emit(ServerMoves,ServerPiecesToRemove)
        except socket.error as error: 
            print(error)

class GetMessagesFromServerThread(QThread):
    def __init__(self, parent, client):
        QThread.__init__(self, parent)
        self.client = client
        
    def run(self):
        while True:
            try:
                msgs = self.client.getMessages()
                if msgs:
                    name = msgs[0]
                    for msg in msgs[1:]:
                        Globals.Signals["ReceiveMessage"].emit(name, msg)
            except socket.error as _error: 
                pass
                #print(error)
            sleep(2)

class CheckersServer(QThread):
    ServerFirst = pyqtSignal()
    def __init__(self, parent):
        QThread.__init__(self, parent)
    
    def run(self):
        self.Querys = 0
        self.movesToRun = []
        self.piecesToRemove = []
        Globals.Signals["SendMove"].connect(self.sendMoves)
        if Globals.partnerIP == "Server":
            Globals.Type = "Server"
            self.server = SimpleXMLRPCServer((myIP, 8000))
            self.server.register_function(self.sendMoves)
            self.server.register_function(self.receiveMoves)
            self.server.register_function(self.setCurrentColorIAm)
            self.server.serve_forever()
        else:
            Globals.Type = "Client"
            self.ServerFirst.connect(self.getMovesFromServer)
            self.client = xmlrpc.client.ServerProxy('http://{0}:8000'.format(Globals.partnerIP))
            self.signalReceiver = SignalReceiver()
            self.signalReceiver.moveToThread(self)
            self.QueryServer()
            
    def QueryServer(self):
        #Set the turn of the server and decide who is red
        #and who is black.
        
        ME = 0
        turn = 1#randint(0,1)
        if ME == turn:
            #I'm black | Server is Red
            Globals.ColorIAm = Black_Turn
            if Globals.partnerIP != "Offline": 
                if not self.SendColorToServer(Red_Turn):
                    return
        else:
            #I'm Red | Server is Black
            Globals.ColorIAm = Red_Turn
            if Globals.partnerIP != "Offline": 
                if self.SendColorToServer(Black_Turn):
                    self.ServerFirst.emit()
                else:
                    return
        Globals.Signals["CurrentTurnSignal"].emit()
        self.signalReceiver.eventLoop.exec()
    
    def SendColorToServer(self,turn):
        retry = False
        try: 
            Globals.PartnerName = self.client.setCurrentColorIAm(turn, Globals.Name)
        except socket.error as error:
            print(error)
            retry = True
        if retry and self.Querys < 24:
            self.Querys += 1
            for i in range(10):
                stdout.flush()
                stdout.write("\r"+Strings.Retrying+"."*i)
                sleep(0.5)
            print()
            self.SendColorToServer(turn)
        elif not retry:
            return True
        else:
            Globals.Signals["CannotConnectSignal"].emit()
            return False
    
    def setCurrentColorIAm(self, color, name):
        Globals.ColorIAm = color
        Globals.PartnerName = name
        Globals.Signals["CurrentTurnSignal"].emit()
        return Globals.Name
            
    def sendMoves(self, listOfMoves, piecesToRemove):
        if Globals.Type == "Client":
            self.getMovesFromServer(listOfMoves, piecesToRemove)
        else:
            self.movesToRun = listOfMoves
            self.piecesToRemove = piecesToRemove
        return 1
    
    def getMovesFromServer(self, listOfMoves=None, piecesToRemove=None):
        if Globals.partnerIP != "Offline": 
            #wait for a response with server's moves.
            GetMovesFromServerThread(self, self.client, listOfMoves, piecesToRemove).start()
    
    def receiveMoves(self, listOfMoves=None, piecesToRemove=None):
        self.movesToRun = []
        self.piecesToRemove = []
        if listOfMoves != None:
            Globals.Signals["ExecuteMove"].emit(listOfMoves,piecesToRemove)
        while self.movesToRun == []:
            pass
        return self.movesToRun, self.piecesToRemove

class MessengerServer(QThread):
    CallGetMsgsLater = pyqtSignal()
    def __init__(self, parent):
        QThread.__init__(self, parent)
    
    def run(self):
        Signals["SendMessage"].connect(self.sendMessage)
        if Globals.partnerIP == "Offline": return
        if Globals.partnerIP == "Server":
            Globals.Type = "Server"
            self.MessagesToReturn = [Globals.Name]
            self.server = SimpleXMLRPCServer((myIP, 8001))
            self.server.register_function(self.getMessages)
            self.server.register_function(self.receiveMessage)
            self.server.serve_forever()
        else:
            Globals.Type = "Client"
            self.client = xmlrpc.client.ServerProxy('http://{0}:8001'.format(Globals.partnerIP))
            #Call this AFTER the signal reciever starts
            self.CallGetMsgsLater.connect(self.GetMsgsLater)
            self.CallGetMsgsLater.emit()
            
            self.signalReceiver = SignalReceiver()
            self.signalReceiver.moveToThread(self)
            self.signalReceiver.eventLoop.exec()
    
    def GetMsgsLater(self):
        GetMessagesFromServerThread(self,self.client).start()
    
    def getMessages(self):
        """
        This function requests a list of messages from the server.
        Used by the client to get any new messages 
        """
        if len(self.MessagesToReturn) > 1:
            messages = self.MessagesToReturn.copy()
            self.MessagesToReturn = [Globals.Name]
            return messages
        else:
            return False
    
    def sendMessage(self, name, msg):
        """
        This function is used by both the server and the client
        to transmit text based messages.
        """
        if Globals.partnerIP == "Server":
            #Prepare the message to send on the next .getMessages()
            Globals.Signals["ReceiveMessage"].emit(name, msg)
            self.MessagesToReturn.append(msg)
        else:
            try: self.client.receiveMessage(name, msg)
            except socket.error as error: 
                print(error)
            self.receiveMessage(name, msg)
            return 1
        
    def receiveMessage(self, name, msg):
        Globals.Signals["ReceiveMessage"].emit(name, msg)
        return 1