# GUI.py

from Globals import *
import Globals
from ServerClient import CheckersServer, MessengerServer
from Messenger import messenger
import Strings
from time import sleep


class Window(QWidget):
    SendMove = pyqtSignal(object,object)
    ExecuteMove = pyqtSignal(object,object)
    CannotConnectSignal = pyqtSignal()
    ServerFirst = pyqtSignal()
    RESET = pyqtSignal()
    
    def __init__(self, screenHeight):
        super(Window, self).__init__()
        self.width, self.height = 900, 600
        self.screenHeight = screenHeight
        self.initUI()

    def initUI(self):
        Globals.Signals["SendMove"] = self.SendMove
        Globals.Signals["ExecuteMove"] = self.ExecuteMove
        Globals.Signals["CannotConnectSignal"] = self.CannotConnectSignal
        Globals.Signals["ServerFirst"] = self.ServerFirst
        Globals.Signals["RESET"] = self.RESET
        
        Globals.Signals["CannotConnectSignal"].connect(self.CannotConnect)
        
        self.mainHBox = QHBoxLayout()
        self.mainHBox.setContentsMargins(0,0,0,0)
        self.mainHBox.setSpacing(0)
        self.gameBoard = gameBoard(self)
        self.mainHBox.addWidget(self.gameBoard,2)
        
        self.messager = messenger()
        self.mainHBox.addWidget(self.messager,1)
        
        self.setLayout(self.mainHBox) 
        self.setGeometry(300, 100, self.width, self.height)
        self.setWindowTitle(Strings.Title)
        self.setWindowIcon(Globals.AppIcon)
        self.show()
        self.requestText = Strings.IPAddressRequest.format(myIP)
        name, Globals.partnerIP = self.GetPartnerIP()
        if ":" in name:
            Globals.Name, Globals.PartnerName = name.split(":")[:2]
        else:
            Globals.Name = name
        if len(Globals.partnerIP.split(".")) == 4:
            if not os.path.isdir(Globals.basePath):
                os.makedirs(Globals.basePath)
            with open(LastConnectionFile,"w") as f:
                f.write(Globals.Name+"\n"+Globals.partnerIP)
        self.GameServer = CheckersServer(self)
        self.GameServer.start()
        MessengerServer(self).start()
        
    def GetPartnerIP(self):
        text = ""
        if Globals.NoInternet:
            title = Strings.NoInternetTitle
            string = Strings.NoInternetText
        else:
            title = Strings.IPAddressRequestTitle
            string = self.requestText
        dialog = GetIPDialog(title, string)
        dialog.setOffline(Globals.NoInternet)
        while True:
            name, ip, ok = dialog.getText()
            if not bool(ok):
                qApp.closeAllWindows()
                QApplication.quit()
                sys.exit()
            if ip == "test" or ip == "Server" or ip == "Offline":
                return name, ip
            if len(ip.split(".")) != 4:
                text = Strings.InvalidIPAddress
                name, ip, ok = dialog.getText(text)
            if ok != 0:
                if len(ip.split(".")) != 4:
                    text = Strings.InvalidIPAddress
                    continue
            else:
                text = ""
                continue
            return name, ip
        
    def resizeEvent(self, event):
        new_width = event.size().width()
        new_height = event.size().height()
        if new_height >= self.screenHeight:
            new_size = QSize(self.screenHeight*(1.5), self.screenHeight)
        else:
            new_size = QSize(new_width, new_width*(1/1.5))

        self.width = new_size.width()
        self.height = new_size.height()
        self.setGeometry(self.geometry().x(), self.geometry().y(), new_size.width(), new_size.height())
        
    def CannotConnect(self, event=None):
        Message = QMessageBox()
        Message.setWindowTitle(Strings.CannotConnectTitle)
        Message.setText(Strings.CannotConnect)
        Message.setTextFormat(Qt.RichText)
        Message.exec_()
        self.close()

