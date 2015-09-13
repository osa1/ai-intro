import sys

class State:
    def __init__(self, arr):
        assert arr and len(arr) == 16
        self.arr = arr

    def __repr__(self):
        return "State(" + str(self.arr) + ")"

    def __str__(self):
        grid = []
        for row in range(0, 4):
            line = []
            for col in range(0, 4):
                line.append(self.arr[row * 4 + col])
            grid.append(line)
        return "State(" + str(grid) + ")"

    def left(self, row):
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

        return State(arr_copy)

    def right(self, row):
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

        return State(arr_copy)

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

        return State(arr_copy)

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

        return State(arr_copy)


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
