# ServerClient.py

()
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
        

"""
python3 Example
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

# Register pow() function; this will use the value of
# pow.__name__ as the name, which is just 'pow'.
server.register_function(pow)

# Register a function under a different name
def adder_function(x,y):
    return x + y
server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'mul').
class MyFuncs:
    def mul(self, x, y):
        return x * y

server.register_instance(MyFuncs())

# Run the server's main loop
server.serve_forever()

import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://localhost:8000')
print(s.pow(2,3))  # Returns 2**3 = 8
print(s.add(2,3))  # Returns 5
print(s.mul(5,2))  # Returns 5*2 = 10

# Print list of available methods
print(s.system.listMethods())


--------------------------------------------

python2.7 Example
from SimpleXMLRPCServer import SimpleXMLRPCServer

class say(msg):
    print msg

# Create the server
server = SimpleXMLRPCServer(("localhost", <port>))
server.register_function(say)
server.serve_forever()

# import library
from xmlrpclib import Server

# Connect to the other computer
remote_computer = Server('http://<friends IP>:<port>')

# Send messages.
message = 'Client connected'

while message:
    remote_computer.say(message)
    message = raw_input("Type here: ")
"""