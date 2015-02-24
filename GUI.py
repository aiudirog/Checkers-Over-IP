# GUI.py
from Globals import *
import Globals
import os
import sys
from random import randint
from ServerClient import serverAndClient
from Messenger import messenger
import Strings

class Window(QWidget):
    SendMove = pyqtSignal(object,object)
    ExecuteMove = pyqtSignal(object,object)
    
    def __init__(self, screenHeight):
        super(Window, self).__init__()
        self.width, self.height = 900, 600
        self.screenHeight = screenHeight
        self.initUI()

    def initUI(self):
        mainHBox = QHBoxLayout()
        mainHBox.setContentsMargins(0,0,0,0)
        mainHBox.setSpacing(0)
        self.gameBoard = gameBoard(self)
        mainHBox.addWidget(self.gameBoard,2)
        
        self.messager = messenger()
        mainHBox.addWidget(self.messager,1)
        
        self.setLayout(mainHBox) 
        self.setGeometry(300, 100, self.width, self.height)
        self.setWindowTitle(Strings.Title)
        self.setWindowIcon(QIcon(os.path.join(Graphics,'Logo.png')))
        self.show()
        self.requestText = Strings.IPAddressRequest.format(myIP)
        Globals.Name, Globals.partnerIP = self.GetPartnerIP()
        with open(LastConnectionFile,"w") as f:
            f.write(Globals.Name+"\n"+Globals.partnerIP)
        serverAndClient(self).start()
        
    def GetPartnerIP(self):
        text = ""
        while True:
            dialog = GetIPDialog(Strings.IPAddressRequestTitle, self.requestText)
            name, ip, ok = dialog.getText()
            if ip == "test":
                return name, ip
            while ok == 0:
                name, ip, ok = dialog.getText(text)
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

