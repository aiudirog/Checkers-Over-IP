# Messenger.py
from Globals import *
import Globals
from random import randint
import Strings

class messenger(QWidget):
    SendMessage = pyqtSignal(object,object)
    ReceiveMessage = pyqtSignal(object,object)
    
    def __init__(self):
        super(messenger, self).__init__()
        self.addSignalsToGlobals()
        self.initUI()
        
    def initUI(self):
        self.Grid = QGridLayout()
        self.Grid.setContentsMargins(0,0,0,0)
        self.Grid.setSpacing(0)
        
        BackGround = QLabel(self)
        BackGround.setMinimumSize(1,1)
        BackGround.setScaledContents(True)
        BackGround.setPixmap(QPixmap(os.path.join(Graphics,"Messenger.png")))
        self.Grid.addWidget(BackGround,0,0,25,1)
        
        self.VBox = QVBoxLayout()
        self.VBox.setContentsMargins(2,2,2,2)
        self.VBox.setSpacing(0)
        
        self.Grid.addLayout(self.VBox,2,0,25,1)
        
        self.ScrolledArea = QScrollArea(self)
        self.ScrolledArea.verticalScrollBar().rangeChanged.connect(self.Scroll)
        self.displayMessages = messageDisplay()
        self.ScrolledArea.setWidget(self.displayMessages)
        self.ScrolledArea.setWidgetResizable(True)
        self.ScrolledArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.VBox.addWidget(self.ScrolledArea,10)
        
        self.messageBox = textField()
        self.VBox.addWidget(self.messageBox,1)
        
        self.setLayout(self.Grid) 

    def addSignalsToGlobals(self):
        Signals["SendMessage"] = self.SendMessage
        Signals["ReceiveMessage"] = self.ReceiveMessage
        
    
    def Scroll(self,y0,y1):
        vbar = self.ScrolledArea.verticalScrollBar()
        vbar.setValue(vbar.maximum())


class textField(QWidget):
    def __init__(self):
        super(textField, self).__init__()
        self.initUI()
        
    def initUI(self):
        mainHBox = QHBoxLayout()
        mainHBox.setContentsMargins(2,2,2,2)
        mainHBox.setSpacing(0)
        
        self.TextEdit = textBox(self)
        self.TextEdit.Enter.connect(self.SendMessage)
        mainHBox.addWidget(self.TextEdit,10)
        
        sendButton = QPushButton('S\ne\nn\nd', self)
        sendButton.setToolTip(Strings.SendButtonToolTip)
        mainHBox.addWidget(sendButton, 1)
        sendButton.clicked.connect(self.SendMessage)
        
        self.setLayout(mainHBox)
    
    def SendMessage(self, event=None):
        text = self.TextEdit.toPlainText()
        if text == "":
            return
        Signals["SendMessage"].emit(Globals.Name,text)
        self.TextEdit.clear()
        
class textBox(QTextEdit):
    Enter = pyqtSignal()
    
    def __init__(self,parent):
        super(textBox, self).__init__(parent)
        self.setToolTip(Strings.MessegeBoxToolTip)
        
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Return:
            if event.modifiers() == Qt.ShiftModifier:
                QTextEdit.keyPressEvent(self,  event)
            else:
                self.Enter.emit()
                return
        QTextEdit.keyPressEvent(self,  event)
        
class messageDisplay(QWidget):
    colors = ['black', 'blue', 'fuchsia',
              'maroon', 'navy', 'purple', 'red']
    NamesAndColors = {}
    
    def __init__(self):
        super(messageDisplay, self).__init__()
        self.initUI()
        
    def initUI(self):
        
        self.mainVBox = QVBoxLayout(self)
        self.mainVBox.setContentsMargins(2,2,2,2)
        self.mainVBox.setSpacing(4)
        
        self.setLayout(self.mainVBox)
        
        Signals["ReceiveMessage"].connect(self.receiveMessage)
        
    def receiveMessage(self, name, msg):
        self.addMessage(name, msg)
    
    def addMessage(self, name, message):
        if name not in self.NamesAndColors:
            color = self.colors[randint(0,len(self.colors)-1)]
            self.colors.remove(color)
            self.NamesAndColors[name] = color
        msg = QLabel('<font size="4" color={2}>{0}: {1}</font>'.format(name, message, self.NamesAndColors[name]), self)
        msg.setWordWrap(True)
        self.mainVBox.addWidget(msg)









