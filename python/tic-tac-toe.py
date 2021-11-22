"""
This module allows you to play tic-tac-toe on the command line.

NOTE: If you are trying to run it on windows, you will need to first run
    'pip install windows-curses' because curses does not work on windows
    otherwise, for some reason.
"""

try:
    import curses
except:
    out = ""
    out += "Could not import module 'curses'. If you you are on windows, you "
    out += "need to run 'pip install windows-curses' because python does not "
    out += "have curses automatically installed on windows for some reason."
    print(out)
    raise
# =============================================================================
# Helper Functions
# -----------------------------------------------------------------------------

def yx(x, y=None):
    """
    Translate xy coordinates to ncurses' coordinates so you don't go insane
        while using ncurses and its cursed yx coordinate system.
    """
    if y is None:
        return x[1], x[0]
    else:
        return y, x

# =============================================================================
# Helper Classes
# -----------------------------------------------------------------------------

class GameBoard:
    def __init__(self, width=3, height=3):
        assert width > 0
        assert height > 0

        self._height = height
        self._width = width
        self.reset() # create's the underlying board

        # The last player to make a move
        self._last_player_to_move = 1

    def height(self):
        return self._height

    def width(self):
        return self._width

    def size(self):
        return self._width * self._height

    def board(self):
        return self._board

    def reset(self):
        """
        Resets the game board to be all -1's

        Board is an array of -1, 0, and 1. Each index represents a cell of the
            board:
          -1 : empty cell
           0 : cell taken by O
           1 : cell taken by X
        """
        self._board = [-1] * self.size()

    def x(self, index:int) -> int:
        """
        Takes in a state and a tile num and returns what the x-coord of the
            tile_num is in the state.
        """
        return (index % self.width())

    def y(self, index:int) -> int:
        """
        Takes in a state and a tile num and returns what the y-coord of the
            tile_num is in the state.
        """
        return 0 if index == 0 else index // self.width()

    def xy_to_index(self, x, y):
        return (self.width() * y) + x

    def index_to_xy(self, index):
        return (self.x(index), self.y(index))

    def get(self, x:int, y:int) -> int:
        """
        Return the value for the given x and y
        """
        return self._board[self.xy_to_index(x, y)]

    def set(self, x:int, y:int, player:int) -> int:
        """
        Sets the cell given by x and y to the given player (-1, 0, or 1)
        """
        assert -1 <= player <= 1
        self._board[self.xy_to_index(x, y)] = player

    def next_move(self, x:int, y:int, player:int=None):
        """
        Does the next move in the game.

        x, y is 0 based from the top-left hand corner so the top-left corner is
            cell (0, 0)

        raises AssertionError if you try to put an X/O on a space that is already
            taken by an X/O
        """
        player = self.next_player() if player is None else player
        assert self.get(x, y) == -1, \
                "You cannot place your X or O in a cell that is already taken by an X or O"
        self.set(x, y, player)
        return self.won()

    def won(self):
        """
        Returns 0 or 1 depending on which player won, -1 otherwise.
        """
        width, height = self.width(), self.height()

        possibles = []
        # Gather rows
        for i in range(height):
            start_idx = i * width
            possibles.append(self._board[start_idx: start_idx + width])

        # Gather cols
        for i in range(width):
            possibles.append([self.get(i, j) for j in range(height)])

        # Gather Diagonals (Not available if board is not square)
        if width == height:
            #   Top-Left to Bottom-Right diagonal
            possibles.append( \
                    [self.get(x, y) for x, y in zip(range(width), range(height))])

            #   Bottom-Left to Top-Right diagonal
            possibles.append( \
                [self.get(x, y) for x, y in zip(range(width), range(height - 1, -1, -1))])

        # Actually check for the winner
        for possible in possibles:
            if -1 in possible:
                # thing not fully taken by either player
                continue
            elif not (1 in possible):
                return 0 # 0 owns entire thing
            elif not (0 in possible):
                return 1 # 1 owns entire thing

        return -1

    def next_player(self):
        """
        Returns which player is making the next move.
        """
        return 0 if self._last_player_to_move == 1 else 1

    def __str__(self):
        out = ""

        largest_width = len(str(self.width()))
        largest_len = len(str(self.height()))
        cell_width = 5

        # print top numbers
        #for i in range(self.width()):
        #    out += " " + i + " "

        row_width = self.width() + 3
        top_n_bottom = "+" + ((("-" * (cell_width - 2)) + "+") * self.width())
        out += top_n_bottom + "\n"

        for i, cell in enumerate(self._board):
            if (((i + 1) % (self.width())) == 1):
                # Row Start
                out += f"| " # New row

            # Row Content
            if cell == -1:
                out += " "
            elif cell == 0:
                out += "O"
            elif cell == 1:
                out += "X"

            if (((i + 1) % (self.width())) == 0):
                # Row End
                out += " |\n"
                out += top_n_bottom + "\n"
            else:
                out += " | "

        #out += top_n_bottom
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}(width={self.width()}, height={self.height()}, board={self._board})>"

# =============================================================================
# Main Function
# -----------------------------------------------------------------------------

def main():
    pass

def test():
    board_size = 3
    # Test Row Win
    for y in range(3):
        board = GameBoard(board_size, board_size)
        assert board.next_move(0, y, 1) == -1
        assert board.next_move(1, y, 1) == -1
        assert board.next_move(2, y, 1) == 1

    # Test Col Win
    for x in range(3):
        board = GameBoard(board_size, board_size)
        assert board.next_move(x, 0, 1) == -1
        assert board.next_move(x, 1, 1) == -1
        assert board.next_move(x, 2, 1) == 1

    # Test Top Left to Bottom Right diag win
    board = GameBoard(board_size, board_size)
    assert board.next_move(0, 0, 1) == -1
    assert board.next_move(1, 1, 1) == -1
    assert board.next_move(2, 2, 1) == 1

    # Test Bottom Left to Top Right diag win
    board = GameBoard(board_size, board_size)
    assert board.next_move(2, 0, 1) == -1
    assert board.next_move(1, 1, 1) == -1
    assert board.next_move(0, 2, 1) == 1

if __name__ == "__main__":
    #main()
    test()
    pass
