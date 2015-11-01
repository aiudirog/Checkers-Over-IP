from game_play import Checker
from PyQt4.QtGui import QPixmap, QPainter
import Globals as Gl
import os


class Pieces(list):

    def __init__(self):
        super(Pieces, self).__init__()
        # Define a two dimensional list to handle piece locations
        self.generate_piece_pixmaps()
        for x in range(10):
            self.append([])
            for y in range(9):
                piece = Checker(Checker.clear, x, y)
                self[-1].append(piece)
        self.setup_new_game()

    def clear_pieces(self):
        # Clear all pieces
        for x, row in enumerate(self):
            for y, piece in enumerate(row):
                piece.reset_state()

    def setup_new_game_pieces(self):
        # Set black pieces
        x, y = 2, 1
        for _n in range(12):
            self[x][y].set_color(Checker.black)
            x, y = self.increment(x, y)
        # Set red pieces
        x, y = 1, 6
        for _n in range(12):
            self[x][y].set_color(Checker.red)
            x, y = self.increment(x, y)

    def setup_new_game(self):
        self.clear_pieces()
        self.setup_new_game_pieces()

    def move_piece(self, old_x, old_y, new_x, new_y):
        """
        Moves a piece from old x,y to new x,y by setting the old checker
        to clear and the new (previously) clear space to the color of
        the checker.

        :param old_x:
        :param old_y:
        :param new_x:
        :param new_y:
        :return:
        """
        piece_color = self[old_x][old_y].get_color()
        self[old_x][old_y].set_color(Checker.clear)
        self[new_x][new_y].set_color(piece_color)

    @staticmethod
    def increment(x, y):
        """
        Helper function for reset_pieces(). This function finds the next
        space given x, y that would a checker would occupy at the beginning
        of a game.

        :param x:
        :param y:
        :return x, y:
        """
        x += 2
        if x == 9:
            y += 1
            x = 2
        elif x == 10:
            y += 1
            x = 1
        return x, y

    @staticmethod
    def generate_piece_pixmaps():
        selected = QPixmap(os.path.join(Gl.Graphics, "clear_Selected.png"))
        last_selected = QPixmap(os.path.join(Gl.Graphics, "Last_Move.png"))
        crown = QPixmap(os.path.join(Gl.Graphics, "Crown.png"))
        clear = QPixmap(os.path.join(Gl.Graphics, "clear.png"))

        black_unselected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_unselected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))
        black_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))
        black_last_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_last_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))

        painter = QPainter(black_selected_pixmap)
        painter.drawPixmap(0, 0, selected)
        painter = QPainter(red_selected_pixmap)
        painter.drawPixmap(0, 0, selected)
        painter = QPainter(black_last_selected_pixmap)
        painter.drawPixmap(0, 0, last_selected)
        painter = QPainter(red_last_selected_pixmap)
        painter.drawPixmap(0, 0, last_selected)

        black_king_unselected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_king_unselected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))
        black_king_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_king_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))
        black_king_last_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Black_Piece.png"))
        red_king_last_selected_pixmap = QPixmap(os.path.join(Gl.Graphics, "Red_Piece.png"))

        painter = QPainter(black_king_unselected_pixmap)
        painter.drawPixmap(0, 0, crown)
        painter = QPainter(red_king_unselected_pixmap)
        painter.drawPixmap(0, 0, crown)

        painter = QPainter(black_king_selected_pixmap)
        painter.drawPixmap(0, 0, selected)
        painter.drawPixmap(0, 0, crown)
        painter = QPainter(red_king_selected_pixmap)
        painter.drawPixmap(0, 0, selected)
        painter.drawPixmap(0, 0, crown)

        painter = QPainter(black_king_last_selected_pixmap)
        painter.drawPixmap(0, 0, last_selected)
        painter.drawPixmap(0, 0, crown)
        painter = QPainter(red_king_last_selected_pixmap)
        painter.drawPixmap(0, 0, last_selected)
        painter.drawPixmap(0, 0, crown)

        Gl.PiecePixmaps = {
            10: black_unselected_pixmap,
            20: red_unselected_pixmap,
            11: black_selected_pixmap,
            21: red_selected_pixmap,
            110: black_king_unselected_pixmap,
            120: red_king_unselected_pixmap,
            111: black_king_selected_pixmap,
            121: red_king_selected_pixmap,
            1: selected,
            0: clear,
            1010: black_last_selected_pixmap,
            1020: red_last_selected_pixmap,
            1110: black_king_last_selected_pixmap,
            1120: red_king_last_selected_pixmap
        }

        """
        Gl.PiecePixmaps = {
            'BlackUnselectedPixmap': black_unselected_pixmap,
            'RedUnselectedPixmap': red_unselected_pixmap,
            'BlackSelectedPixmap': black_selected_pixmap,
            'RedSelectedPixmap': red_selected_pixmap,
            'BlackKingUnselectedPixmap': black_king_unselected_pixmap,
            'RedKingUnselectedPixmap': red_king_unselected_pixmap,
            'BlackKingSelectedPixmap': black_king_selected_pixmap,
            'RedKingSelectedPixmap': red_king_selected_pixmap,
            'SelectedPixmap': selected,
            'UnselectedPixmap': clear,
            'BlackLastSelectedPixmap': black_last_selected_pixmap,
            'RedLastSelectedPixmap': red_last_selected_pixmap,
            'BlackKingLastSelectedPixmap': black_king_last_selected_pixmap,
            'RedKingLastSelectedPixmap': red_king_last_selected_pixmap
        }
        """
