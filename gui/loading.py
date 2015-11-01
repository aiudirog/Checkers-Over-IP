import Globals as Gl
from PyQt4.QtGui import QLabel, QDialog, QVBoxLayout, QMovie, QApplication
from PyQt4.QtCore import Qt
import os


# noinspection PyUnresolvedReferences
class Loading(QDialog):
    def __init__(self, parent, text=""):
        super(Loading, self).__init__(parent)

        self.setStyleSheet("background-color:white;")
        Gl.Signals["changeLoadingText"].connect(self.change_text)
        Gl.Signals["endLoading"].connect(self.on_end)
        self.setWindowTitle("Please wait")

        # Credit to zegerdon on DeviantArt for his loading gif.
        self.load_gif = QMovie(os.path.join(Gl.Graphics, "loading_by_zegerdon-deviantart.gif"))
        self.load_label = QLabel()
        self.load_label.setMovie(self.load_gif)

        self.text = QLabel(text)
        self.text.setStyleSheet("QLabel { color : black; }")

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.load_label)
        self.vbox.setAlignment(self.load_label, Qt.AlignCenter)
        self.vbox.addWidget(self.text)
        self.vbox.setAlignment(self.text, Qt.AlignCenter)
        self.vbox.setMargin(20)
        self.vbox.setSpacing(30)

        self.setLayout(self.vbox)

        self.load_gif.start()

        self.end_loading = False

    def change_text(self, string):
        self.text.setText(string)

    def on_end(self):
        """
        Close on signal.

        :return:
        """
        self.end_loading = True
        self.close()

    # noinspection PyArgumentList
    def closeEvent(self, close_event):
        """
        If closed by user, exit program.

        :return:
        """
        if self.end_loading:
            super(Loading, self).close()
        else:
            Gl.Signals["KILL"].emit()
            QApplication.processEvents()

