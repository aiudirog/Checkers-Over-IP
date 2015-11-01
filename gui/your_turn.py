from PyQt4.QtGui import QDialog, QVBoxLayout, QPalette, QLabel, QPixmap, QApplication
from PyQt4.QtCore import Qt
import os
from time import sleep
import Globals as Gl


class YourTurnDialog(QDialog):
    def __init__(self, parent):
        super(YourTurnDialog, self).__init__(parent=parent, flags=Qt.FramelessWindowHint)
        self.need_hide = False
        self.setBackgroundRole(QPalette.Base)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        main_layout = QVBoxLayout()

        your_turn_pixmap = QPixmap(os.path.join(Gl.Graphics, "Your_Turn.png"))
        label = QLabel()
        label.setPixmap(your_turn_pixmap)

        main_layout.addWidget(label)
        self.setLayout(main_layout)
        self.setWindowModality(Qt.NonModal)

        self.show()

    # noinspection PyArgumentList
    def show(self):
        super(YourTurnDialog, self).show()
        for i in range(15):
            QApplication.processEvents()
            sleep(0.1)
            if self.need_hide:
                self.need_hide = False
                self.hide()
                return
        self.hide()

    def mousePressEvent(self, event=None):
        self.need_hide = True
