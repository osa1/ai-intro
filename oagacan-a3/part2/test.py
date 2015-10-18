import unittest

from ZacateAutoPlayer import *

class TestPoints(unittest.TestCase):
    def setUp(self):
        self.player = ZacateAutoPlayer()

    def test_unos(self):
        dice = [1, 2, 3, 4, 1]
        self.assertEqual(2, unos_points(dice))

        dice = [2, 2, 3, 4, 5]
        self.assertEqual(0, unos_points(dice))

    def test_doses(self):
        dice = [1, 2, 3, 4, 1]
        self.assertEqual(2, doses_points(dice))

        dice = [2, 2, 3, 4, 6]
        self.assertEqual(4, doses_points(dice))

    def test_treses(self):
        dice = [1, 2, 3, 4, 1]

        self.assertEqual(3, treses_points(dice))

        dice = [2, 2, 3, 4, 3]
        self.assertEqual(6, treses_points(dice))

    def test_pupusa_de_queso(self):
        dice = [5, 2, 3, 4, 1]
        self.assertEqual(40, pupusa_de_queso_points(dice))

        dice = [2, 3, 4, 5, 6]
        self.assertEqual(40, pupusa_de_queso_points(dice))

        dice[0] = 1
        self.assertEqual(0, pupusa_de_queso_points(dice))

    def test_pupusa_de_frijol(self):
        dice = [4, 3, 2, 1, 6]
        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice = [4, 3, 2, 5, 6]
        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice = [4, 3, 1, 5, 6]
        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice = [4, 3, 3, 5, 5]
        self.assertEqual(0, pupusa_de_frijol_points(dice))

    def test_elote(self):
        dice = [1, 2, 1, 2, 1]
        self.assertEqual(25, elote_points(dice))

        dice = [1, 2, 3, 2, 1]
        self.assertEqual(0, elote_points(dice))

    def test_triple(self):
        dice = [1, 2, 1, 2, 1]
        self.assertEqual(7, triple_points(dice))

        dice = [1, 2, 3, 2, 1]
        self.assertEqual(0, triple_points(dice))

    def test_cuadruple(self):
        dice = [1, 2, 1, 1, 1]
        self.assertEqual(6, cuadruple_points(dice))

        dice = [1, 2, 1, 1, 3]
        self.assertEqual(0, cuadruple_points(dice))

    def test_quintupulo_points(self):
        dice = [1, 1, 1, 1, 1]
        self.assertEqual(50, quintupulo_points(dice))

        dice = [2, 1, 1, 1, 1]
        self.assertEqual(0, quintupulo_points(dice))

    def test_tamal_points(self):
        dice = [1, 2, 3, 4, 5]
        self.assertEqual(sum(dice), tamal_points(dice))

    ############################################################################
    # Testing re-throws
    ############################################################################

    def test_filter_idx(self):
        self.assertEqual([1, 3, 5], filter_idx(lambda w: w == 1, [2, 1, 2, 1, 2, 1]))
        self.assertEqual([],        filter_idx(lambda w: w == 10, []))
        self.assertEqual([],        filter_idx(lambda w: w == 10, [20]))

    def test_find_idxs(self):
        self.assertEqual([1, 3, 5], find_idx(1,  [2, 1, 2, 1, 2, 1]))
        self.assertEqual([],        find_idx(10, []))
        self.assertEqual([],        find_idx(10, [20]))

    def test_group_dice(self):
        self.assertEqual([[0, 5], [1], [2], [], [3, 4], []], group_dice([1, 2, 3, 5, 5, 1]))

    def test_min_by(self):
        self.assertEqual(3, min_by(len, [[1], [2, 3], [4, 5, 6], []]))
        self.assertEqual(0, min_by(len, [[1], [2, 3], [4, 5, 6]]))

    def test_max_by(self):
        self.assertEqual(2, max_by(len, [[1], [2, 3], [4, 5, 6], []]))
        self.assertEqual(0, max_by(len, [[1, 2, 3, 4], [2, 3], [4, 5, 6]]))

    def test_mult(self):
        self.assertEqual(1, mult([]))
        self.assertEqual(2, mult([1, 2]))
        self.assertEqual(0, mult([0, 1, 2]))

    def test_normalize_outcomes(self):
        outcomes = [ (0.123, 10), (0.02323, 20), (0.8383, 30) ]
        outcomes = normalize_outcomes(outcomes)

        ps = 0
        for (p, _) in outcomes:
            ps += p

        self.assertEqual(1, ps)

    def test_average(self):
        outcomes = [ (0.4, 6), (0.6, 4) ]
        self.assertEqual(4.8, round(average(outcomes), 1))

    def test_subsets(self):
        for i in range(5):
            lst = range(i)
            self.assertEqual(2 ** len(lst), len(list(subsets(lst))))

        self.assertEqual([(), (1,), (2,), (1, 2)], list(subsets([1, 2])))

    def test_rethrow_possibilities(self):
        self.assertEqual([[1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 2]],
                rethrow_possibilities([1, 2], [0]))

        self.assertEqual([[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6]],
                rethrow_possibilities([1, 2], [1]))

        # print rethrow_possibilities([1, 2], [0, 1])

################################################################################

if __name__ == "__main__":
    search([1, 2, 3, 4, 5, 6], CATFNS)

    print "Running unit tests..."

    unittest.main()
