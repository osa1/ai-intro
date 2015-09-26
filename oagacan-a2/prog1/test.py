import unittest

import rameses

class TestRegression(unittest.TestCase):
    def test_moveCheckRegression(self):
        # .xx
        # x..
        # x.x
        grid = rameses.Grid(3, ".xxx..x.x")
        self.assertFalse(grid.check_move_xy(1, 1))

    def test_someMoves(self):
        # .xx
        # x..
        # x.x
        grid = rameses.Grid(3, ".xxx..x.x")
        self.assertFalse(grid.check_move_xy(2, 1))
        self.assertFalse(grid.check_move_xy(1, 2))

if __name__ == "__main__":
    unittest.main()
