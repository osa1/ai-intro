import sys
import math
from collections import deque

# NOTE: Ideally I would implement wrapper classes for adding moves and costs,
# but Python makes everything so verbose I decided not to do that. One problem
# with current approach is that equality methods, hashes etc. don't take moves
# and costs into account, and if we want to take those into account then we
# won't be able to have the current implementation, can't have both.

################################################################################
## Some random notes about the problem
## (see also NOTEs)
#
# - Best solution I could find for swapping two consecutive tiles consists of
#   15 moves. Since we wrap around, the positions of these consecutive tiles
#   don't matter. (but we may need to rotate moves if we want to swap in row
#   instead of col etc.)
#   TODO: Maybe mention how you do it here.
#
#   I believe 15 move is the minimum amount to swap to consecutive tiles.
#
#   UPDATE: Ops! Solved in 13 moves.
#

class State:
    # NOTE: It turns out keyword arguments suck. Try to guess what happens when
    # you call this constructor like:
    #
    #   State([], [])
    def __init__(self, arr, size=None, moves=[], cost=0):
        self.arr = arr
        self.size = int(size if size else math.sqrt(len(arr)))
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
        for row in range(self.size):
            line = []
            for col in range(self.size):
                line.append(self.arr[row * self.size + col])
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

        row_start = self.size * row
        temps = []

        for i in range(self.size):
            temps.append(arr_copy[row_start + i])

        for i in range(self.size):
            arr_copy[row_start + i] = temps[(i + 1) % self.size]

        moves = self.moves[:]
        moves.append("L" + str(row + 1))

        return State(arr_copy, self.size, moves, self.cost + 1)

    def right(self, row):
        arr_copy = self.arr[:]
        row_start = self.size * row
        temps = []

        for i in range(self.size):
            temps.append(arr_copy[row_start + i])

        for i in range(self.size):
            arr_copy[row_start + i] = temps[(self.size - 1 + i) % self.size]

        moves = self.moves[:]
        moves.append("R" + str(row + 1))

        return State(arr_copy, self.size, moves, self.cost + 1)

    def up(self, col):

        arr_copy = self.arr[:]

        temps = []

        for i in range(self.size):
            temps.append(arr_copy[col + self.size * i])

        for i in range(self.size):
            arr_copy[col + self.size * i] = temps[(i + 1) % self.size]

        moves = self.moves[:]
        moves.append("U" + str(col + 1))

        return State(arr_copy, self.size, moves, self.cost + 1)

    def down(self, col):
        arr_copy = self.arr[:]

        temps = []

        for i in range(self.size):
            temps.append(arr_copy[col + self.size * i])

        for i in range(self.size):
            arr_copy[col + self.size * i] = temps[(self.size - 1 + i) % self.size]

        moves = self.moves[:]
        moves.append("D" + str(col + 1))

        return State(arr_copy, self.size, moves, self.cost + 1)

    def correct_pos(self, num):
        """Return correct (col, row) for a given number. Note that first tile
        is (0, 0)."""
        return ((num - 1) % self.size, (num - 1) / self.size)

    def num_at(self, col, row):
        """First tile is again (0, 0)."""
        assert col < self.size
        assert row < self.size
        return self.arr[row * self.size + col]

    def solved(self):
        return self.arr == range(1, self.size * self.size + 1)


################################################################################
## Brute-force search -- only useful on 2x2 board

def brute_bfs(state0):
    """Brute-force breadth-first search implementation. Uses memoization to
    prevent loops."""

    # See NOTE [Infeasibility of brute force search]

    queue = deque([state0])
    memo  = set()

    while len(queue) != 0:
        state = queue.popleft()

        memo.add(state)

        if state.solved():
            return state

        for i in range(state.size):
            for meth in [State.right, State.down, State.left, State.up]:
                next_state = meth(state, i)
                if next_state not in memo:
                    queue.append(next_state)

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

        memo.add(state)

        if state.solved(state):
            return state

        for i in range(state.size):
            for meth in [State.down, State.right, State.up, State.left]:
                next_state = meth(state, i)
                if next_state not in memo:
                    stack.append(next_state)

    return None

################################################################################
## A*

def astar(state0, heuristic):
    from heapq import heappush, heappop

    pq = [(0, state0)]

    while len(pq) != 0:
        current = heappop(pq)[1]

        if current.solved():
            return current

        for i in range(current.size):
            for meth in [State.down, State.right, State.up, State.left]:
                next_state = meth(current, i)
                heappush(pq, (current.cost + heuristic(next_state), next_state))

################################################################################
## Greedy best-first

# TODO: Maybe make A* code parametric on used keys in priority queue and remove
# duplication.

def bestfirst(state0, heuristic):
    from heapq import heappush, heappop

    pq = [(0, state0)]

    memo = {}

    while len(pq) != 0:
        current = heappop(pq)[1]

        if current.solved():
            return current

        memo[current] = current

        for i in range(current.size):
            for meth in [State.down, State.right, State.up, State.left]:
                next_state = meth(current, i)

                next_state_seen = memo.get(next_state)
                if next_state_seen:
                    if next_state_seen.cost <= current.cost + 1:
                        continue

                heappush(pq, (heuristic(next_state), next_state))

################################################################################
## Heuristics

def h1(state):
    """Number of incorrectly placed numbers. This is not admissible, still
    keeping this here for testing purposes."""
    misplaced = 0
    for i in range(state.size * state.size):
        if state.arr[i] != i + 1:
            misplaced += 1
    return misplaced

def correct_row_col(state):
    # Not sure if this is admissible? It's useless anyway, no need to waste
    # time with proving.
    correct = 0

    for i in range(state.size * state.size):
        num = state.arr[i]
        (num_correct_col, num_correct_row) = state.correct_pos(num)

        i_col = i % state.size
        i_row = i / state.size

        if i_col == num_correct_col:
            correct += 1

        if i_row == num_correct_row:
            correct += 1

    return len(state.arr) * 2 - correct

def swap_heuristic(state):
    """We know that we can swap two numbers in at most 13 steps. Calculate how
    many swaps would be necessary to reach the goal, and multiply it with 13.
    Pretty dumb but admissible heuristic."""
    pass

def print_heuristic(heuristic):
    def printer(state):
        heuristic_score = heuristic(state)
        print str(state)
        print "Heuristic:", heuristic_score
        return heuristic_score

    return printer

################################################################################
## Entry

def parse_state(f):
    arr = []
    for line in f:
        for i in line.split():
            arr.append(int(i))

    size = math.sqrt(len(arr))

    if not size.is_integer():
        raise RuntimeError("Malformed input file. Size of the grid should be a square.")

    return State(arr, size)

if __name__ == "__main__":
    # leaky file descriptor
    s = parse_state(open(sys.argv[1], "r"))
    ret = astar(s, h1)
    for move in ret.moves:
        print move,
    print
