import Strings
from PyQt4.QtGui import QPixmap, QLabel
from PyQt4.QtCore import pyqtSignal
import Globals as Gl
import os


class SubmitMoveButton(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent):
        super(SubmitMoveButton, self).__init__(parent)
        self.setToolTip(Strings.SubmitMoveToolTip)
        self.setScaledContents(True)
        self.up = QPixmap(os.path.join(Gl.Graphics, "SubmitMoveButton.png"))
        self.down = QPixmap(os.path.join(Gl.Graphics, "SubmitMoveButtonSelected.png"))
        self.setMinimumSize(1, 1)
        self.setPixmap(self.up)

    def mouseReleaseEvent(self, event=None):
        self.setPixmap(self.up)
        self.clicked.emit()

    def mousePressEvent(self, event=None):
        self.setPixmap(self.down)