class gameBoard(QWidget):
    CurrentTurnSignal = pyqtSignal(object)
    Black_Turn = 0
    Red_Turn = 1
    
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
        self.Grid.addWidget(submitButton, 9, 6, 1, 3)
        submitButton.clicked.connect(self.SendMovesToServer)
        
        self.CurrentTurn = 0
        self.TurnLabel = QLabel(Strings.Turn_Labels[self.CurrentTurn], self)
        self.TurnLabel.setTextFormat(Qt.RichText)
        self.Grid.addWidget(self.TurnLabel, 9, 1, 2, 4)
        
        self.SelectedMoves = []
        self.piecesToRemove = []
        self.emptyBoardSpacesType = type(emptyBoardSpaces())
        self.checkerPieceType = type(checkerPiece())
        
        self.gamePieces = pieces()
        self.refreshPieces()
        self.registerPieceSelections()
        self.TurnsSinceLastTake = 0
        
        self.MainWindow.ExecuteMove.connect(self.executeMove)
        self.CurrentTurnSignal.connect(self.setCurrentTurn)
        
        self.setLayout(self.Grid)
    
    def setCurrentTurn(self, data):
        self.CurrentTurn = data
        self.TurnLabel.setText(Strings.Turn_Labels[self.CurrentTurn])
    
    def executeMove(self, submitList, piecesToRemove):
        self.SelectedMoves = []
        for item in submitList:
            self.SelectedMoves.append(self.gamePieces.Manager[item[0]][item[1]])
        self.piecesToRemove = piecesToRemove
        self.executeSelectedMoves()
    
    def registerPieceSelections(self):
        for y, row in enumerate(self.gamePieces.Manager):
            for x, piece in enumerate(row):
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
            if object_.color == "Black" and self.Red_Turn == self.CurrentTurn:
                object_.Deselect()
                return
            if object_.color == "Red" and self.Black_Turn == self.CurrentTurn:
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
                for n, space in enumerate(self.SelectedMoves[index:]):
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
            return
        if len(self.piecesToRemove) > 0:
            self.TurnsSinceLastTake = 0
        else:
            self.TurnsSinceLastTake += 1
        for pieceToRemove in self.piecesToRemove:
            self.Grid.removeWidget(self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]])
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].parent = None
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].deleteLater()
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]] = emptyBoardSpaces()
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].PieceSelected.connect(self.handlePieceSelection)
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].SubmitMove.connect(self.SendMovesToServer)
            self.gamePieces.Manager[pieceToRemove[0]][pieceToRemove[1]].setXY(pieceToRemove[0], pieceToRemove[1])
        self.gamePieces.movePiece(self.SelectedMoves[0].x, self.SelectedMoves[0].y, self.SelectedMoves[-1].x, self.SelectedMoves[-1].y)
        if self.SelectedMoves[0].y == 1 and self.SelectedMoves[0].color == "Red":
            self.SelectedMoves[0].setKing()
        elif self.SelectedMoves[0].y == 8 and self.SelectedMoves[0].color == "Black":
            self.SelectedMoves[0].setKing()
        self.refreshPieces()
        self.ResetSelectedMoves()
        
        self.ChangeTurn()
        
        self.CheckWinLoss()
        
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
        if self.CurrentTurn == self.Red_Turn:
            self.CurrentTurn = self.Black_Turn
        else:
            self.CurrentTurn = self.Red_Turn
        self.TurnLabel.setText(Strings.Turn_Labels[self.CurrentTurn])
    
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
        if self.TurnsSinceLastTake > 20:
            if Checkers["Black"] == Checkers["Red"]:
                self.EndGame(Strings.Stalemate)
            elif Checkers["Black"] > Checkers["Red"]:
                self.EndGame(Strings.BlackWinsStalemate)
            else:
                self.EndGame(Strings.RedWinsStalemate)
        elif Moves["Red"] == 0:
            self.EndGame(Strings.BlackWinsNoMoreMoves)
        elif Moves["Black"] == 0:
            self.EndGame(Strings.RedWinsNoMoreMoves)
        elif Checkers["Red"] == 0:
            self.EndGame(Strings.BlackWins)
        elif Checkers["Black"] == 0:
            self.EndGame(Strings.RedWins)

    def EndGame(self, Text):
        Message = QMessageBox()
        Message.setWindowTitle(Strings.GameOverTitle)
        Message.setText(Text)
        Message.setTextFormat(Qt.RichText)
        Message.exec_()
        
    def SendMovesToServer(self, event=None):
        if len(self.SelectedMoves) < 2:
            return
        submitList = []
        for item in self.SelectedMoves:
            submitList.append((item.x,item.y))
        self.MainWindow.SendMove.emit(submitList,self.piecesToRemove)

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
            
class pieces():
    def __init__(self):
        #Define a two dimensional list to handle piece locations
        self.Manager = []
        falseList = [False]*10
        for n in range(10):
            self.Manager.append(falseList.copy())
        #Add black pieces
        x,y = 1,1
        color = "Black"
        for n in range(12):
            self.Manager[x][y] = checkerPiece(color,x,y)
            x,y = self.increment(x,y)
        #Add red piece
        x,y = 2,6
        color = "Red"
        for n in range(12):
            self.Manager[x][y] = checkerPiece(color,x,y)
            x,y = self.increment(x,y)
        for x, row in enumerate(self.Manager):
            if x == 0 or x == 9:
                continue
            for y, space in enumerate(self.Manager[x]):
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
        Grid.addWidget(self.Label,0,0,1,3)
        Grid.addWidget(self.NameEdit,1,0,1,3)
        Grid.addWidget(self.IPEdit,2,0,1,3)
        
        Ok = QPushButton("Submit",self)
        Ok.clicked.connect(self.accept)
        
        Grid.addWidget(Ok,3,2,1,1)
        self.setLayout(Grid)
        
        if os.path.isfile(LastConnectionFile):
            with open(LastConnectionFile, "r") as f:
                self.NameEdit.setText(f.readline()[:-1])
                self.IPEdit.setText(f.readline())
        
        
    def getText(self, text=False):
        if text:
            self.Label.setText(self.text+text)
        else:
            self.Label.setText(self.text)
        ok = self.exec_()
        name = self.NameEdit.text()
        ip = self.IPEdit.text()
        return name, ip, ok
        
        
    




