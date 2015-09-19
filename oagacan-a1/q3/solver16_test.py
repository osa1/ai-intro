import solver16

import unittest

class TestSolver(unittest.TestCase):
    def setUp(self):
        self.state = solver16.State(range(1, 17))

    def test_up(self):
        self.assertEqual(
                self.state.up(0),
                solver16.State([5, 2, 3, 4, 9, 6, 7, 8, 13, 10, 11, 12, 1, 14, 15, 16]))

        self.assertEqual(
                self.state.up(1),
                solver16.State([1, 6, 3, 4, 5, 10, 7, 8, 9, 14, 11, 12, 13, 2, 15, 16]))

        self.assertEqual(
                self.state.up(2),
                solver16.State([1, 2, 7, 4, 5, 6, 11, 8, 9, 10, 15, 12, 13, 14, 3, 16]))

        self.assertEqual(
                self.state.up(3),
                solver16.State([1, 2, 3, 8, 5, 6, 7, 12, 9, 10, 11, 16, 13, 14, 15, 4]))

    def test_down(self):
        self.assertEqual(
                self.state.down(0),
                solver16.State([13, 2, 3, 4, 1, 6, 7, 8, 5, 10, 11, 12, 9, 14, 15, 16]))

        self.assertEqual(
                self.state.down(1),
                solver16.State([1, 14, 3, 4, 5, 2, 7, 8, 9, 6, 11, 12, 13, 10, 15, 16]))

        self.assertEqual(
                self.state.down(2),
                solver16.State([1, 2, 15, 4, 5, 6, 3, 8, 9, 10, 7, 12, 13, 14, 11, 16]))

        self.assertEqual(
                self.state.down(3),
                solver16.State([1, 2, 3, 16, 5, 6, 7, 4, 9, 10, 11, 8, 13, 14, 15, 12]))

    def test_left(self):
        self.assertEqual(
                self.state.left(0),
                solver16.State([2, 3, 4, 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.left(1),
                solver16.State([1, 2, 3, 4, 6, 7, 8, 5, 9, 10, 11, 12, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.left(2),
                solver16.State([1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 9, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.left(3),
                solver16.State([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 13]))

    def test_right(self):
        self.assertEqual(
                self.state.right(0),
                solver16.State([4, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.right(1),
                solver16.State([1, 2, 3, 4, 8, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.right(2),
                solver16.State([1, 2, 3, 4, 5, 6, 7, 8, 12, 9, 10, 11, 13, 14, 15, 16]))

        self.assertEqual(
                self.state.right(3),
                solver16.State([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 13, 14, 15]))

    def test_num_pos(self):
        self.assertEqual(self.state.correct_pos(1), (0, 0))
        self.assertEqual(self.state.correct_pos(2), (1, 0))
        self.assertEqual(self.state.correct_pos(16), (3, 3))
        self.assertEqual(self.state.correct_pos(11), (2, 2))
        self.assertEqual(self.state.correct_pos(10), (1, 2))

        smaller_state = solver16.State(range(1, 10))
        self.assertEqual(smaller_state.correct_pos(9), (2, 2))
        self.assertEqual(smaller_state.correct_pos(1), (0, 0))
        # This one is bogus, but it still works:
        self.assertEqual(smaller_state.correct_pos(10), (0, 3))

    def test_four_id(self):
        for i in range(4):
            self.assertEqual(self.state, self.state.right(i).right(i).right(i).right(i))
            self.assertEqual(self.state, self.state.left(i).left(i).left(i).left(i))
            self.assertEqual(self.state, self.state.up(i).up(i).up(i).up(i))
            self.assertEqual(self.state, self.state.down(i).down(i).down(i).down(i))

    def test_ids(self):
        for i in range(4):
            self.assertEqual(self.state, self.state.right(i).left(i))
            self.assertEqual(self.state, self.state.up(i).down(i))

    def test_2x2(self):
        import itertools
        perms = map(list, list(itertools.permutations([1, 2, 3, 4])))
        for perm in perms:
            state = solver16.State(perm)
            # print state.arr
            answer = solver16.brute_bfs(state)
            # print answer.moves
            # print
            self.assertIsNotNone(answer)

    # def test_swap_3x3(self):
    #     begin = [1, 6, 3, 4, 5, 2, 7, 8, 9]
    #     state = solver16.State(begin)
    #     # answer = solver16.astar(state, solver16.print_heuristic(solver16.correct_row_col))
    #     # answer = solver16.bestfirst(state, solver16.h1)
    #     # answer = solver16.brute_bfs(state)
    #     print answer
    #     print
    #     self.assertIsNotNone(answer)

    def test_swap_2x2(self):
        begin = [3, 2, 1, 4]
        state = solver16.State(begin)
        answer = solver16.brute_bfs(state)
        # print answer
        # print
        self.assertIsNotNone(answer)

    def test_astar_2x2(self):
        import itertools
        perms = map(list, list(itertools.permutations([1, 2, 3, 4])))
        for perm in perms:
            state = solver16.State(perm)
            answer = solver16.astar(state, solver16.h1)
            self.assertIsNotNone(answer)

    # def test_one_move(self):
    #     begin = [1, 2, 4, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    #     state = solver16.State(begin)
    #     answer = solver16.brute_bfs(state)
    #     print answer
    #     print
    #     self.assertIsNotNone(answer)

    def test_opt_moves(self):
        from solver16 import opt_moves
        self.assertEqual([], [])
        self.assertEqual(["R1"], opt_moves(["R1"]))
        self.assertEqual(["R1", "D1"], opt_moves(["R1", "D1"]))
        self.assertEqual(["L1"], opt_moves(["R1", "R1", "R1"]))
        self.assertEqual(["U1"], opt_moves(["D1", "D1", "D1"]))
        self.assertEqual(["U1", "D1"], opt_moves(["D1", "D1", "D1", "D1"]))
        self.assertEqual(["U1", "D1"], opt_moves(["D1", "D1", "D1", "D1"]))
        self.assertEqual(["U1", "D1", "L1"], opt_moves(["D1", "D1", "D1", "D1", "R1", "R1", "R1"]))

if __name__ == "__main__":
    unittest.main()
