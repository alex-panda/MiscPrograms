"""
The classic game of snake run on the terminal using ncurses.

NOTE: If you are trying to run it on windows, you will need to first run
    'pip install windows-curses' because curses does not work on windows
    otherwise, apparently
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

from random import randint
import time

UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"

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

class GameWindow:
    """
    A window to house the game state without having to worry about how the game
        is actually displayed.
    """
    def __init__(self, width, height, snake, apples):
        self.width = width
        self.height = height
        self.snake = snake
        self.apples = apples

    def new_apple(self):
        return (randint(1, self.width - 2), randint(1, self.height - 2))

    def advance(self, direction=None):
        """
        Advance Game State.

        Returns True when the game is to continue, False if the game is over.
        """
        snake, apples = self.snake, self.apples

        snake.advance(direction)

        # Check if ate an Apple
        idx_of_eaten_apples = []
        for i, apple in enumerate(apples):
            if snake.ate(apple):
                idx_of_eaten_apples.append(i)

                # Replace apple (after we remove it in a moment)
                apples.append(self.new_apple())

                if ((snake.apples_eaten() % 10) == 0):
                    apples.append(self.new_apple()) # Add another apple as game progresses

        num_idxs_eaten = 0
        for idx in idx_of_eaten_apples:
            idx -= num_idxs_eaten # Keep indexes correct
            apples.pop(idx)

        # Check if snake hit a wall
        if snake.collision_with_boundaries(0, 0, self.width, self.height):
            return False

        # Check if snake hit itself
        if snake.collision_with_self():
            return False

        return True

class Snake:
    def __init__(self, start_point=(0, 0), start_direction=RIGHT):
        self.points = [start_point] # index 0 is head, index n - 1 is tail
        self._last_direction = start_direction
        self._ate_apple = False
        self._num_apples_eaten = 0
        self.head_char = ">"
        self.body_char = "#"

    def _update_head_char(self):
        if self._last_direction == UP:
            self.head_char = "^"
        elif self._last_direction == RIGHT:
            self.head_char = ">"
        elif self._last_direction == LEFT:
            self.head_char = "<"
        elif self._last_direction == DOWN:
            self.head_char = "."

    def ate(self, apple):
        """
        Returns True and adds a point to the snake if eats given apple (point),
            False otherwise.
        """
        if apple in self.points:
            self._ate_apple = True
            self._num_apples_eaten += 1
            return True
        else:
            return False

    def score(self):
        return self.apples_eaten()

    def apples_eaten(self):
        return self._num_apples_eaten

    def advance(self, direction=None):
        """
        Advance the snake.
        """
        direction = self._last_direction if direction is None else direction

        x, y = self.points[0] # Get head point

        # Be nice to player and don't let them move backwards into their own
        #   body which would kill their snake
        if direction == UP and self._last_direction == DOWN:
            direction = DOWN
        elif direction == DOWN and self._last_direction == UP:
            direction = UP
        elif direction == LEFT and self._last_direction == RIGHT:
            direction = RIGHT
        elif direction == RIGHT and self._last_direction == LEFT:
            direction = LEFT

        # Move Head
        if direction == UP:
            y -= 1
        elif direction == DOWN:
            y += 1
        elif direction == LEFT:
            x -= 1
        elif direction == RIGHT:
            x += 1

        self.points.insert(0, (x, y)) # Add new head position

        if self._ate_apple:
            self._ate_apple = False
            # Since not popping tail, will grow 1 point longer
        else:
            self.points.pop() # pop old tail

        self._last_direction = direction
        self._update_head_char()

    def collision_with_boundaries(self, x, y, w, h):
        """Return True if snake hit boundary, False otherwise."""
        sx, sy = self.points[0] # Get x, y of head
        return (sx <= x) or (sx >= x + w) or (sy <= y) or (sy >= y + h)

    def collision_with_self(self):
        """Returns True if hit self, False otherwise."""
        snake_head = self.points[0]
        return (snake_head in self.points[1:])


# =============================================================================
# Main Function
# -----------------------------------------------------------------------------

def main(scr=None):
    if scr is None: curses.wrapper(main); return

    h, w = scr.getmaxyx()
    status_win = curses.newwin(1, w, 0, 0) # Window above window with game

    main_h, main_w = h - 1, w

    win = curses.newwin(main_h, main_w, 1, 0) # new window

    win.keypad(1) # Initialize keyboard to get keypresses
    curses.curs_set(0) # Set cursor to be invisible

    apples = [(10, 10)]
    snake = Snake((1, 1), RIGHT)

    game_win = GameWindow(main_w, main_h, snake, apples)

    # Make snake length 3
    for _ in range(2):
        snake._ate_apple = True
        snake.advance()

    def draw(win, status_win, apples, snake, snake_speedup):
        status_win.clear()
        out = " "
        out += f"Score: {snake.score()} | "
        out += f"Snake Length: {len(snake.points)} | "
        out += f"Apples: {len(apples)} | "
        out += f"Speedup: {snake_speedup}"
        status_win.addstr(0, 0, out)
        status_win.refresh()

        win.clear()
        win.border("|", "|", "-", "-", "+", "+", "+", "+") # put border around the game screen

        for apple in apples:
            win.addch(*yx(apple), "A")

        for i, point in enumerate(snake.points):
            if i == 0:
                win.addch(*yx(point), snake.head_char)
            else:
                win.addch(*yx(point), snake.body_char)

        win.refresh()

    draw(win, status_win, apples, snake, 0)

    while True:
        # Figure out new screen
        snake_speedup = int(snake.score() ** (1/2))
        win.timeout(200 - snake_speedup)

        # Advance Snake
        key = win.getch()

        if key == curses.KEY_LEFT:
            continue_game = game_win.advance(LEFT)
        elif key == curses.KEY_RIGHT:
            continue_game = game_win.advance(RIGHT)
        elif key == curses.KEY_UP:
            continue_game = game_win.advance(UP)
        elif key == curses.KEY_DOWN:
            continue_game = game_win.advance(DOWN)
        else:
            continue_game = game_win.advance()

        if not continue_game:
            break

        # Draw New Screen
        draw(win, status_win, apples, snake, snake_speedup)

    scr.addstr(h // 3, w // 3, 'FINAL SCORE: ' + str(snake.score()))
    scr.refresh()
    time.sleep(1)
    scr.getch() # Wait till player presses a button before exiting fully

if __name__ == "__main__":
    main()



