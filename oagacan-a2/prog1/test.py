import unittest

from rameses import *

class TestSolver(unittest.TestCase):
    def test_moveCheckRegression(self):
        # .xx
        # x..
        # x.x
        grid = Grid(3, ".xxx..x.x")
        self.assertFalse(grid.check_move_xy(1, 1))

    def test_someMoves(self):
        # .xx
        # x..
        # x.x
        grid = Grid(3, ".xxx..x.x")
        self.assertFalse(grid.check_move_xy(2, 1))
        self.assertFalse(grid.check_move_xy(1, 2))

    def test_moves_list(self):
        grid = Grid(3, "xx..xx...")
        good_moves = list(grid.good_moves())
        self.assertEqual([(0, 2)], good_moves)
        all_moves = set(list(grid.available_spaces()))
        self.assertEqual(set([(2, 0), (0, 1), (0, 2), (1, 2), (2, 2)]), all_moves)

    def test_game1(self):
        grid = Grid.empty(3)
        self.assertTrue(run_game(
            grid, main_player, simple_player, verbose=False))

    def test_game2(self):
        grid = Grid.empty(3)
        self.assertFalse(run_game(
            grid, simple_player, main_player, verbose=False))

    # def test_game3(self):
    #     grid = Grid.empty(3)
    #     self.assertFalse(run_game(
    #         grid, random_player, main_player, verbose=False))

    # def test_game4(self):
    #     grid = Grid.empty(3)
    #     self.assertTrue(run_game(
    #         grid, main_player, random_player, verbose=False))

    def test_hashing(self):
        grid = Grid.empty(2)
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

    def test_minimax_stupidity_1(self):
        grid = Grid.empty(3)
        grid.move_inplace(0, 0)
        grid.move_inplace(1, 0)
        move = main_player(grid)[1]
        self.assertNotEqual((0, 1), move)

    def test_minimax_stupidity_2(self):
        # An inversion of previous stupidity
        grid = Grid.empty(3)
        grid.move_inplace(0, 0)
        grid.move_inplace(0, 1)
        move = main_player(grid)[1]
        self.assertNotEqual((1, 0), move)

    def test_minimax_stupidity_3(self):
        grid = Grid.empty(3)
        grid.move_inplace(0, 0)
        grid.move_inplace(1, 0)
        grid.move_inplace(1, 1)
        move = main_player(grid)[1]
        # (0, 1) is winning move here
        self.assertEqual((0, 1), move)

    def test_minimax_depth_simple_first(self):
        grid = Grid.empty(4)
        player = Minimax(h_terminal_available, max_depth=3)
        self.assertFalse(run_game(
            grid, simple_player, player, verbose=False))

    def test_minimax_depth_main_first(self):
        grid = Grid.empty(4)
        player = Minimax(h_terminal_available, max_depth=1)
        self.assertFalse(run_game(
            grid, player, simple_player, verbose=False))

if __name__ == "__main__":
    unittest.main()
