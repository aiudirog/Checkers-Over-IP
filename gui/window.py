import Globals as Gl
from PyQt4.QtGui import QWidget, QGridLayout, QMessageBox, QApplication
from PyQt4.QtCore import pyqtSignal, Qt
import os
import sys
import Strings
from gui import GameBoard, GetIPDialog, Loading
from game_play import GameManager


# noinspection PyArgumentList
class Window(QWidget):
    KILL = pyqtSignal()
    SendMove = pyqtSignal(object, object)
    ExecuteMove = pyqtSignal(object, object)
    CannotConnectSignal = pyqtSignal()
    ServerFirst = pyqtSignal()
    RESET = pyqtSignal()
    DeselectAllPieces = pyqtSignal()
    RESIZE = pyqtSignal()
    pieceSelected = pyqtSignal(object)
    emptySpaceSelected = pyqtSignal(object)
    emptySpaceDoubleClicked = pyqtSignal(object)
    clearAllCheckers = pyqtSignal()
    CurrentTurnSignal = pyqtSignal()
    showLoading = pyqtSignal(str)
    endLoading = pyqtSignal()
    changeLoadingText = pyqtSignal(str)

    def __init__(self, screen_rect):
        super(Window, self).__init__()
        self.create_global_signals()
        self.name = "Main Window"
        # Create Main UI
        self.main_grid = QGridLayout()
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setSpacing(0)
        self.game_board = GameBoard(self)
        self.main_grid.setColumnStretch(0, 9999)
        self.main_grid.setRowStretch(0, 9999)
        self.main_grid.addWidget(self.game_board, 1, 1)
        self.main_grid.setColumnStretch(2, 9999)
        self.main_grid.setRowStretch(2, 9999)
        self.setLayout(self.main_grid)

        self.game_over_msg = QMessageBox(self)
        self.game_over_msg.setWindowTitle(Strings.GameOverTitle)
        self.game_over_msg.setTextFormat(Qt.RichText)

        self.setGeometry(300, 100, 600, 600)
        self.setWindowTitle(Strings.Title)
        self.setWindowIcon(Gl.AppIcon)

        self.game_manager = GameManager(self, self.game_board)

        self.show()

        name, Gl.partnerIP = self.get_partner_ip()
        if ":" in name:
            Gl.Name, Gl.PartnerName = name.split(":")[:2]
        else:
            Gl.Name = name
        if len(Gl.partnerIP.split(".")) == 4:
            if not os.path.isdir(Gl.basePath):
                os.makedirs(Gl.basePath)
            with open(Gl.LastConnectionFile, "w") as f:
                f.write(Gl.Name + "\n" + Gl.partnerIP)

        self.game_manager.start_checkers_server()

    def create_global_signals(self):
        Gl.Signals["KILL"] = self.KILL
        Gl.Signals["SendMove"] = self.SendMove
        Gl.Signals["ExecuteMove"] = self.ExecuteMove
        Gl.Signals["CannotConnectSignal"] = self.CannotConnectSignal
        Gl.Signals["ServerFirst"] = self.ServerFirst
        Gl.Signals["RESET"] = self.RESET
        Gl.Signals["DeselectAllPieces"] = self.DeselectAllPieces
        Gl.Signals["pieceSelected"] = self.pieceSelected
        Gl.Signals["emptySpaceSelected"] = self.emptySpaceSelected
        Gl.Signals["emptySpaceDoubleClicked"] = self.emptySpaceDoubleClicked
        Gl.Signals["clearAllCheckers"] = self.clearAllCheckers
        Gl.Signals["CurrentTurnSignal"] = self.CurrentTurnSignal
        Gl.Signals["changeLoadingText"] = self.changeLoadingText
        Gl.Signals["showLoading"] = self.showLoading
        Gl.Signals["endLoading"] = self.endLoading

        Gl.Signals["KILL"].connect(self.on_kill)
        Gl.Signals["CannotConnectSignal"].connect(self.cannot_connect)
        Gl.Signals["showLoading"].connect(self.show_loading)

    @staticmethod
    def get_partner_ip():
        dialog = GetIPDialog()
        dialog.set_offline(Gl.NoInternet)
        while True:
            name, ip, ok = dialog.get_text()
            if not bool(ok):
                Gl.Signals["KILL"].emit()
            if ip == "test" or ip == "Server" or ip == "Offline":
                return name, ip
            if len(ip.split(".")) != 4:
                text = Strings.InvalidIPAddress
                name, ip, ok = dialog.get_text(text)
            if ok != 0:
                if len(ip.split(".")) != 4:
                    continue
            else:
                continue
            return name, ip

    def cannot_connect(self):
        message = QMessageBox()
        message.setWindowTitle(Strings.CannotConnectTitle)
        message.setText(Strings.CannotConnect)
        message.setTextFormat(Qt.RichText)
        message.exec_()
        self.close()

    def resizeEvent(self, qresizeevent):
        self.RESIZE.emit()

    def show_loading(self, string=""):
        Loading(self, string).exec()

    @staticmethod
    def on_kill():
        QApplication.instance().closeAllWindows()
        QApplication.quit()
        sys.exit()
