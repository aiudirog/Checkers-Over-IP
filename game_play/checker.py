from PyQt4.QtGui import QLabel
import Globals as Gl


class Checker(QLabel):
    # state holds the current appearance of a checker piece
    # Holds 4 digits
    # One's place: 0 = Unselected, 1 = Selected
    # Ten's place: 0 = Clear, 1 = Black, 2 = Red
    # Hundred's place: 0 = Not King, 1 = King
    # Thousand's place: 0 = Not Last Selected, 1 = Last Selected
    #            (Last selected overrides selected)
    state = 0000
    clear = 0
    black = 10
    red = 20
    x = 0
    y = 0

    def __init__(self, state=0000, x=0, y=0):
        super(Checker, self).__init__()
        self.state = state
        self.x = x
        self.y = y
        self.setMinimumSize(1, 1)
        self.setScaledContents(True)
        self.change_image()
        Gl.Signals["clearAllCheckers"].connect(self.clear_all_selected)

    def set_state(self, new_state):
        self.state = new_state
        self.change_image()

    def set_selected(self, is_selected):
        # Clear current selection state
        self.clear_all_selected()
        if is_selected:
            self.state += 1
        self.change_image()

    def change_selected(self):
        self.set_selected(not self.is_selected())

    def is_selected(self):
        return self.state % 10 == 1

    def set_last_selected(self, is_last_selected):
        # Clear current last selection state
        self.clear_all_selected()
        if is_last_selected:
            self.state += 1000
        self.change_image()

    def clear_all_selected(self):
        self.state -= ((self.state // 1000) % 10) * 1000
        self.state -= self.state % 10
        self.change_image()

    def set_king(self, is_king):
        # Clear current king state
        self.state -= ((self.state // 100) % 10) * 100
        if is_king:
            self.state += 100
        self.change_image()

    def is_king(self):
        return ((self.state // 100) % 10) == 1

    def change_image(self):
        if Gl.PiecePixmaps[self.state] is not None:
            self.setPixmap(Gl.PiecePixmaps[self.state])

    def set_color(self, color):
        """
        Changes the image used to display the checker.

        Pass color using Checker.clear, Checker.black, and Checker.red

        :param color:
        :return:
        """
        # Clear second digit.
        second_digit = (self.state // 10) % 10
        self.state -= second_digit
        self.state += color
        self.change_image()

    def reset_state(self):
        self.state = 0
        self.change_image()

    def get_state(self):
        return self.state

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self):
        return ((self.state // 10) % 10) * 10

    def is_clear(self):
        return (self.state // 10) % 10 == 0

    def mouseReleaseEvent(self, mouse_event):
        if not self.is_clear():
            if Gl.partnerIP == "Offline":
                if Gl.Current_Turn == Gl.Red_Turn and self.get_color() != self.red:
                    return
                elif Gl.Current_Turn == Gl.Black_Turn and self.get_color() != self.black:
                    return
                else:
                    Gl.Signals["pieceSelected"].emit(self)
                    return

            # Only select if it is your turn.
            if Gl.ColorIAm == Gl.Current_Turn:
                if Gl.Current_Turn == Gl.Red_Turn and self.get_color() == self.red:
                    Gl.Signals["pieceSelected"].emit(self)
                if Gl.Current_Turn == Gl.Black_Turn and self.get_color() == self.black:
                    Gl.Signals["pieceSelected"].emit(self)
        else:
            Gl.Signals["emptySpaceSelected"].emit(self)

    def mouseDoubleClickEvent(self, mouse_event):
        if self.is_clear():
            Gl.Signals["emptySpaceDoubleClicked"].emit(self)
