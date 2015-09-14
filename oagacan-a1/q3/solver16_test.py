import solver16

import unittest

class TestMoveMethods(unittest.TestCase):
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
    #     answer = solver16.brute_bfs(state)
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

    # def test_one_move(self):
    #     begin = [1, 2, 4, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    #     state = solver16.State(begin)
    #     answer = solver16.brute_bfs(state)
    #     print answer
    #     print
    #     self.assertIsNotNone(answer)

if __name__ == "__main__":
    unittest.main()
