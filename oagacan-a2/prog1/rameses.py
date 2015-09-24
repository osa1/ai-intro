import itertools

class Grid:
    def __init__(self, size, str):
        if len(str) != size * size:
            raise RuntimeError("Grid size doesn't match with grid. (%d vs. %d)"
                    % (size * size, len(str)))

        assert (len(str) == size * size)
        self.size = size
        self.grid = [c for c in str]

    def at_xy(self, col, row):
        return self.grid[row * self.size + col]

    def available_space(self):
        for row in xrange(self.size):
            for col in xrange(self.size):
                if self.at_xy(col, row) == '.':
                    yield (col, row)

    def check_move_xy(self, col, row):
        return self.__check_col(col, row) and \
                self.__check_row(col, row) and \
                self.__check_diagonal_1(col, row) and \
                self.__check_diagonal_2(col, row)

    # True  -> it's OK
    # False -> avoid
    def __check_col(self, col, row):
        for x in range(self.size):
            if x != col and self.at_xy(x, row) == '.':
                return True
        return False

    # True  -> it's OK
    # False -> avoid
    def __check_row(self, col, row):
        for y in range(self.size):
            if y != row and self.at_xy(col, y) == '.':
                return True
        return False

    def __check_diagonal_1(self, row, col):
        "From top-left to bottom-right. True -> OK, False -> avoid."
        if row != col:
            return True

        for xy in range(self.size):
            if xy == row:
                continue

            if self.at_xy(xy, xy) == '.':
                return True

        return False

    def __check_diagonal_2(self, row, col):
        "From top-right to bottom-left. True -> OK, False -> avoid."
        if row != self.size - 1 - col:
            return True

        for xy in range(self.size):
            if self.at_xy(self.size - 1 - xy, xy) == '.':
                return True

        return False

    def __str__(self):
        lines = []

        line_sep = "+" + "".join(itertools.repeat("-", self.size * 3 + (self.size - 1))) + "+"
        lines.append(line_sep)

        for row in range(self.size):
            line = "| "
            for col in range(self.size):
                line += self.at_xy(col, row) + " | "
            lines.append(line)
            lines.append(line_sep)

        return "\n".join(lines)

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser("Rameses player")
    arg_parser.add_argument("board-size", type=int, nargs=1)
    arg_parser.add_argument("board", type=str, nargs=1)
    arg_parser.add_argument("time-limit", type=float, nargs=1)

    args = vars(arg_parser.parse_args())
    print args
    grid = Grid(args["board-size"][0], args["board"][0])
    print grid
    print list(grid.available_space())
    print grid.check_move_xy(2, 2)
