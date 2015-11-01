from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import Globals as Gl
from PyQt4.QtCore import QObject, QThread, QEventLoop
from PyQt4.QtGui import QApplication
from time import sleep
from random import randint
import socket
from sys import stdout
import Strings
import http


class SignalReceiver(QObject):
    def __init__(self):
        super(SignalReceiver, self).__init__()
        self.eventLoop = QEventLoop(self)


class GetMovesFromServerThread(QThread):
    def __init__(self, parent, client, list_of_moves=None, pieces_to_remove=None):
        QThread.__init__(self, parent)
        self.client = client
        self.list_of_moves = list_of_moves
        self.pieces_to_remove = pieces_to_remove

    def run(self):
        try:
            if self.list_of_moves is None:
                server_moves, server_pieces_to_remove = self.client.receive_moves()
            else:
                server_moves, server_pieces_to_remove = self.client.receive_moves(self.list_of_moves,
                                                                                  self.pieces_to_remove)
            Gl.Signals["ExecuteMove"].emit(server_moves, server_pieces_to_remove)
        except socket.error as error:
            print(error)
        except http.client.CannotSendRequest as error:
            print("http.client.CannotSendRequest:", error)


class CheckersServer(QThread):
    server = False
    client = False
    signal_receiver = False
    querys = 0
    moves_to_run = []
    pieces_to_remove = []

    def __init__(self, parent):
        QThread.__init__(self, parent)

    def run(self):
        self.querys = 0
        self.moves_to_run = []
        self.pieces_to_remove = []
        Gl.Signals["SendMove"].connect(self.send_moves)

        if Gl.partnerIP == "Server":
            Gl.Type = "Server"
            self.server = SimpleXMLRPCServer((Gl.myIP, 8000))
            self.server.register_function(self.send_moves)
            self.server.register_function(self.receive_moves)
            self.server.register_function(self.set_current_color_i_am)
            self.server.serve_forever()
        else:
            Gl.Type = "Client"
            Gl.Signals["ServerFirst"].connect(self.get_moves_from_server)
            self.client = xmlrpc.client.ServerProxy('http://{0}:8000'.format(Gl.partnerIP))
            self.signal_receiver = SignalReceiver()
            self.signal_receiver.moveToThread(self)
            self.query_server()

    def query_server(self):
        self.determine_who_is_what_color()
        self.signal_receiver.eventLoop.exec()

    def determine_who_is_what_color(self):
        # Set the turn of the server and decide who is red
        # and who is black.

        me = 0
        turn = randint(0, 1)
        if me == turn:
            # I'm black | Server is Red
            Gl.ColorIAm = Gl.Black_Turn
            if Gl.partnerIP != "Offline":
                if not self.send_color_to_server(Gl.Red_Turn):
                    return
        else:
            # I'm Red | Server is Black
            Gl.ColorIAm = Gl.Red_Turn
            if Gl.partnerIP != "Offline":
                if self.send_color_to_server(Gl.Black_Turn):
                    Gl.Signals["ServerFirst"].emit()
                else:
                    return
        Gl.Signals["CurrentTurnSignal"].emit()

    def send_color_to_server(self, turn):
        Gl.Signals["showLoading"].emit(Strings.ConnectingToServer)
        retry = True
        while retry:
            retry = False
            try:
                Gl.PartnerName = self.client.set_current_color_i_am(turn, Gl.Name)
            except socket.error as error:
                print(error)
                retry = True
            except http.client.CannotSendRequest as error:
                print("http.client.CannotSendRequest:", error)
                retry = True
            if retry:
                for i in range(8):
                    stdout.flush()
                    stdout.write("\r" + Strings.Retrying + "." * i)
                    sleep(0.5)
                print()
        Gl.Signals["endLoading"].emit()
        return True

    @staticmethod
    def set_current_color_i_am(color, name):
        Gl.ColorIAm = color
        Gl.PartnerName = name
        Gl.Signals["CurrentTurnSignal"].emit()
        return Gl.Name

    def send_moves(self, list_of_moves, pieces_to_remove):
        if Gl.Type == "Client":
            self.get_moves_from_server(list_of_moves, pieces_to_remove)
        else:
            self.moves_to_run = list_of_moves
            self.pieces_to_remove = pieces_to_remove
        return 1

    def get_moves_from_server(self, list_of_moves=None, pieces_to_remove=None):
        if Gl.partnerIP != "Offline":
            # wait for a response with server's moves.
            GetMovesFromServerThread(self, self.client, list_of_moves, pieces_to_remove).start()

    def receive_moves(self, list_of_moves=None, pieces_to_remove=None):
        self.moves_to_run = []
        self.pieces_to_remove = []
        if list_of_moves is not None:
            Gl.Signals["ExecuteMove"].emit(list_of_moves, pieces_to_remove)
            # noinspection PyArgumentList
            QApplication.processEvents()
        sleep(2)
        while not self.moves_to_run:
            sleep(0.2)
        return self.moves_to_run, self.pieces_to_remove