class gameBoard(QWidget):
    CurrentTurnSignal = pyqtSignal()
    def __init__(self, MainWindow):
        super(gameBoard, self).__init__()
        self.MainWindow = MainWindow
        self.initUI()
        
    def initUI(self):
        self.board = QLabel(self)
        self.board.setMinimumSize(1,1)
        self.board.setGeometry(0, 0, 600, 600)
        self.board.setScaledContents(True)
        self.boardPixMap = QPixmap(os.path.join(Graphics,"Board1080.png"))
        self.board.setPixmap(self.boardPixMap)
        
        self.Grid = QGridLayout()
        self.Grid.setContentsMargins(0,0,0,0)
        self.Grid.setSpacing(0)
        self.Grid.addWidget(self.board, 0, 0, 10, 10)
        
        submitButton = SubmitMoveButton()
        self.Grid.addWidget(submitButton, 9, 7, 1, 2)
        submitButton.clicked.connect(self.SendMovesToServer)
        
        self.CurrentTurn = 0
        self.TurnLabel = QLabel(Strings.Turn_Labels[self.CurrentTurn].format("_____"), self)
        self.TurnLabel.setTextFormat(Qt.RichText)
        self.Grid.addWidget(self.TurnLabel, 9, 1, 2, 6)
        
        self.SelectedMoves = []
        self.piecesToRemove = []
        self.emptyBoardSpacesType = type(emptyBoardSpaces())
        self.checkerPieceType = type(checkerPiece())
        
        self.gamePieces = pieces()
        self.refreshPieces()
        self.registerPieceSelections()
        self.TurnsSinceLastTake = 0
        
        Globals.Signals["ExecuteMove"].connect(self.executeMove)
        Globals.Signals["RESET"].connect(self.RESET)
        self.CurrentTurnSignal.connect(self.setCurrentTurn)
        Globals.Signals["CurrentTurnSignal"] = self.CurrentTurnSignal
        
        self.setLayout(self.Grid)
    
    def setCurrentTurn(self):
        if Globals.ColorIAm != self.CurrentTurn:
            self.TurnLabel.setText(Strings.Turn_Labels[self.CurrentTurn].format(Globals.PartnerName))
        else:
            self.TurnLabel.setText(Strings.Turn_Labels[self.CurrentTurn].format(Globals.Name))
    
    def executeMove(self, submitList, piecesToRemove):
        self.SelectedMoves = []
        for item in submitList:
            self.SelectedMoves.append(self.gamePieces.Manager[item[0]][item[1]])
        self.piecesToRemove = piecesToRemove
        self.executeSelectedMoves()
    
    def registerPieceSelections(self):
        for row in self.gamePieces.Manager:
            for piece in row:
                if piece:
                    piece.PieceSelected.connect(self.handlePieceSelection)
                if type(piece) == self.emptyBoardSpacesType:
                    piece.SubmitMove.connect(self.SendMovesToServer)
    
    def refreshPieces(self):
        for y, row in enumerate(self.gamePieces.Manager):
            for x, piece in enumerate(row):
                if piece:
                    self.Grid.addWidget(piece, x, y)
                    
    def printCheckGrid(self):
        for row in self.gamePieces.Manager:
            for n in row:
                if n is not False:
                    print(n.color, end="\t")
            print("\n")
    
    def handlePieceSelection(self, args):
        selected = args[0]
        type_ = args[1]
        object_ = args[2]
        #Only move your piece
        if type_ == self.checkerPieceType:
            if object_.color == "Black" and Red_Turn == self.CurrentTurn:
                object_.Deselect()
                return
            if object_.color == "Red" and Black_Turn == self.CurrentTurn:
                object_.Deselect()
                return
        #If piece is deselected, remove all moves
        if selected is False and type_ == self.checkerPieceType:
            self.ResetSelectedMoves()
            return
        #If no piece is selected
        if len(self.SelectedMoves) == 0:
            #Don't select spaces if ^
            if type_ == self.emptyBoardSpacesType:
                object_.Deselect()
            #Set piece as active
            self.SelectedMoves.append(object_)
            return
        else:
            #Selecting another checker resets moves
            if type_ == self.checkerPieceType:
                self.ResetSelectedMoves()
                self.SelectedMoves.append(object_)
                return
            #If space was deselected, remove all moves after
            if selected is False:
                index = self.SelectedMoves.index(object_)
                for space in self.SelectedMoves[index:]:
                    space.Deselect()
                    self.SelectedMoves.pop(index)
                return
            #Check if move is allowed
            allowed, removePiece = self.CheckViableMove(object_)
            if allowed:
                self.SelectedMoves.append(object_)
            else:
                object_.Deselect()
                return
            if removePiece != False:
                self.piecesToRemove.append(removePiece)

    def executeSelectedMoves(self, event=None):
        if len(self.SelectedMoves) < 2:
            return False
        if len(self.piecesToRemove) > 0:
            self.TurnsSinceLastTake = 0
        else:
            if self.SelectedMoves[0].isKing:
                self.TurnsSinceLastTake += 1
            else:
                self.TurnsSinceLastTake = 0
        for pieceToRemove in self.piecesToRemove:
            self.Grid.removeWidget(self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]])
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].parent = None
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].deleteLater()
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]] = emptyBoardSpaces()
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].PieceSelected.connect(self.handlePieceSelection)
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].SubmitMove.connect(self.SendMovesToServer)
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].setXY(pieceToRemove[0], pieceToRemove[1])
        
        color = self.SelectedMoves[0].color
        
        self.gamePieces.movePiece(self.SelectedMoves[0].x, self.SelectedMoves[0].y, self.SelectedMoves[-1].x, self.SelectedMoves[-1].y)
        if self.SelectedMoves[0].y == 1 and self.SelectedMoves[0].color == "Red":
            self.SelectedMoves[0].setKing()
        elif self.SelectedMoves[0].y == 8 and self.SelectedMoves[0].color == "Black":
            self.SelectedMoves[0].setKing()
        self.refreshPieces()
        self.ResetSelectedMoves()
        
        self.ChangeTurn()
        #Check win/loss only if this call came from the opponent
        if Globals.ColorIAm == Red_Turn and color != "Red":
            self.CheckWinLoss()
        if Globals.ColorIAm == Black_Turn and color != "Black":
            self.CheckWinLoss()
        return True
        
    def CheckViableMove(self, space):
        currentPosX = self.SelectedMoves[-1].x
        currentPosY = self.SelectedMoves[-1].y
        PieceType = self.SelectedMoves[0].color
        isKing = self.SelectedMoves[0].isKing
        removePiece = False
        #print("Current position is ",currentPosX,currentPosY)
        #print("New position is ",space.x,space.y)
        #Make sure movement is on a diagnol
        if space.x == currentPosX or space.y == currentPosY:
            #print("No diagnol movement")
            return (False, removePiece)
        if abs(space.x-currentPosX) != abs(space.y-currentPosY):
            #print("No diagnol movement")
            return (False, removePiece)
        #Single moves greater than 2 are illegal
        if abs(space.x-currentPosX) > 2:
            #print("More than two spaces of movement.")
            return (False, removePiece)
        #Make sure we're moving in the right direction
        if isKing == False:
            if PieceType == "Red":
                if space.y > currentPosY:
                    #print("You can't go backwards.")
                    return (False, removePiece)
            elif PieceType == "Black":
                if space.y < currentPosY:
                    #print("You can't go backwards.")
                    return (False, removePiece)
        #Check for jumping
        if abs(space.x-currentPosX) == 2:
            checkX, checkY = int((space.x+currentPosX)/2), int((space.y+currentPosY)/2)
            if type(self.gamePieces.Manager[checkX][checkY]) != self.checkerPieceType:
                #print("You can't move two blocks at a time without taking a piece.")
                return (False, removePiece)
            else:
                if self.gamePieces.Manager[checkX][checkY].color == PieceType:
                    #print("You can't jump your own pieces.")
                    return (False, removePiece)
                removePiece = (checkX, checkY)
        if len(self.piecesToRemove) != 0 and removePiece == False:
            return (False, removePiece)
        if len(self.SelectedMoves) == 2 and removePiece == False:
            return (False, removePiece)
        return (True, removePiece)
    
    def ResetSelectedMoves(self):
        for space in self.SelectedMoves[1:]:
            space.Deselect()
        if self.SelectedMoves[0].Selected:
            self.SelectedMoves[0].Deselect()
        self.SelectedMoves = []
        self.piecesToRemove = []
    
    def ChangeTurn(self):
        if self.CurrentTurn == Red_Turn:
            self.CurrentTurn = Black_Turn
        else:
            self.CurrentTurn = Red_Turn
        self.setCurrentTurn()
    
    def CheckWinLoss(self):
        Moves = {"Red":0,"Black":0}
        Checkers = {"Red":0,"Black":0}
        for x, row in enumerate(self.gamePieces.Manager):
            for y, piece in enumerate(row):
                if type(piece) == self.checkerPieceType:
                    Checkers[piece.color] += 1
                    x = piece.x
                    y = piece.y
                    if piece.isKing or piece.color == "Black":
                        if type(self.gamePieces.Manager[x+1][y+1]) == self.emptyBoardSpacesType:
                            Moves[piece.color] += 1
                        elif self.gamePieces.Manager[x+1][y+1] != False:
                            if x+2 <= 9:
                                if type(self.gamePieces.Manager[x+2][y+2]) == self.emptyBoardSpacesType:
                                    Moves[piece.color]+=1
                        if type(self.gamePieces.Manager[x-1][y+1]) == self.emptyBoardSpacesType:
                            Moves[piece.color] += 1
                        elif self.gamePieces.Manager[x-1][y+1] != False:
                            if x-2 > 0 and y+2 <= 9:
                                if type(self.gamePieces.Manager[x-2][y+2]) == self.emptyBoardSpacesType:
                                    Moves[piece.color] += 1
                    if piece.isKing or piece.color == "Red":
                        if type(self.gamePieces.Manager[x-1][y-1]) == self.emptyBoardSpacesType:
                            Moves[piece.color] += 1
                        elif self.gamePieces.Manager[x-1][y-1] != False:
                            if x-2 > 0:
                                if type(self.gamePieces.Manager[x-2][y-2]) == self.emptyBoardSpacesType:
                                    Moves[piece.color]+=1
                        if type(self.gamePieces.Manager[x+1][y-1]) == self.emptyBoardSpacesType:
                            Moves[piece.color] += 1
                        elif self.gamePieces.Manager[x+1][y-1] != False:
                            if x+2 <= 9 and y-2 > 0:
                                if type(self.gamePieces.Manager[x+2][y-2]) == self.emptyBoardSpacesType:
                                    Moves[piece.color] += 1
        if self.TurnsSinceLastTake > 40:
            if Checkers["Black"] == Checkers["Red"]:
                self.EndGame(Strings.Stalemate.format(self.TurnsSinceLastTake))
            elif Checkers["Black"] > Checkers["Red"]:
                self.EndGame(Strings.BlackWinsStalemate.format(self.TurnsSinceLastTake))
            else:
                self.EndGame(Strings.RedWinsStalemate.format(self.TurnsSinceLastTake))
        elif Moves["Red"] == 0:
            self.EndGame(Strings.BlackWinsNoMoreMoves)
        elif Moves["Black"] == 0:
            self.EndGame(Strings.RedWinsNoMoreMoves)
        elif Checkers["Red"] == 0:
            self.EndGame(Strings.BlackWins)
        elif Checkers["Black"] == 0:
            self.EndGame(Strings.RedWins)

    def EndGame(self, Text):
        Message = QMessageBox(self.MainWindow)
        Message.setWindowTitle(Strings.GameOverTitle)
        Message.setText(Text)
        Message.setTextFormat(Qt.RichText)
        Message.setWindowModality(Qt.NonModal)
        Message.setModal(False)
        Message.show()
        QApplication.processEvents()
        Globals.Signals["RESET"].emit()
        
    def SendMovesToServer(self, event=None):
        if len(self.SelectedMoves) < 2:
            return
        submitList = []
        for item in self.SelectedMoves:
            submitList.append((item.x,item.y))
        removePiecesCopy = self.piecesToRemove.copy()
        if self.executeMove(submitList,self.piecesToRemove) != False:
            Globals.Signals["SendMove"].emit(submitList,removePiecesCopy)
        self.CheckWinLoss()
        
    def RESET(self):
        sleep(3)
        for row in self.gamePieces.Manager:
            for piece in row:
                if piece:
                    self.Grid.removeWidget(piece)
                    piece.parent = None
                    piece.deleteLater()
                    del piece
        self.SelectedMoves = []
        self.piecesToRemove = []
        self.gamePieces = pieces()
        self.refreshPieces()
        self.registerPieceSelections()
        self.TurnsSinceLastTake = 0
        Globals.ColorIAm = int(not Globals.ColorIAm)
        self.CurrentTurn = 0
        self.setCurrentTurn()
        if Globals.Type == "Client" and self.CurrentTurn != Globals.ColorIAm:
            Globals.Signals["ServerFirst"].emit()
        QApplication.processEvents()
        
