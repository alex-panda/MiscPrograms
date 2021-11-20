"""
A module that lets you create and manipulate a SlidePuzzle where you take a
    jumbled slide puzzel board and turn it into a solved board that looks like
    this:
    +-------+        +-------------+
    | 1 2 3 |        | 1  2  3  4  |
    | 4 5 6 |   or   | 5  6  7  8  |
    | 7 8 0 |        | 9  10 11 12 |
    +-------+        | 13 14 15 0  |
                     +-------------+
"""
__all__ = ("Board", "test", "main")
from collections import namedtuple
from heapq import heappop, heappush

# =============================================================================
# Board
# -----------------------------------------------------------------------------
Item = namedtuple("Item", ["f", "h", "g", "board", "direction", "parent_index"])
Move = namedtuple("Move", ["direction", "board"])

EMPTY_TILE = 0

# Move Directions
UP = "u"
DOWN = "d"
LEFT = "l"
RIGHT = "r"

class Board:
    __slots__ = ["_height_and_width", "_board"]
    """
    Represents a SlidePuzzle board.

    All xy values are from the top left-hand corner of the board so tile (0, 0)
        is the tile in the top left-hand corner of the board.
    """
    def __init__(self, board:tuple=None, height_and_width:int=3):
        self._height_and_width = height_and_width

        if board is None:
            self._board = None
            self.randomize()
        else:
            if not isinstance(board, tuple):
                self._board = tuple(board)
            else:
                self._board = board

    def _valid_tile_num(self, tile_num):
        if not (isinstance(tile_num, int) and -1 < tile_num < self.size()):
            error = f"{tile_num} is not a valid tile!"
            raise AssertionError(error)
            return False
        return True

    def goal(self):
        """
        Returns a Board that represents the goal or "solved" version of this
            board.
        """
        size = self.size()
        board = [i if i != size else EMPTY_TILE for i in range(1, size + 1)]
        return Board(board, self.width())

    def randomize(self):
        """
        Randomizes the tiles of this board.
        """
        from random import shuffle
        goal = self.goal()._board

        while (self._board is None) or (not self.solvable()):
            self._board = [i for i in goal]
            shuffle(self._board)
            self._board = tuple(self._board)

    def solvable(self):
        """
        Returns whether the current board, as it currently is, is solvable.

        CREDIT: Big thanks to "hmakholm left over Monica" on stack exchange for
             the great outline of how to check if the puzzle is solvable!
        """
        # When you count inversions, pretend the empty space is a tile with a
        # higher number than any others.
        board = [x if (x != EMPTY_TILE) else (self.size() + 1) for x in self._board]
        _, inv_cnt = count_sort(board)

        # Count the distance between the empty space and the lower-right cell,
        # following the grid lines. For example in a 15-puzzle with the empty
        # space at the far upper left this distance would be 6 because you need
        # to go 3 right, 3 down.
        x, y = self.xy(EMPTY_TILE) # get xy of empty tile
        dist = (abs(x - (self.width() - 1)) + abs(y - (self.height() - 1)))

        # The configuration is solvable if and only if the number of inversions
        # plus the empty-space distance from the lower right is an even number.
        return ((inv_cnt + dist) % 2 == 0)

    def solve(self, ignore_warning=False, give_max_queue_length=False):
        """
        Does an A* search for the correct set of steps from the current state of
            this board to the goal state and returns a list detailing how
            to get from this board to the goal board in the least number of
            moves.

        Returns: a list of size n where the next move that should be taken
            towards the goal is at index 0 and the goal state (the state the
            list is working towards) is at index (n - 1). Each index of the list
            will hold a named tuple where the first element is the next move
            that should be taken after the previous index' move is done and
            the second element is the resulting board after that move is done.
        """
        assert self.solvable(), \
                f"The board\n\n{self}\n\n    is not solveable so even an A* search will not be able to solve it."

        if (not ignore_warning) and (self.width() > 3 or self.height() > 3):
            raise AssertionError(f"Sorry, but a {self.width()} x {self.height()} board cannot be solved in a reasonable amount of time (could take hours or even universe lifetimes to solve).")

        open = [] # Will function as priority queue for successors not yet looked at

        item_by_idx = {}
        idx_by_item = {}
        visited = set()

        # Item Index Generator For Traceback of States
        def idx():
            i = 0
            while True:
                yield i
                i += 1
        item_index = idx()
        curr_idx = next(item_index)

        goal = self.goal()

        # Function to create items
        def item(g, direction, board, parent_index):
            # g will be the number of moves from the start board and h (the
            # heuristic we are using) is the sum of the manhatten distances
            # from given board to the goal board
            h = board.sum_m_dists(goal)
            return Item(g + h, h, g, board, direction, parent_index)

        # g = 0 because no moves yet and parent_index = -1 because no parent yet
        start_item = item(0, None, self, -1)
        item_by_idx[curr_idx] = start_item
        idx_by_item[start_item] = curr_idx

        heappush(open, start_item)

        if give_max_queue_length:
            max_queue_length = len(open)

        while len(open) > 0:
            curr_item = heappop(open)
            curr_board = curr_item.board

            # Our cost function g(n) is the total number of moves so far, and every
            # valid successor has an additional cost of 1.
            g = curr_item.g +  1

            curr_idx = idx_by_item[curr_item]

            if curr_board == goal:
                path = [curr_item]

                # Traceback path
                while path[-1] != start_item:
                    path.append(item_by_idx[path[-1].parent_index])

                # Get boards from path
                for i in range(len(path)):
                    path[i] = Move(path[i].direction, path[i].board)

                # Make move 0 (this board) be at index 0
                path.reverse()


                if give_max_queue_length:
                    return path, max_queue_length
                return path

            successors = curr_board.successors()

            # Add successors to the queue
            for direction, successor in successors.items():

                if successor._board in visited:
                    # To save time, don't visit the same node twice
                    continue

                visited.add(successor._board)

                successor_idx = next(item_index)

                successor_item = item(g, direction, successor, curr_idx)

                idx_by_item[successor_item] = successor_idx
                item_by_idx[successor_idx] = successor_item

                heappush(open, successor_item)

            if give_max_queue_length:
                max_queue_length = max(max_queue_length, len(open))

    def size(self):
        return self._height_and_width ** 2

    def width(self):
        return self._height_and_width

    def height(self):
        return self._height_and_width

    def x(self, tile_num:int):
        """
        Takes in a state and a tile num and returns what the x-coord of the
            tile_num is in the state.
        """
        if not self._valid_tile_num(tile_num): return None
        return (self._board.index(tile_num) % self.width())

    def y(self, tile_num:int):
        """
        Takes in a state and a tile num and returns what the y-coord of the
            tile_num is in the state.
        """
        if not self._valid_tile_num(tile_num): return None
        tile_idx = self._board.index(tile_num)
        return 0 if tile_idx == 0 else tile_idx // self.width()

    def xy(self, tile_num):
        if not self._valid_tile_num(tile_num): return None, None
        return self.x(tile_num), self.y(tile_num)

    def xy_to_idx(self, x, y):
        return (self.width() * y) + x

    def m_dist(self, other_board, tile_num:int, count_free_tile=False):
        """
        Returns the manhatten distance from tile_num on this board to tile_num
            on the given board.
        """
        if not self._valid_tile_num(tile_num): return None

        if (not count_free_tile) and (tile_num == EMPTY_TILE):
            # Don't count free_tile because it is not a tile but an empty space
            return 0

        return (abs(self.x(tile_num) - other_board.x(tile_num)) \
                + abs(self.y(tile_num) - other_board.y(tile_num)))

    def sum_m_dists(self, other_board):
        """
        Returns sum of manhatten distance for all tiles in this board and other
            board.

        NOTE: both boards must have the same height and width
        """
        assert self.size() == other_board.size(), \
                f"\n{self}\n\n({self.width()}, {self.height()}) is not the " + \
                f"same size as ({other_board.width()}, {other_board.height()})" \
                + f"\n\n{other_board}\n\nso you cannot sum their dists."

        return sum(self.m_dist(other_board, i) for i in range(self.size()))

    def move_tile(self, direction, new=False):
        """
        Moves the given tile one spot in the given direction and returns the
            corresponding board for it. If it cannot be moved in that direction,
            None is returned.

        New is whether to return a new board for the tile movement. If it is
            False, than this board will be moved in place.
        """
        old_x, old_y = x, y = self.xy(EMPTY_TILE)

        if direction == LEFT:
            x -= 1
        elif direction == RIGHT:
            x += 1
        elif direction == UP:
            y -= 1
        elif direction == DOWN:
            y += 1

        if not (-1 < x < self.width() and -1 < y < self.height()):
            # If new spot will be out of bounds, then cannot move tile given
            # direction
            return None

        idx = self.xy_to_idx(x, y)
        old_idx = self.xy_to_idx(old_x, old_y)

        # If new, then produce an entirely new board, otherwise just make
        # changes in place to this board
        new_board = [x for x in self._board]

        new_board[idx], new_board[old_idx] = new_board[old_idx], new_board[idx]

        if new:
            return Board(new_board, self.width())
        else:
            self._board = tuple(new_board)
            return self

    def solved(self):
        """
        Returns True if solved, False otherwise.
        """
        return self == self.goal()

    def successors(self):
        """
        Return the dict of boards representing all of this board's successor
            states, that is, a dict containing each possible next move and the
            board that would result from each possible next move.
        """
        out = {}

        for direction in (UP, DOWN, LEFT, RIGHT):
            new = self.move_tile(direction, new=True)

            if new is not None:
                out[direction] = new

        return out

    def __lt__(self, other):
        if isinstance(other, Board):
            return self._board < other._board
        else:
            raise TypeError(f"'<' not supported between instances of type '{type(self)}' and '{type(other)}'")

    def __hash__(self):
        return hash(self._board)

    def __eq__(self, other):
        if isinstance(other, Board):
            return self._board == other._board
        else:
            return self._board == other

    def __len__(self):
        return len(self._board)

    def __str__(self):
        max_tile_len = 0

        for x in self._board:
            max_tile_len = max(max_tile_len, len(f'{x}'))

        top_n_bottom = "+" + ("-" * ((self.width() * (max_tile_len + 1)) + 1)) + "+"
        out = ""
        out += top_n_bottom + "\n"

        for i, tile in enumerate(self._board):
            if (((i + 1) % (self.width())) == 1):
                out += "| "

            tile_str = f"{tile}"

            out += tile_str
            out += (" " * (max_tile_len - len(tile_str)))
            out += " "

            # New Row
            if (((i + 1) % (self.width())) == 0):
                out += "|\n"

        out += top_n_bottom
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}(width={self.width()}, height={self.height()}, board={self._board})>"

