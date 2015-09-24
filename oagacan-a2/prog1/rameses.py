import itertools

class Grid:
    def __init__(self, size, str):
        if len(str) != size * size:
            raise RuntimeError("Grid size doesn't match with grid. (%d vs. %d)"
                    % (size * size, len(str)))

        assert (len(str) == size * size)
        self.size = size
        self.grid = [c for c in str]

    def at(self, row, col):
        return self.grid[row * self.size + col]

    def __str__(self):
        lines = []

        line_sep = "+" + "".join(itertools.repeat("-", self.size * 3 + (self.size - 1))) + "+"
        lines.append(line_sep)

        for row in range(self.size):
            line = "| "
            for col in range(self.size):
                line += self.at(row, col) + " | "
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
    print Grid(args["board-size"][0], args["board"][0])