class checkerPiece(QLabel):
    PieceSelected = pyqtSignal(object)

    def __init__(self, color="Black", x=1, y=1):
        super(checkerPiece, self).__init__()
        self.x = x
        self.y = y
        self.isKing = False
        #Get path to image for piece
        self.UnselectedPixmap = QPixmap(os.path.join(Graphics,"{0}_Piece.png".format(color)))
        self.SelectedPixmap = QPixmap(os.path.join(Graphics,"{0}_Piece_Selected.png".format(color)))
        #Save color
        self.color = color
        self.setMinimumSize(1,1)
        self.setScaledContents(True)
        self.setPixmap(self.UnselectedPixmap)
        
        self.Selected = False
    
    def mouseReleaseEvent(self, event):
        if Globals.partnerIP == "Offline":
            self.ChangeSelected(event)
            return
        #Prevent selection if it isn't your turn
        if Globals.ColorIAm == Red_Turn and self.color != "Red":
            return
        if Globals.ColorIAm == Black_Turn and self.color != "Black":
            return
        #Select the piece
        self.ChangeSelected(event)
        
    def ChangeSelected(self, event=None):
        if self.Selected:
            self.Selected = False
        else:
            self.Selected = True
        self.ChangeImageOnClick(event)
    
    def ChangeImageOnClick(self, event):
        if self.Selected:
            self.setPixmap(self.SelectedPixmap)
        else:
            self.setPixmap(self.UnselectedPixmap)
        if event != None:
            self.PieceSelected.emit((self.Selected, type(self), self))
    
    def Deselect(self):
        self.Selected = False
        self.ChangeImageOnClick(None)
        
    def Select(self):
        self.Selected = True
        self.ChangeImageOnClick(None)
    
    def setXY(self, x, y):
        self.x = x
        self.y = y
        
    def setKing(self):
        self.isKing = True
        self.UnselectedPixmap = QPixmap(os.path.join(Graphics,"{0}_Piece_King.png".format(self.color)))
        self.SelectedPixmap = QPixmap(os.path.join(Graphics,"{0}_Piece_Selected_King.png".format(self.color)))
        self.ChangeImageOnClick(None)
        
