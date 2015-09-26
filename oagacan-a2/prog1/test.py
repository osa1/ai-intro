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

    def test_game1(self):
        grid = rameses.Grid.empty(3)
        self.assertTrue(rameses.run_game(
            grid, rameses.minimax, rameses.seemingly_dumb_heuristic, verbose=False))

    def test_game2(self):
        grid = rameses.Grid.empty(3)
        self.assertFalse(rameses.run_game(
            grid, rameses.seemingly_dumb_heuristic, rameses.minimax, verbose=False))

if __name__ == "__main__":
    unittest.main()
