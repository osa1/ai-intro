# from heapq import heappop, heappush
import itertools
import sys
import time

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

# Note [Implementing minimax recursively]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Instead of maintaining a stack I'm using recursive implementation here. The
# reason is becaue it doesn't matter, because IMO you never need to consider
# 200 moves ahead etc. because:
#
# 1. It takes forever.
#
# 2. If you have that many empty space on the board, you can just do a random,
#    safe move. No need to consider that many moves ahead in this game.

# Creating this class to avoid horrible wrapper functions.
class Minimax:
    def __init__(self, heuristic, max_depth=sys.maxint):
        self.heuristic = heuristic
        self.max_depth = max_depth

    def __call__(self, state, depth=None, steps=0, timeit=False):
        if depth == None:
            depth = self.max_depth

        if timeit:
            begin = time.clock()

        max_move = None

        # print (indent_lines(steps,
        #     "minimax considering state:\n" + str(state)))

        # This implementation is not great, ideally we'd want to use heuristic
        # if depth = 0 or we're in a terminal state, but checking for terminal
        # state is expensive enough, and more importantly, it involves
        # generating good_moves(), which we do it here in any case. So what we
        # do is instead we generate good_moves(), and if doesn't generate
        # anything we know it's terminal state.
        #
        # Furthermore, all terminal states are equally bad for us, so if a move
        # leads to a terminal state, we just return MIN_INT instead of actually
        # calling the heuristic. Heuristic is only used when depth = 0 and
        # we're not at a terminal state. (which to me makes perfect sense, but
        # some of the resources like Wikipedia doesn't use it this way)

        for move in state.good_moves():
            # print (indent_lines(steps, "considering move: " + str(move)))
            # print (indent_lines(steps, "current max move: " + str(max_move)))
            state.move_inplace(*move)

            if depth == 0:
                new_state_eval = self.heuristic(state)
            else:
                (new_state_eval, _) = self.__call__(
                        state, depth=depth-1, steps=steps+1, timeit=timeit)
                new_state_eval = - new_state_eval

            state.revert(*move)
            if max_move == None or new_state_eval > max_move[0]:
                # print (indent_lines(steps, "updating max move"))
                max_move = (new_state_eval, move)

        if not max_move:
            # (terminal state)
            # We couldn't add any moves, end of game.
            for move in state.available_spaces():
                max_move = (-sys.maxint, move)
                break

        # print (indent_lines(steps, "max move: " + str(max_move)))

        if timeit:
            end = time.clock()
            print "Decided in %fs." % (end - begin)

        return max_move

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
        for move in state.available_spaces():
            # Not quite random but whatever.
            return (-sys.maxint, move)

    return max_move

def quick_player(state, timeit=False):
    # Quick player tries to play quick and smart. He thinks that for boards
    # with size > 4, first moves can be just almost random. He just makes sure
    # that he won't do super stupid things(like moving to the only place that
    # makes him lose while there is a dozen free places), but doesn't consider
    # more than one move ahead.
    #
    # After game comes closer to an end, it starts actually thinking. Considers
    # increasingly more moves ahead.
    best_move = consider_depth(state, 10)

    if not best_move:
        return simple_player(state)

    return best_move

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

# This heuristic makes almost no sense, but leaving here for testing purposes.
def h_available_space(state):
    return state.good_space()

# I think this is the perfect heuristic, but it's almost useless since it
# doesn't approximate. To this heuristic all states except terminal ones are
# equal.
def h_terminal(state):
    if state.is_terminal():
        return -10
    return 0

def h_terminal_available(state):
    if state.is_terminal():
        return -10
    return state.spanned_space()

################################################################################
# Minimax players

available_space_player = Minimax(h_available_space)
terminal_state_player = Minimax(h_terminal)
terminal_state_player_2 = Minimax(h_terminal_available)
# main_player = terminal_state_player
main_player = terminal_state_player_2
main_player.max_depth = 3

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
    (_, move) = main_player(grid, timeit=False)
    print move

    # grid = Grid.empty(3)
    # run_game(grid, simple_player, available_space_player)
    # run_game(grid, random_player, available_space_player)
    # run_game(grid, available_space_player, random_player)
