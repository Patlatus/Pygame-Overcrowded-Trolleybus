from square import Square
from piece import Piece

##COLORS##
#             R    G    B
WHITE    = (255, 255, 255)
GREEN    = (  0, 255,   0)
MAGENTA  = (255,   0, 255)
GREEN_DARK    = (  0, 243,   0)
MAGENTA_DARK  = (243,   0, 243)
BLACK    = (  0,   0,   0)


##DIRECTIONS##
NORTH = (0, -1)
EAST = (1, 0)
SOUTH = (0, 1)
WEST = (-1, 0)

class Board:
    def __init__(self):
        self.matrix = self.new_board()

    def new_board(self):
        """
        Create a new board matrix.
        """

        # initialize squares and place them in matrix

        matrix = [[None] * 8 for i in range(8)]

        for x in range(8):
            for y in range(8):
                if (x % 2 != 0) and (y % 2 == 0):
                    matrix[y][x] = Square(WHITE)
                elif (x % 2 != 0) and (y % 2 != 0):
                    matrix[y][x] = Square(BLACK)
                elif (x % 2 == 0) and (y % 2 != 0):
                    matrix[y][x] = Square(WHITE)
                elif (x % 2 == 0) and (y % 2 == 0):
                    matrix[y][x] = Square(BLACK)

        # initialize the pieces and put them in the appropriate squares

        for x in range(4, 8):
            for y in range(4):
                matrix[x][y].occupant = Piece(MAGENTA)
            for y in range(4, 8):
                matrix[x][y].occupant = Piece(GREEN)

        return matrix

    def board_string(self, board):
        """
        Takes a board and returns a matrix of the board space colors. Used for testing new_board()
        """

        board_string = [[None] * 8] * 8

        for x in range(8):
            for y in range(8):
                if board[x][y].color == WHITE:
                    board_string[x][y] = "WHITE"
                else:
                    board_string[x][y] = "BLACK"

        return board_string

    def rel(self, dir, pixel):
        """
        Returns the coordinates one square in a different direction to (x,y).

        ===DOCTESTS===

        >>> board = Board()

        >>> board.rel(NORTH, (1,2))
        (1,1)

        >>> board.rel(SOUTH, (3,4))
        (3,5)

        >>> board.rel(EAST, (3,6))
        (3,5)

        >>> board.rel(WEST, (2,5))
        (1,5)
        """
        x, y = pixel
        dx, dy = dir
        return (x + dx, y + dy)

    def adjacent(self, pixel):
        """
        Returns a list of squares locations that are adjacent (on a diagonal) to (x,y).
        """
        x, y = pixel

        return [self.rel(NORTH, (x, y)), self.rel(EAST, (x, y)), self.rel(WEST, (x, y)), self.rel(SOUTH, (x, y))]

    def location(self, pixel):
        """
        Takes a set of coordinates as arguments and returns self.matrix[x][y]
        This can be faster than writing something like self.matrix[coords[0]][coords[1]]
        """
        x, y = pixel

        return self.matrix[x][y]

    def blind_legal_moves(self, pixel):
        """
        Returns a list of blind legal move locations from a set of coordinates (x,y) on the board.
        If that location is empty, then blind_legal_moves() return an empty list.
        """

        x,y = pixel
        return self.adjacent(pixel) if self.matrix[x][y].occupant != None else []

    def legal_moves(self, pixel, hop=False):
        """
        Returns a list of legal move locations from a given set of coordinates (x,y) on the board.
        If that location is empty, then legal_moves() returns an empty list.
        """

        x, y = pixel
        blind_legal_moves = self.blind_legal_moves((x, y))
        legal_moves = []

        if hop == False:
            for move in blind_legal_moves:
                if hop == False:
                    if self.on_board(move):
                        if self.location(move).occupant == None:
                            legal_moves.append(move)

                        else:
                            mx, my = move
                            jump = (mx + mx - x, my + my - y)
                            if self.on_board(jump) and self.location(jump).occupant == None: # is this location empty?
                                legal_moves.append(jump)

        else:  # hop == True
            for move in blind_legal_moves:
                if self.on_board(move) and self.location(move).occupant != None:
                    mx, my = move
                    jump = (mx + mx - x, my + my - y)
                    if self.on_board(jump) and self.location(jump).occupant == None: # is this location empty?
                        legal_moves.append(jump)

        return legal_moves

    def remove_piece(self, pixel):
        """
        Removes a piece from the board at position (x,y).
        """
        x,y = pixel
        self.matrix[x][y].occupant = None

    def move_piece(self, start, finish):
        """
        Move a piece from (start_x, start_y) to (end_x, end_y).
        """
        sx, sy = start
        fx, fy = finish

        self.matrix[fx][fy].occupant = self.matrix[sx][sy].occupant
        self.remove_piece((sx, sy))






 


    def on_board(self, pixel):
        """
        Checks to see if the given square (x,y) lies on the board.
        If it does, then on_board() return True. Otherwise it returns false.

        ===DOCTESTS===
        >>> board = Board()

        >>> board.on_board((5,0)):
        True

        >>> board.on_board(-2, 0):
        False

        >>> board.on_board(3, 9):
        False
        """

        x,y = pixel
        return not (x < 0 or y < 0 or x > 7 or y > 7)


