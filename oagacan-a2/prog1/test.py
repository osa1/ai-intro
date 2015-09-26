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


    def test_hashing(self):
        grid = rameses.Grid.empty(2)
        self.assertEqual(0, hash(grid))

        grid.move_inplace(1, 1)
        self.assertEqual(0b1000, hash(grid))
        grid.revert(1, 1)
        self.assertEqual(0, hash(grid))

        grid.move_inplace(0, 1)
        self.assertEqual(0b0100, hash(grid))
        grid.move_inplace(0, 0)
        self.assertEqual(0b0101, hash(grid))
        grid.move_inplace(1, 1)
        self.assertEqual(0b1101, hash(grid))
        grid.move_inplace(1, 0)
        self.assertEqual(0b1111, hash(grid))

        grid.revert(0, 0)
        grid.revert(0, 1)
        grid.revert(1, 0)
        grid.revert(1, 1)
        self.assertEqual(0b0000, hash(grid))

if __name__ == "__main__":
    unittest.main()