# =============================================================================
# Helper Functions
# -----------------------------------------------------------------------------

def count_sort(L:list):
    """
    Returns the number of inversions that exist in the given list of ints.
    """
    half = len(L) // 2
    if len(L) == 0 or half == 0: return (L, 0)

    L1, c1 = count_sort(L[:half]) # Sort Front-Half of L
    L2, c2 = count_sort(L[half:]) # Sort Back-Half of L
    L, c = merge_count(L1, L2)
    return (L, c + c1 + c2)

def merge_count(A, B):
    """
    Merges two lists, counting how many inversions there are and returning both
        the count and the merged list. Necessary for Count Sort
    """
    S = []
    c = 0

    while (len(A) > 0) or (len(B) > 0):

        # When one of them is len 0, just keep appending the one that is not len 0
        if (len(A) == 0) or (len(B) == 0):
            if len(A) > 0:
                S.append(A.pop(0))
            else:
                S.append(B.pop(0))
            continue

        # Pop and append the min{front of A, front of B} to S
        if A[0] <= B[0]:
            S.append(A.pop(0))
        else:
            S.append(B.pop(0))
            c += len(A)

    return S, c


# =============================================================================
# Main Function
# -----------------------------------------------------------------------------

def test():
    example1 = Board([2, 5, 8, 4, 3, 6, 7, 1, 0], 3)
    example1_goal = (1, 2, 3, 4, 5, 6, 7, 8, 0) # what goal should be

    assert example1.goal()._board == example1_goal, \
            f"{example1._board} is not {example1_goal}"

    for tile, exp_dist in zip(tuple(range(1, 8)), ((3, 1, 2, 0, 1, 0, 0, 3))):
        assert example1.m_dist(example1.goal(), tile) == exp_dist
    assert example1.sum_m_dists(example1.goal()) == 10

    example1_goal = Board(example1_goal)

    solution = example1.solve()
    assert solution[-1].board == example1_goal, \
            f'\n{solution[-1]}\n\nis not\n\n{example1_goal}'

    example2 = Board([4,3,8,5,1,6,7,2,0], 3)
    example2_goal = example2.goal()
    solution, max_queue_length = example2.solve(True)

    for i, move in enumerate(solution):
        print(f'\nMove {i} ({move.direction}):\n{move.board}')

    print(f'Max Queue Length: {max_queue_length}')


