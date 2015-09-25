# from heapq import heappop, heappush
import itertools

################################################################################
## NOTES

# When we use boolean as an indicator of whose turn is this, True means it's
# our turn.

################################################################################

class Grid:
    def __init__(self, size, arg):
        if len(arg) != size * size:
            raise RuntimeError("Grid size doesn't match with grid. (%d vs. %d)"
                    % (size * size, len(arg)))

        self.size = size

        if isinstance(arg, str):
            self.grid = [c for c in arg]
        else:
            self.grid = arg

    @classmethod
    def empty(cls, size):
        arr = ['.' for _ in xrange(size * size)]
        return cls(size, arr)

    def move(self, col, row):
        "Return a new grid with the given move made. Copies the whole grid."
        assert col < self.size
        assert row < self.size

        new_arr = self.grid[:]
        new_arr[row * self.size + col] = 'x'
        return Grid(self.size, new_arr)

    def at_xy(self, col, row):
        return self.grid[row * self.size + col]

    def available_spaces(self):
        for row in xrange(self.size):
            for col in xrange(self.size):
                if self.at_xy(col, row) == '.':
                    yield (col, row)

    def good_moves(self):
        for (x, y) in self.available_spaces():
            if self.check_move_xy(x, y):
                yield (x, y)

    def check_move_xy(self, col, row):
        return self.__check_col(col, row) and \
                self.__check_row(col, row) and \
                self.__check_diagonal_1(col, row) and \
                self.__check_diagonal_2(col, row)

    def available_space(self):
        return sum(1 for _ in self.good_moves())

    def spanned_space(self):
        return (self.size * self.size) - self.available_space()

    def valid_move_p(self, col, row):
        return self.at_xy(col, row) == '.'

    # True  -> it's OK
    # False -> avoid
    def __check_col(self, col, row):
        for x in xrange(self.size):
            if x != col and self.at_xy(x, row) == '.':
                return True
        return False

    # True  -> it's OK
    # False -> avoid
    def __check_row(self, col, row):
        for y in xrange(self.size):
            if y != row and self.at_xy(col, y) == '.':
                return True
        return False

    def __check_diagonal_1(self, row, col):
        "From top-left to bottom-right. True -> OK, False -> avoid."
        if row != col:
            return True

        for xy in xrange(self.size):
            if xy == row:
                continue

            if self.at_xy(xy, xy) == '.':
                return True

        return False

    def __check_diagonal_2(self, row, col):
        "From top-right to bottom-left. True -> OK, False -> avoid."
        if row != self.size - 1 - col:
            return True

        for xy in xrange(self.size):
            if self.at_xy(self.size - 1 - xy, xy) == '.':
                return True

        return False

    def __str__(self):
        lines = []

        line_sep = "+" + "".join(itertools.repeat("-", self.size * 3 + (self.size - 1))) + "+"
        lines.append(line_sep)

        for row in xrange(self.size):
            line = "| "
            for col in xrange(self.size):
                line += self.at_xy(col, row) + " | "
            lines.append(line)
            lines.append(line_sep)

        return "\n".join(lines)

    def __repr__(self):
        # Just to be able to print something useful when in containers
        return self.__str__()


################################################################################

def eval_spanned_space(grid, turn):
    assert turn != None
    cost = grid.spanned_space()
    if turn:
        return cost
    return -cost

def minimax(state, turn=True):
    moves = []

    for move in state.good_moves():
        new_state = state.move(move[0], move[1])
        new_state_eval = eval_spanned_space(state, turn)
        if not turn:
            new_state_eval = -new_state_eval
        moves.append((new_state_eval, move, new_state))

    if len(moves) == 0:
        # We couldn't add any moves, end of game. We just do some random move.
        for move in state.available_spaces():
            # TODO: This is not quite random, should we collect available
            # spaces in a list and pick something random?
            new_state = state.move(move[0], move[1])
            new_state_eval = eval_spanned_space(state, turn)
            if turn:
                return (new_state_eval, move, new_state)
            return (-new_state_eval, move, new_state)

    # TODO: One thing to do here might be to pick something random when we have
    # multiples moves with same evals.
    if turn:
        return max(moves)
    return min(moves)

def run_game(state):
    print state

    turn = True
    while state.spanned_space() != state.size * state.size:
        (eval, move, state) = minimax(state, turn)

        print "turn: %s, eval: %d, move: %s" % (str(turn), eval, str(move))
        print state

        turn = not turn

    print "%s wins." % turn

################################################################################

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser("Rameses player")
    arg_parser.add_argument("board-size", type=int, nargs=1)
    arg_parser.add_argument("board", type=str, nargs=1)
    arg_parser.add_argument("time-limit", type=float, nargs=1)

    args = vars(arg_parser.parse_args())
    # print args

    grid = Grid(args["board-size"][0], args["board"][0])
    (_, move, new_state) = minimax(grid)
    print move