class emptyBoardSpaces(checkerPiece):
    SubmitMove = pyqtSignal()
    
    def __init__(self, x=1, y=2):
        super(emptyBoardSpaces, self).__init__(color=None, x=x, y=y)
        #Get path to image for piece
        self.UnselectedPixmap = QPixmap(os.path.join(Graphics,"clear.png"))
        self.SelectedPixmap = QPixmap(os.path.join(Graphics,"clear_Selected.png"))
        #Build the widget that will be displayed
        self.setMinimumSize(1,1)
        self.setScaledContents(True)
        self.setPixmap(self.SelectedPixmap)
        self.setPixmap(self.UnselectedPixmap)
        
        #self.setToolTip("Double click to move here")
        
        self.Selected = False
    
    def mouseDoubleClickEvent(self, event):
        self.SubmitMove.emit()
    
    def mouseReleaseEvent(self, event):
        self.ChangeSelected(event)
            
class pieces():
    def __init__(self):
        #Define a two dimensional list to handle piece locations
        self.Manager = []
        falseList = [False]*10
        for _n in range(10):
            self.Manager.append(falseList.copy())
        #Add black pieces
        x,y = 1,1
        color = "Black"
        for _n in range(12):
            self.Manager[x][y] = checkerPiece(color,x,y)
            x,y = self.increment(x,y)
        #Add red piece
        x,y = 2,6
        color = "Red"
        for _n in range(12):
            self.Manager[x][y] = checkerPiece(color,x,y)
            x,y = self.increment(x,y)
        for x, row in enumerate(self.Manager):
            if x == 0 or x == 9:
                continue
            for y, space in enumerate(row):
                if y == 0 or y == 9:
                    continue
                if space is False:
                    self.Manager[x][y] = emptyBoardSpaces(x,y)
                    
    def increment(self,x,y):
        x += 2
        if x == 9:
            y += 1
            x = 2
        elif x == 10:
            y += 1
            x = 1
        return x,y
    
    def movePiece(self, old_x, old_y, new_x, new_y):
        self.Manager[old_x][old_y], self.Manager[new_x][new_y] = self.Manager[new_x][new_y], self.Manager[old_x][old_y]
        self.Manager[old_x][old_y].setXY(old_x, old_y)
        self.Manager[new_x][new_y].setXY(new_x, new_y)

