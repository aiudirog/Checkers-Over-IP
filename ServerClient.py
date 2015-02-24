# ServerClient.py

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from Globals import *
import Globals
from time import sleep
from random import randint
import socket

class serverAndClient(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
    
    def run(self):
        self.movesToRun = []
        Globals.mainWindow.SendMove.connect(self.sendMoves)
        Signals["SendMessage"].connect(self.sendMessage)
        self.client = xmlrpc.client.ServerProxy('http://{0}:8000'.format(Globals.partnerIP))
        self.server = SimpleXMLRPCServer((myIP, 8000))
        self.server.register_function(self.sendMoves)
        self.server.register_function(self.receiveMoves)
        self.server.register_function(self.setCurrentTurn)
        self.server.register_function(self.setCurrentTurnReceive)
        self.server.register_function(self.sendMessage)
        self.server.register_function(self.receiveMessage)
        
        self.server.serve_forever()
    
    def setCurrentTurn(self):
        turn = randint(0,1)
        Globals.mainWindow.gameBoard.CurrentTurnSignal.emit(turn)
        try: self.client.setCurrentTurnReceive(turn)
        except socket.gaierror as error: 
            print(error)
        return 1
    
    def setCurrentTurnReceive(self, turn):
        Globals.mainWindow.gameBoard.CurrentTurnSignal.emit(turn)
        return 1
            
    def sendMoves(self, listOfMoves, piecesToRemove):
        try: self.client.receiveMoves(listOfMoves,piecesToRemove)
        except socket.gaierror as error: 
            print(error)
        Globals.mainWindow.ExecuteMove.emit(listOfMoves,piecesToRemove)
        return 1
    
    def receiveMoves(self, listOfMoves, piecesToRemove):
        Globals.mainWindow.ExecuteMove.emit(listOfMoves,piecesToRemove)
        return 1
    
    def sendMessage(self, name, msg):
        try: self.client.receiveMessage(name, msg)
        except socket.gaierror as error: 
            print(error)
        self.receiveMessage(name, msg)
        return 1
    
    def receiveMessage(self, name, msg):
        Signals["ReceiveMessage"].emit(name, msg)
        return 1