def main():
    OUT_BULLET = "  -  "
    valid_moves = (UP, DOWN, LEFT, RIGHT)
    quit_words = ("quit", "exit", "leave", "q")
    help_words = ("help", "h")
    restart_words = ("restart",)
    solve_words = ("solve",)
    goal_words = ("goal",)

    movement = f'UP="{UP}", DOWN="{DOWN}", LEFT="{LEFT}", RIGHT="{RIGHT}"'

    def quit():
        print("Thanks for playing!")

    def help(move_loop=False):
        out = "\n-----Help-----"

        out += "\nHelp:"
        for word in help_words: out += f' "{word}"'

        out += "\n\nQuit:"
        for word in quit_words: out += f' "{word}"'

        if move_loop:
            out += f"\n\nMove Empty Tile ({EMPTY_TILE}): "
            out += movement
            out += f"\n{OUT_BULLET}Note: You can type multiple of these to do multiple moves at once."

            out += f"\n\nRestart with new puzzle: "
            for word in restart_words: out += f' "{word}"'

            out += f"\n\nHaving Trouble?\n"
            out += f"{OUT_BULLET}Type 'goal' to see what the solved board looks like so that you know what you are trying to work towards.\n"
            out += f"{OUT_BULLET}Type 'solve' then a number to display the next 'number' moves you should make to get closer to the solution. If no number is given (you just press the return key), then as many moves as it takes to get to the solution will be displayed.\n"

            for word in restart_words: out += f' "{word}"'

        out += "\n--------------"

        print(out, end="\n\n")

    def program_input():
        # Return user input, preprocessing it however it needs to be
        return input().rstrip("\r\n").rstrip("\n").rstrip(" ").rstrip("\t")

    print()
    print("Welcome to the Slide Puzzle Game!")
    print(f"You can quit at any time by typing any of {[x for x in quit_words]}")
    print(f"You can get help by typing any of {[x for x in help_words]}\n")

    # Main Game Loop
    while True:
        restart = False

        print("How large (N x N) do you want your slide puzzle? (give integer > 2):")

        while True:
            x = program_input()

            if x in quit_words:
                quit()
                return
            elif x in help_words:
                help()
                print("How large (N x N) do you want your slide puzzle? (give integer > 2):")
                continue

            try:
                x = int(x)
            except ValueError:
                print("That's not an integer like 3, 4, 8, or 42. Please try again:")
                continue

            if x < 3:
                print("The integer must be greater than 2. Please try again:")
                continue

            break

        board = Board(None, x)

        print(f"\nTo move empty tile ({EMPTY_TILE}): {movement}")
        print(f"New {x} x {x} board generated:")
        print(board)

        # Move Loop
        while True:
            print("Move: ", end="")
            x = program_input()
            print()

            if x in quit_words:
                quit()
                return
            elif x in help_words:
                help(move_loop=True)
                continue
            elif x in restart_words:
                restart = True
                break
            elif x in solve_words:
                print("Show Next N Steps (int):", end="")
                num = ''
                try:
                    num = int(program_input())
                except ValueError:
                    if num != '':
                        print(f"'{num}' is not a number. ")
                        continue

                try:
                    solution = board.solve()
                except AssertionError as e:
                    print(e)
                    print("Are you sure you want to try? (Y or N):")
                    x_ = program_input()

                    if not (x_ in ('Y', 'y')):
                        continue

                    solution = board.solve(ignore_warning=True)

                direction_str = ""
                for i, move in enumerate(solution):
                    if num != '' and i > num: break
                    if i == 0: continue
                    direction_str += f'{move.direction}'
                    print(f'\nMove {i} ({move.direction}):\n{move.board}')

                print(f'Move Summary: {direction_str}\n') # Print out what moves were made
                continue
            elif x in goal_words:
                print(f'Goal:\n{board.goal()}')
                print(f"\nCurrently:")
                print(board, end="\n\n")
                continue

            invalid = False
            moves = []
            for ch in x:
                if ch in valid_moves:
                    moves.append(ch)
                    continue
                elif ch in (" ", "\t", "\r", "\n"):
                    continue
                else:
                    print(f'\n"{x}" is not a valid move {valid_moves}. Moves aborted. Please try again.\n')
                    print("Board:")
                    print(board, end="\n\n")
                    invalid = True
                    break
            if invalid: continue

            curr_board = board

            # Actually carry out movement
            for move in moves:
                new_board = curr_board.move_tile(move, new=True)

                if new_board is not None:
                    curr_board = new_board

            board = curr_board

            if board.solved():
                print(f"\n-+-+ Congrats! You solved the Puzzle! +-+-")
                print("\nSolved Board:")
                print(board)
                break

            print(f"New Board:")
            print(board)

        if restart:
            continue

        # Another Puzzle? while loop
        while True:
            print("Do another slide puzzle? (Y or N): ", end="")
            x = program_input()

            if x in quit_words or x in ("N", "n"):
                quit()
                return
            elif x in help_words:
                help()
                print()
                continue

            if x in ("Y", "y"):
                quit()
                break
            else:
                print(f'"{x}" is not Y or N. Please try again.\n')


if __name__ == "__main__":
    #test()
    main()








