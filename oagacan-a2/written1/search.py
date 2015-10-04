import sys
from collections import deque

################################################################################

def search_knight_moves(start, target):
    current_pos = None

    move_stack = deque([(start, None)])
    visiteds = set()

    solutions = []

    print

    while len(move_stack) != 0:
        current_state = move_stack.popleft()
        current_pos = current_state[0]

        if current_pos == target:
        #     print "\nReached target."
        #     print current_pos
        #     print "Do you want to search for other solutions?"
        #     ret = raw_input()
            solutions.append(current_state)

        visiteds.add(current_pos)
        sys.stdout.write("\rcurrent state: " + str(current_state))
        sys.stdout.flush()

        increments = \
            [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

        for increment in increments:
            next_move = (current_pos[0] + increment[0], current_pos[1] + increment[1])

            not_white_occupied_space = next_move[1] != 1
            not_black_occupied_space = \
                    (next_move[1] == 6 and
                        (next_move[0] not in [0, 1, 2, 5, 6, 8])) or \
                    next_move[1] != 6

            if next_move not in visiteds and \
                    next_move[0] >= 0 and next_move[1] >= 0 and \
                    next_move[0] <= 7 and next_move[1] <= 7 and \
                    not_white_occupied_space and \
                    not_black_occupied_space:
                move_stack.append((next_move, current_state))

    return solutions

def mk_l(s):
    ret = []

    ret.append(s[0])
    while (s[1] != None):
        s = s[1]
        ret.append(s[0])

    return ret

################################################################################

def invalid(pos):
    # Out of board
    if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
        return True

    # First two ranks are occupied(well, in theory we can use B2 but ...)
    if pos[1] == 1 or pos[1] == 0:
        return True

    # Last rank is occupied except for B8
    if pos[1] == 7 and pos[0] != 1:
        return True

    # Rank 7 is occupied except for D7 and E7
    if pos[1] == 6 and (pos[0] != 3 and pos[0] != 4):
        return True

    return False

class State:
    def __init__(self):
        self.white_knight = (1, 0)
        self.black_knight = (1, 7)
        self.black_pawn_1 = (3, 6)
        self.black_pawn_2 = (4, 6)
        self.turn = "white"

    def __str__(self):
        lines = []
        lines.append("<<<")
        lines.append("    white knight: " + str(self.white_knight))
        lines.append("    black knight: " + str(self.black_knight))
        lines.append("    black_pawn_1: " + str(self.black_pawn_1))
        lines.append("    black_pawn_2: " + str(self.black_pawn_2))
        lines.append(">>>")
        return "\n".join(lines)

    def is_solved(self):
        return self.black_knight == None and \
                self.white_knight == None and \
                ((self.black_pawn_1 == None and self.black_pawn_2 == (3, 5)) or \
                     (self.black_pawn_2 == None and self.black_pawn_1 == (3, 5)))

    def move_white_knight(self, new):
        new_s = State()
        new_s.white_knight = new

        if self.black_knight == new:
            new_s.black_knight = None
        else:
            new_s.black_knight = self.black_knight

        if self.black_pawn_1 == new:
            new_s.black_pawn_1 = None
        else:
            new_s.black_pawn_1 = self.black_pawn_1

        if self.black_pawn_2 == new:
            new_s.black_pawn_2 = None
        else:
            new_s.black_pawn_2 = self.black_pawn_2

        new_s.turn = "black"
        return new_s

    def move_black_knight(self, new):
        new_s = State()

        if self.white_knight == new:
            new_s.white_knight = None
        else:
            new_s.white_knight = self.white_knight

        new_s.black_knight = new
        new_s.black_pawn_1 = self.black_pawn_1
        new_s.black_pawn_2 = self.black_pawn_2
        new_s.turn = "white"
        return new_s

    def move_black_pawn_1(self, new):
        new_s = State()

        if self.white_knight == new:
            new_s.white_knight = None
        else:
            new_s.white_knight = self.white_knight

        new_s.black_knight = self.black_knight
        new_s.black_pawn_1 = new
        new_s.black_pawn_2 = self.black_pawn_2
        new_s.turn = "white"
        return new_s

    def move_black_pawn_2(self, new):
        new_s = State()

        if self.white_knight == new:
            new_s.white_knight = None
        else:
            new_s.white_knight = self.white_knight

        new_s.black_knight = self.black_knight
        new_s.black_pawn_1 = self.black_pawn_1
        new_s.black_pawn_2 = new
        new_s.turn = "white"
        return new_s

    def has_black(self, (x, y)):
        return self.black_knight == (x, y) or \
                self.black_pawn_1 == (x, y) or \
                self.black_pawn_2 == (x, y)

    def has_white(self, (x, y)):
        return self.white_knight == (x, y)

    def generate_moves(self):
        if self.turn == "white" and self.white_knight != None:
            for move in self.knight_moves(self.white_knight):
                yield move
        else:
            if self.black_knight != None:
                for move in self.knight_moves(self.black_knight):
                    yield move
            if self.black_pawn_1 != None:
                for move in self.pawn_moves(self.black_pawn_1):
                    yield move
            if self.black_pawn_2 != None:
                for move in self.pawn_moves(self.black_pawn_2):
                    yield move

    def pawn_moves(self, pawn):
        assert self.turn == "black"

        if pawn[1] == 6:
            d2 = (pawn[0], 4)
            if not self.has_black(d2) and not self.has_white(d2) and not invalid(d2):
                yield d2

        d1 = (pawn[0], pawn[1] - 1)
        if not self.has_black(d1) and not self.has_white(d1) and not invalid(d1):
            yield d1

        # caspturing moves
        black_capture_1 = (pawn[0] - 1, pawn[1] - 1)
        black_capture_2 = (pawn[0] + 1, pawn[1] - 1)
        if self.has_white(black_capture_1):
            yield black_capture_1
        if self.has_white(black_capture_2):
            yield black_capture_2

    def knight_moves(self, knight):
        for d in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            new_pos = (knight[0] + d[0], knight[1] + d[1])
            if not invalid(new_pos):
                if (self.turn == "white" and not self.has_white(new_pos)) or \
                        (self.turn == "black" and not self.has_black(new_pos)):
                    yield new_pos

def solve(*args):
    # Four pieces are involved in this game:
    #
    # - White knight at B1
    # - Black knight at B8
    # - Black pawns at D7 and E7
    #
    # Other pieces do not move, and we can't move to their places. Furthermore,
    # we know that there has been 4 plys. Given all these constraints, the
    # search space should be so small that an exhaustive search should be
    # possible.
    #
    # Here we implement that exhaustive search.

    return occupied(*args)

################################################################################

def search(state, depth):
    # print state

    if state.is_solved():
        print "!!!!!!!!!!!! SOLVED !!!!!!!!!!!!"
        return state

    if depth == 8:
        print "Done 8 moves, returning"
        return None

    if state.turn == "white":
        if state.white_knight == None:
            print "Can't move white, knight is captured."
        else:
            for move in state.knight_moves(state.white_knight):
                ret = search(state.move_white_knight(move), depth + 1)
                if ret != None:
                    return ret

    else:
        if state.black_knight != None:
            for move in state.knight_moves(state.black_knight):
                ret = search(state.move_black_knight(move), depth + 1)
                if ret != None:
                    return ret

        if state.black_pawn_1 != None:
            for move in state.pawn_moves(state.black_pawn_1):
                ret = search(state.move_black_pawn_1(move), depth + 1)
                if ret != None:
                    return ret

        if state.black_pawn_2 != None:
            for move in state.pawn_moves(state.black_pawn_2):
                ret = search(state.move_black_pawn_2(move), depth + 1)
                if ret != None:
                    return ret


if __name__ == "__main__":
    # s = State()
    # print search(s, -1)
    # print s.white_knight
    # print list(s.knight_moves(s.white_knight))

    # s.turn = "black"
    # print s.black_pawn_1
    # print list(s.pawn_moves(s.black_pawn_1))
    # print s.black_pawn_2
    # print list(s.pawn_moves(s.black_pawn_2))
    # print s.black_knight
    # print list(s.knight_moves(s.black_knight))

    start_x = int(sys.argv[1]) - 1
    start_y = int(sys.argv[2]) - 1

    end_x = int(sys.argv[3]) - 1
    end_y = int(sys.argv[4]) - 1

    solutions = map(mk_l, search_knight_moves((start_x, start_y), (end_x, end_y)))
    print "\nSOLUTIONS:(%d)", len(solutions)
    for s in solutions:
        print s

    # # can we visit D6 on the way?
    # for s in solutions:
    #     for m in s:
    #         # if m == (4, 4):
    #         #     print "Found a solution that visits E5:", s
    #         # if m == (4, 3):
    #         #     print "Found a solution that visits E6:", s
    #         if m == (3, 5):
    #             print "Found a solution that visits D6:", s
