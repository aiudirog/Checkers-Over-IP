from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QApplication, QMessageBox
from game_play import Pieces, Checker
import Globals as Gl
from server_client import CheckersServer
import Strings


class GameManager(QObject):
    """
    This class is used to mediate. It handles validating moves, mediating between
    the GUI and the server thread, etc.
    """
    pieces = None
    game_board = None
    curr_selection = []
    curr_piece = None
    curr_pieces_to_remove = []

    def __init__(self, parent, game_board):
        super(GameManager, self).__init__(parent)
        self.game_board = game_board
        self.pieces = Pieces()
        self.game_board.load_pieces(self.pieces)

        Gl.Signals["pieceSelected"].connect(self.on_piece_selected)
        Gl.Signals["emptySpaceSelected"].connect(self.on_empty_space_selected)
        Gl.Signals["emptySpaceDoubleClicked"].connect(self.on_empty_space_double_clicked)
        Gl.Signals["ExecuteMove"].connect(self.on_execute_moves)
        Gl.Signals["CurrentTurnSignal"].connect(self.change_turn)

        self.checkers_server = CheckersServer(self)

    def start_checkers_server(self):
        self.checkers_server.start()

    # noinspection PyArgumentList
    def on_piece_selected(self, piece):
        Gl.Signals["clearAllCheckers"].emit()
        QApplication.processEvents()
        piece.change_selected()
        self.curr_selection = [(piece.get_x(), piece.get_y())]
        self.curr_pieces_to_remove = []
        self.curr_piece = piece

    def on_empty_space_selected(self, space):
        # If no piece is selected, don't even try
        if not self.curr_selection:
            return

        x, y = space.get_x(), space.get_y()

        # Allow selecting a different first space.
        if (x, y) not in self.curr_selection and len(self.curr_selection) > 1:
            if self.is_possible_move(x, y, from_piece=True):
                Gl.Signals["clearAllCheckers"].emit()
                self.pieces[self.curr_selection[0][0]][self.curr_selection[0][1]].set_selected(True)
                space.change_selected()
                self.curr_selection = [self.curr_selection[0], (x, y)]
                return

        # If the space was deselected, remove all following moves.
        if (x, y) in self.curr_selection:
            index = self.curr_selection.index((x, y))
            for move in self.curr_selection[index:]:
                self.pieces[move[0]][move[1]].clear_all_selected()
                self.curr_selection.pop(index)
            return

        if self.is_possible_move(x, y):
            space.change_selected()
            self.curr_selection.append((x, y))

    def on_empty_space_double_clicked(self, space=None):
        # If no piece is selected, don't even try
        if not self.curr_selection:
            return

        if not space:
            if len(self.curr_selection) >= 2:
                x, y = self.curr_selection[-1][0], self.curr_selection[-1][1]
            else:
                return
        else:
            x, y = space.get_x(), space.get_y()

        if (x, y) != self.curr_selection[-1]:
            if self.is_possible_move(x, y):
                space.set_selected(True)
                self.curr_selection.append((x, y))
            else:
                return
        self.send_moves()

    def is_possible_move(self, move_x, move_y, from_piece=False):
        color = self.curr_piece.get_color()
        red = self.curr_piece.red
        black = self.curr_piece.black
        is_king = self.curr_piece.is_king()
        if from_piece:
            curr_x = self.curr_piece.get_x()
            curr_y = self.curr_piece.get_y()
        else:
            curr_x = self.curr_selection[-1][0]
            curr_y = self.curr_selection[-1][1]
        removing_piece = False

        # Stay on board
        if move_x == 0 or move_y == 0 or move_x == 9 or move_y == 9:
            return False

        # Make sure we are moving on a diagonal
        if move_x == curr_x or move_y == curr_y:
            return False
        if abs(move_x - curr_x) != abs(move_y - curr_y):
            return False
        # Single moves greater than 2 are illegal
        if abs(move_x - curr_x) > 2:
            return False
        # Make sure we are moving in the right direction
        if not is_king:
            if color == red:
                if move_y > curr_y:
                    return False
            elif color == black:
                if move_y < curr_y:
                    return False
        # Check for jumping
        if abs(move_x - curr_x) == 2:
            check_x, check_y = (move_x + curr_x) // 2, (move_y + curr_y) // 2
            if self.pieces[check_x][check_y].is_clear():
                # Can't jump an empty space
                return False
            else:
                if self.pieces[check_x][check_y].get_color == color:
                    # Can't jump your own color
                    return False
                # Jumping a piece of opposite color, prepare it to be taken
                self.curr_pieces_to_remove.append((check_x, check_y))
                removing_piece = True
        # Prevent moving move than once without taking a piece
        if len(self.curr_pieces_to_remove) != 0 and not removing_piece and not from_piece:
            return False
        if len(self.curr_selection) == 2 and not removing_piece and not from_piece:
            return False
        return True

    def on_execute_moves(self, moves, removals):
        Gl.Signals["clearAllCheckers"].emit()
        if Gl.Current_Turn == 0:
            color = Checker.black
        else:
            color = Checker.red
        piece = moves[0]
        space = moves[-1]
        is_king = self.pieces[piece[0]][piece[1]].is_king()
        self.pieces[piece[0]][piece[1]].reset_state()
        self.pieces[space[0]][space[1]].set_color(color)
        self.pieces[space[0]][space[1]].set_king(is_king)

        if (color == Checker.black and space[1] == 8) or (color == Checker.red and space[1] == 1):
            self.pieces[space[0]][space[1]].set_king(True)

        for removal in removals:
            self.pieces[removal[0]][removal[1]].reset_state()

        if not self.check_win_loss():
            self.change_turn()

        Gl.Signals["clearAllCheckers"].emit()

        self.pieces[space[0]][space[1]].set_last_selected(True)

        self.curr_selection = []
        self.curr_piece = None
        self.curr_pieces_to_remove = []

    def send_moves(self):
        if len(self.curr_selection) < 2:
            return
        if Gl.partnerIP != "Offline":
            Gl.Signals["SendMove"].emit(self.curr_selection, self.curr_pieces_to_remove)
        self.on_execute_moves(self.curr_selection, self.curr_pieces_to_remove)

    def change_turn(self):
        if Gl.Current_Turn == 0:
            Gl.Current_Turn += 1
        else:
            Gl.Current_Turn -= 1
        self.game_board.set_current_turn()

    def check_win_loss(self):
        moves = {Checker.red: 0, Checker.black: 0}
        checkers = {Checker.red: 0, Checker.black: 0}
        for x, row in enumerate(self.pieces):
            for y, piece in enumerate(row):
                if not piece.is_clear():
                    checkers[piece.get_color()] += 1
                    x = piece.get_x()
                    y = piece.get_y()
                    if piece.is_king() or piece.get_color() == Checker.black:
                        if (x + 1) != 9 and (y + 1) != 9:
                            if self.pieces[x + 1][y + 1].is_clear():
                                moves[piece.get_color()] += 1
                            else:
                                if x + 2 < 9 and y + 2 < 9:
                                    if self.pieces[x + 2][y + 2].is_clear():
                                        moves[piece.get_color()] += 1
                        if (x - 1) != 0 and (y + 1) != 9:
                            if self.pieces[x - 1][y + 1].is_clear():
                                moves[piece.get_color()] += 1
                            else:
                                if x - 2 > 0 and y + 2 < 9:
                                    if self.pieces[x - 2][y + 2].is_clear():
                                        moves[piece.get_color()] += 1
                    if piece.is_king() or piece.get_color() == Checker.red:
                        if (x - 1) != 0 and (y - 1) != 0:
                            if self.pieces[x - 1][y - 1].is_clear():
                                moves[piece.get_color()] += 1
                            else:
                                if x - 2 > 0 and y - 2 > 0:
                                    if self.pieces[x - 2][y - 2].is_clear():
                                        moves[piece.get_color()] += 1
                        if (x + 1) != 9 and (y - 1) != 0:
                            if self.pieces[x + 1][y - 1].is_clear():
                                moves[piece.get_color()] += 1
                            else:
                                if x + 2 < 9 and y - 2 > 0:
                                    if self.pieces[x + 2][y - 2].is_clear():
                                        moves[piece.get_color()] += 1
        if checkers[Checker.red] == 0:
            self.end_game(Strings.BlackWins)
            return True
        elif checkers[Checker.black] == 0:
            self.end_game(Strings.RedWins)
            return True
        elif moves[Checker.red] == 0:
            self.end_game(Strings.BlackWinsNoMoreMoves)
            return True
        elif moves[Checker.black] == 0:
            self.end_game(Strings.RedWinsNoMoreMoves)
            return True
        else:
            return False

    # noinspection PyArgumentList
    def end_game(self, string):
        message = QMessageBox(self.game_board.main_window)
        message.setWindowTitle(Strings.GameOverTitle)
        message.setText(string)
        message.setTextFormat(Qt.RichText)
        message.exec()
        QApplication.processEvents()
        self.reset()

    # noinspection PyArgumentList
    def reset(self):
        self.pieces.setup_new_game()
        Gl.ColorIAm = int(not Gl.ColorIAm)
        Gl.Current_Turn = Gl.Black_Turn
        if Gl.Type == "Client" and Gl.Current_Turn != Gl.ColorIAm:
            Gl.Signals["ServerFirst"].emit()
        self.game_board.set_current_turn()
        QApplication.processEvents()
