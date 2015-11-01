import Globals as Gl
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QCheckBox, \
                        QDialog, QPushButton
import os
import Strings


# noinspection PyUnresolvedReferences
class GetIPDialog(QDialog):
    def __init__(self):
        super(GetIPDialog, self).__init__()

        # Create UI
        if Gl.NoInternet:
            title = Strings.NoInternetTitle
            string = Strings.NoInternetText
        else:
            title = Strings.IPAddressRequestTitle
            string = Strings.IPAddressRequest.format(Gl.myIP)
        self.text = string
        grid = QGridLayout(self)
        self.NameEdit = QLineEdit(self)
        self.NameEdit.setPlaceholderText(Strings.PlaceHolderName)
        self.IPEdit = QLineEdit(self)
        self.IPEdit.setPlaceholderText(Strings.PlaceHolderIPEnter)
        self.Label = QLabel(self.text)
        self.BeServer = QCheckBox(Strings.BeServer, self)
        self.PlayOffline = QCheckBox(Strings.PlayOffline, self)
        grid.addWidget(self.Label, 0, 0, 1, 3)
        grid.addWidget(self.NameEdit, 1, 0, 1, 3)
        grid.addWidget(self.IPEdit, 2, 0, 1, 3)
        grid.addWidget(self.BeServer, 3, 0, 1, 2)
        grid.addWidget(self.PlayOffline, 4, 0, 1, 2)

        self.BeServer.stateChanged.connect(self.check_box)
        self.PlayOffline.stateChanged.connect(self.offline)

        ok = QPushButton("Submit", self)
        ok.clicked.connect(self.accept)

        grid.addWidget(ok, 5, 2, 1, 1)
        self.setLayout(grid)

        self.setWindowTitle(title)

        if os.path.isfile(Gl.LastConnectionFile):
            with open(Gl.LastConnectionFile, "r") as f:
                self.NameEdit.setText(f.readline()[:-1])
                self.IPEdit.setText(f.readline())

    def check_box(self):
        self.IPEdit.setEnabled(not self.BeServer.isChecked())

    def offline(self):
        self.IPEdit.setEnabled(not self.PlayOffline.isChecked())
        self.BeServer.setEnabled(not self.PlayOffline.isChecked())
        if self.PlayOffline.isChecked():
            self.text = Strings.PlayOfflineText
        else:
            self.text = Strings.IPAddressRequest.format(Gl.myIP)
        self.Label.setText(self.text)

    def get_text(self, text=False):
        if text:
            self.Label.setText(self.text + text)
        else:
            self.Label.setText(self.text)
        ok = self.exec_()
        name = self.NameEdit.text()
        if self.PlayOffline.isChecked():
            ip = "Offline"
        elif self.BeServer.isChecked():
            ip = "Server"
        else:
            ip = self.IPEdit.text()
        return name, ip, ok

    def set_offline(self, state):
        self.PlayOffline.setChecked(state)