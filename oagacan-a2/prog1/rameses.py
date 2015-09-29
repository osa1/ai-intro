# from heapq import heappop, heappush
import itertools
import sys
import time

################################################################################
## NOTES

# When we use boolean as an indicator of whose turn is this, True means it's
# our turn.
#
# NOTE [Heuristics]
#
# - Don't have much here; one simple but useful heuristic might be just number
#   of spaces that we can use. Moves that lead to losing don't count.

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

        self.__hash = 0
        for i in xrange(len(self.grid)):
            if self.grid[i] == 'x':
                self.__hash |= 1 << i

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

    def move_inplace(self, col, row):
        # assert col < self.size
        # assert row < self.size

        idx = row * self.size + col
        self.grid[idx] = 'x'
        self.__hash |= 1 << idx

    def revert(self, col, row):
        "This is for reverting moves, puts a '.'."
        # assert col < self.size
        # assert row < self.size

        idx = row * self.size + col
        self.grid[idx] = '.'
        self.__hash &= ~ (1 << idx)

    def at_xy(self, col, row):
        return self.grid[row * self.size + col]

    def available_spaces(self):
        for row in xrange(self.size):
            for col in xrange(self.size):
                if self.at_xy(col, row) == '.':
                    yield (col, row)

    def has_available_space(self):
        for _ in self.available_spaces():
            return True
        return False

    def good_moves(self):
        for (x, y) in self.available_spaces():
            if self.check_move_xy(x, y):
                yield (x, y)

    def check_move_xy(self, col, row):
        return self.__check_col(col, row) and \
                self.__check_row(col, row) and \
                self.__check_diagonal_1(col, row) and \
                self.__check_diagonal_2(col, row)

    def good_space(self):
        return sum(1 for _ in self.good_moves())

    def all_space(self):
        return sum(1 for _ in self.available_spaces())

    def spanned_space(self):
        return (self.size * self.size) - self.good_space()

    def valid_move_p(self, col, row):
        return self.at_xy(col, row) == '.'

    def is_terminal(self):
        return (self.spanned_space() == self.size * self.size)

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

    def __check_diagonal_1(self, col, row):
        "From top-left to bottom-right. True -> OK, False -> avoid."
        if row != col:
            return True

        for xy in xrange(self.size):
            if xy == row:
                continue

            if self.at_xy(xy, xy) == '.':
                return True

        return False

    def __check_diagonal_2(self, col, row):
        "From top-right to bottom-left. True -> OK, False -> avoid."
        if row != self.size - 1 - col:
            return True

        for xy in xrange(self.size):
            col_to_check = self.size - 1 - xy
            row_to_check = xy

            if col_to_check == col and row_to_check == row:
                continue

            if self.at_xy(col_to_check, row_to_check) == '.':
                return True

        return False

    def __hash__(self):
        return self.__hash

    def __eq__(self, other):
        return self.__hash == other.__hash

    def __ne__(self, other):
        return self.__hash != other.__hash

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

def indent_lines(n, s):
    import itertools
    lines = s.split('\n')
    spaces = "".join(itertools.repeat(' ', 4 * n))
    sep = '\n' + spaces
    return sep + sep.join(lines)

################################################################################

# TODO: Add a depth parameter and use heuristic after considering depth.

def minimax(state, heuristic, steps=0, timeit=False):
    # TODO: We should probably maintain a stack instead of doing recursive
    # calls, if we want to work on big states.

    if timeit:
        begin = time.clock()

    max_move = None

    # print (indent_lines(steps,
    #     "minimax considering state:\n" + str(state)))

    for move in state.good_moves():
        # print (indent_lines(steps, "considering move: " + str(move)))
        # print (indent_lines(steps, "current max move: " + str(max_move)))

        state.move_inplace(*move)
        (new_state_eval, _) = minimax(state, heuristic, steps=steps+1)
        new_state_eval = - new_state_eval
        state.revert(*move)
        if max_move == None or new_state_eval > max_move[0]:
            # print (indent_lines(steps, "updating max move"))
            max_move = (new_state_eval, move)

    if not max_move:
        # (terminal state)
        # We couldn't add any moves, end of game. We just do some random move.
        for move in state.available_spaces():
            # TODO: This is not quite random, should we collect available
            # spaces in a list and pick something random?
            state.move_inplace(*move)
            new_state_eval = heuristic(state)
            state.revert(*move)
            max_move = (new_state_eval, move)
            break

    # print (indent_lines(steps, "max move: " + str(max_move)))

    if timeit:
        end = time.clock()
        print "Decided in %fs." % (end - begin)

    return max_move

def with_heuristic(heuristic):
    def minimax_w_heuristic(state, **kwargs):
        return minimax(state, heuristic, **kwargs)
    return minimax_w_heuristic

def simple_player(state, timeit=False):
    max_move = None

    for move in state.good_moves():
        state.move_inplace(*move)
        new_state_eval = state.spanned_space()
        state.revert(*move)
        if max_move == None or new_state_eval > max_move[0]:
            max_move = (new_state_eval, move)

    if not max_move:
        # We couldn't add any moves, end of game. We just do some random move.
        new_state_eval = state.size * state.size
        for move in state.available_spaces():
            # TODO: This is not quite random, should we collect available
            # spaces in a list and pick something random?
            return (new_state_eval, move)

    return max_move

def random_player(state, timeit=False):
    import random
    # We only use state arguments, others are added to comply with the
    # interface.
    moves = list(state.good_moves())
    if len(moves) != 0:
        return (0, random.choice(moves))

    # All of the moves result in a lose, still do something
    moves = list(state.available_moves())
    return (0, random.choice(moves))

################################################################################
# Heuristics

def h_available_space(state):
    return state.spanned_space()

def h_terminal(state):
    if state.is_terminal():
        return -10
    else:
        return 0

################################################################################
# Minimax players

available_space_player = with_heuristic(h_available_space)
terminal_state_player = with_heuristic(h_terminal)
main_player = terminal_state_player

################################################################################

def run_game(state, p1, p2, verbose=True):
    if verbose:
        print state

    turn = True
    while state.spanned_space() != state.size * state.size:
        if turn:
            (eval, move) = p1(state)
        else:
            (eval, move) = p2(state)

        state.move_inplace(*move)

        if verbose:
            print "turn: %s, eval: %d, move: %s" % (str(turn), eval, str(move))
            print state

        turn = not turn

    if verbose:
        print "%s wins." % ("player 2" if turn else "player 1")

    return (not turn)

################################################################################

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser("Rameses player")
    arg_parser.add_argument("board-size", type=int, nargs=1)
    arg_parser.add_argument("board", type=str, nargs=1)
    arg_parser.add_argument("time-limit", type=float, nargs=1)

    args = vars(arg_parser.parse_args())
    grid = Grid(args["board-size"][0], args["board"][0])
    (_, move) = terminal_state_player(grid, timeit=False)
    print move

    # grid = Grid.empty(3)
    # run_game(grid, simple_player, available_space_player)
    # run_game(grid, random_player, available_space_player)
    # run_game(grid, available_space_player, random_player)
