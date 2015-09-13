import sys
from collections import deque

# NOTE: Ideally I would implement wrapper classes for adding moves and costs,
# but Python makes everything so verbose I decided not to do that. One problem
# with current approach is that equality methods, hashes etc. don't take moves
# and costs into account, and if we want to take those into account then we
# won't be able to have the current implementation, can't have both.

class State:
    def __init__(self, arr, moves=[], cost=0):
        assert arr and len(arr) == 16
        self.arr = arr
        self.hash = State.hash(arr)
        self.moves = moves
        self.cost = cost

    @staticmethod
    def hash(arr):
        exp = 1
        ret = 0
        for i in arr:
            ret += i ^ exp
            exp += 1
        return ret

    def __repr__(self):
        return "State(" + str(self.arr) + ")"

    def __str__(self):
        grid = []
        for row in range(0, 4):
            line = []
            for col in range(0, 4):
                line.append(self.arr[row * 4 + col])
            grid.append(line)
        return "State(" + str(grid) + "," \
                        + "cost=" + str(self.cost) \
                        + ")"

    def __eq__(self, s):
        return self.arr == s.arr

    def __ne__(self, s):
        return self.arr != s.arr

    def __cmp__(self, s):
        return cmp(self.arr, s.arr)

    def __hash__(self):
        return self.hash

    def left(self, row):
        arr_copy = self.arr[:]
        row_start = 4 * row
        i1 = arr_copy[row_start]
        i2 = arr_copy[row_start + 1]
        i3 = arr_copy[row_start + 2]
        i4 = arr_copy[row_start + 3]

        arr_copy[row_start] = i2
        arr_copy[row_start + 1] = i3
        arr_copy[row_start + 2] = i4
        arr_copy[row_start + 3] = i1

        moves = self.moves[:]
        moves.append("left")

        return State(arr_copy, moves, self.cost + 1)

    def right(self, row):
        arr_copy = self.arr[:]
        row_start = 4 * row
        i1 = arr_copy[row_start]
        i2 = arr_copy[row_start + 1]
        i3 = arr_copy[row_start + 2]
        i4 = arr_copy[row_start + 3]

        arr_copy[row_start] = i4
        arr_copy[row_start + 1] = i1
        arr_copy[row_start + 2] = i2
        arr_copy[row_start + 3] = i3

        moves = self.moves[:]
        moves.append("right")

        return State(arr_copy, moves, self.cost + 1)

    def up(self, col):
        arr_copy = self.arr[:]
        i1 = arr_copy[col]
        i2 = arr_copy[col + 4]
        i3 = arr_copy[col + 8]
        i4 = arr_copy[col + 12]

        arr_copy[col] = i2
        arr_copy[col + 4] = i3
        arr_copy[col + 8] = i4
        arr_copy[col + 12] = i1

        moves = self.moves[:]
        moves.append("up")

        return State(arr_copy, moves, self.cost + 1)

    def down(self, col):
        arr_copy = self.arr[:]
        i1 = arr_copy[col]
        i2 = arr_copy[col + 4]
        i3 = arr_copy[col + 8]
        i4 = arr_copy[col + 12]

        arr_copy[col] = i4
        arr_copy[col + 4] = i1
        arr_copy[col + 8] = i2
        arr_copy[col + 12] = i3

        moves = self.moves[:]
        moves.append("down")

        return State(arr_copy, moves, self.cost + 1)


##
## Heuristics
##

# This is the hard part. Things that I considered:
#
# - Manhattan distances of pieces to their correct locations:
#   A naive version would not be admissible, for example, if we have a line
#   like this:
#
#     4 1 2 3
#
#   Cost should be 1, not 4.

def brute_bfs(state0):
    """Brute-force breadth-first search implementation. Uses memoization to
    prevent loops."""

    # See NOTE [Infeasibility of brute force search]

    queue = deque([state0])
    memo  = set()
    # mems  = 0

    while len(queue) != 0:
        state = queue.popleft()
        if state in memo:
            # print("found memoized state(" + str(mems) + ")")
            # mems += 1
            continue
        # print "processing new state"

        memo.add(state)
        if solved(state):
            return state

        for i in range(4):
            queue.append(state.up(i))
            queue.append(state.down(i))
            queue.append(state.left(i))
            queue.append(state.right(i))

    return None

def brute_dfs(state0):
    """Brute-force depth-first search implementation. Uses memoization to
    prevent loops."""

    ### NOTE [Infeasibility of brute force search]
    #
    # Allocates like crazy. On my laptop with 16G RAM it filled the whole thing
    # within seconds. (should be memoized states)
    #
    # Here's a back-of-the-envelope calculation for how much can we memoize at most:
    #
    #   A state has 16 integers, assuming 64bit(8 byte) ints this makes
    #   8 x 16 = 128 bytes. We have 16G RAM,
    #
    #     >>> (16 * 1024 * 1024 * 1024) / 128
    #     134,217,728
    #
    #   This may look like a lot, but when compared with all the states we can
    #   have:
    #
    #     >>> math.factorial(16)
    #     20,922,789,888,000
    #
    #   It's a very small number. Also note that in reality the number of
    #   states we can memoize is a lot smaller, because of extra bookkeeping
    #   we're doing(list of steps we took, an integer for total cost so far,
    #   Python's internal bookkeeping etc.)

    stack = [state0]
    memo  = set()

    while len(stack) != 0:
        state = stack.pop()
        if state in memo:
            continue

        memo.add(state)
        if solved(state):
            return state

        for i in range(4):
            stack.append(state.up(i))
            stack.append(state.down(i))
            stack.append(state.left(i))
            stack.append(state.right(i))

    return None

def h1(state):
    """Manhattan distances of pieces to their correct locations."""
    pass

def solved(state):
    """Return whether the problem is solved."""
    return state.arr == range(1, 17)

def parse_state(f):
    arr = []
    for line in f:
        for i in line.split():
            arr.append(int(i))

    if len(arr) != 16:
        raise RuntimeError("Parsing wrong number of ints. " +
                           "Are you sure the file has correct format?")

    return State(arr)

if __name__ == "__main__":
    s = parse_state(open(sys.argv[1], "r"))
    print s
    #print s.left(1).left(1).right(1).right(1)
    print s.up(3).down(3).up(3).up(3).down(3).down(3)
    print (s == s.up(3))
    print (s == s.up(3).down(3))
    print (s != s.up(3))
    print (s != s.up(3).down(3))
    brute_dfs(s)

    print hash(s)
    print hash(s.up(1))
    print hash(s.up(1).down(1))