class SubmitMoveButton(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self):
        super(SubmitMoveButton, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setToolTip(Strings.SubmitMoveToolTip)
        self.Up = QPixmap(os.path.join(Graphics,"SubmitMoveButton.png"))
        self.Down = QPixmap(os.path.join(Graphics,"SubmitMoveButtonSelected.png"))
        self.setMinimumSize(1,1)
        self.setScaledContents(True)
        self.setPixmap(self.Up)
        
    def mouseReleaseEvent(self, event):
        self.setPixmap(self.Up)
        self.clicked.emit()
    
    def mousePressEvent(self, event):
        self.setPixmap(self.Down)
        
class GetIPDialog(QDialog):
    def __init__(self, title, text):
        super(GetIPDialog, self).__init__()
        self.setWindowTitle(title)
        
        self.initUI(text)
    
    def initUI(self, text):
        self.text = text
        Grid = QGridLayout(self)
        self.NameEdit = QLineEdit(self)
        self.NameEdit.setPlaceholderText(Strings.PlaceHolderName)
        self.IPEdit = QLineEdit(self)
        self.IPEdit.setPlaceholderText(Strings.PlaceHolderIPEnter)
        self.Label = QLabel(text)
        self.BeServer = QCheckBox(Strings.BeServer, self)
        self.PlayOffline = QCheckBox(Strings.PlayOffline, self)
        Grid.addWidget(self.Label,0,0,1,3)
        Grid.addWidget(self.NameEdit,1,0,1,3)
        Grid.addWidget(self.IPEdit,2,0,1,3)
        Grid.addWidget(self.BeServer,3,0,1,2)
        Grid.addWidget(self.PlayOffline,4,0,1,2)
        
        self.BeServer.stateChanged.connect(self.CheckBox)
        self.PlayOffline.stateChanged.connect(self.Offline)
        
        Ok = QPushButton("Submit",self)
        Ok.clicked.connect(self.accept)
        
        Grid.addWidget(Ok,5,2,1,1)
        self.setLayout(Grid)
        
        if os.path.isfile(LastConnectionFile):
            with open(LastConnectionFile, "r") as f:
                self.NameEdit.setText(f.readline()[:-1])
                self.IPEdit.setText(f.readline())
        
    def CheckBox(self, event=None):
        self.IPEdit.setEnabled(not self.BeServer.isChecked())
    
    def Offline(self, event=None):
        self.IPEdit.setEnabled(not self.PlayOffline.isChecked())
        self.BeServer.setEnabled(not self.PlayOffline.isChecked())
    
    def getText(self, text=False):
        if text:
            self.Label.setText(self.text+text)
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
    
    def setOffline(self, state):
        self.PlayOffline.setChecked(state)
        
        
    




