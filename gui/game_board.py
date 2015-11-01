import Globals as Gl
from PyQt4.QtGui import QWidget, QPixmap, QLabel, QGridLayout
from PyQt4.QtCore import pyqtSignal, Qt
import os
import Strings
from gui import SubmitMoveButton, SquarePixmapLabel, YourTurnDialog


class GameBoard(QWidget):
    CurrentTurnSignal = pyqtSignal()

    def __init__(self, main_window):
        super(GameBoard, self).__init__()
        self.main_window = main_window
        self.main_window.RESIZE.connect(self.resize_of_main_win_event)

        self.game_board = SquarePixmapLabel(self)
        self.game_board.setMinimumSize(1, 1)
        self.game_board.setGeometry(0, 0, 600, 600)
        self.game_board.setScaledContents(True)
        self.board_pixmap = QPixmap(os.path.join(Gl.Graphics, "Board1080Wood.png"))
        self.game_board.setPixmap(self.board_pixmap)

        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)
        self.grid.addWidget(self.game_board, 0, 0, 10, 10)

        submit_moves = SubmitMoveButton(self.main_window)
        self.grid.addWidget(submit_moves, 9, 7, 1, 2)
        submit_moves.clicked.connect(self.on_submit_moves)

        self.turn_label = QLabel(Strings.Turn_Labels[Gl.Current_Turn].format("_____"), self)
        self.turn_label.setMinimumSize(1, 1)
        self.turn_label.setTextFormat(Qt.RichText)
        self.grid.addWidget(self.turn_label, 9, 1, 1, 6)

        self.setLayout(self.grid)

    def load_pieces(self, pieces):
        for x, row in enumerate(pieces):
            for y, piece in enumerate(row):
                piece.setParent(self)
                self.grid.addWidget(piece, y, x)

    def heightForWidth(self, p_int):
        return p_int

    def resize_of_main_win_event(self):
        main_win_size = self.main_window.size()
        m = min(main_win_size.height(), main_win_size.width())
        self.setMaximumSize(m, m)

    def set_current_turn(self):
        if Gl.ColorIAm != Gl.Current_Turn:
            self.turn_label.setText(Strings.Turn_Labels[Gl.Current_Turn].format(Gl.PartnerName))
        else:
            self.turn_label.setText(Strings.Turn_Labels[Gl.Current_Turn].format(Gl.Name))
            if Gl.partnerIP != "Offline":
                YourTurnDialog(self.main_window)

    @staticmethod
    def on_submit_moves():
        Gl.Signals["emptySpaceDoubleClicked"].emit(False)
