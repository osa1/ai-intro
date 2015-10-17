import unittest

from ZacateAutoPlayer import *
from ZacateState import Dice

class TestPoints(unittest.TestCase):
    def setUp(self):
        self.player = ZacateAutoPlayer()

    def test_unos(self):
        dice = Dice()
        dice.dice = [1, 2, 3, 4, 1]

        self.assertEqual(2, unos_points(dice))

        dice.dice = [2, 2, 3, 4, 5]
        self.assertEqual(0, unos_points(dice))

    def test_doses(self):
        dice = Dice()
        dice.dice = [1, 2, 3, 4, 1]

        self.assertEqual(2, doses_points(dice))

        dice.dice = [2, 2, 3, 4, 6]
        self.assertEqual(4, doses_points(dice))

    def test_treses(self):
        dice = Dice()
        dice.dice = [1, 2, 3, 4, 1]

        self.assertEqual(3, treses_points(dice))

        dice.dice = [2, 2, 3, 4, 3]
        self.assertEqual(6, treses_points(dice))

    def test_pupusa_de_queso(self):
        dice = Dice()
        dice.dice = [5, 2, 3, 4, 1]
        self.assertEqual(40, pupusa_de_queso_points(dice))

        dice.dice = [2, 3, 4, 5, 6]
        self.assertEqual(40, pupusa_de_queso_points(dice))

        dice.dice[0] = 1
        self.assertEqual(0, pupusa_de_queso_points(dice))

    def test_pupusa_de_frijol(self):
        dice = Dice()
        dice.dice = [4, 3, 2, 1, 6]

        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice.dice = [4, 3, 2, 5, 6]
        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice.dice = [4, 3, 1, 5, 6]
        self.assertEqual(30, pupusa_de_frijol_points(dice))

        dice.dice = [4, 3, 3, 5, 5]
        self.assertEqual(0, pupusa_de_frijol_points(dice))

    def test_elote(self):
        dice = Dice()
        dice.dice = [1, 2, 1, 2, 1]
        self.assertEqual(25, elote_points(dice))

        dice.dice = [1, 2, 3, 2, 1]
        self.assertEqual(0, elote_points(dice))

    def test_triple(self):
        dice = Dice()
        dice.dice = [1, 2, 1, 2, 1]
        self.assertEqual(7, triple_points(dice))

        dice.dice = [1, 2, 3, 2, 1]
        self.assertEqual(0, triple_points(dice))

    def test_cuadruple(self):
        dice = Dice()
        dice.dice = [1, 2, 1, 1, 1]
        self.assertEqual(6, cuadruple_points(dice))

        dice.dice = [1, 2, 1, 1, 3]
        self.assertEqual(0, cuadruple_points(dice))

    def test_quintupulo_points(self):
        dice = Dice()
        dice.dice = [1, 1, 1, 1, 1]
        self.assertEqual(50, quintupulo_points(dice))

        dice.dice = [2, 1, 1, 1, 1]
        self.assertEqual(0, quintupulo_points(dice))

    def test_tamal_points(self):
        dice = Dice()
        dice.dice = [1, 2, 3, 4, 5]
        self.assertEqual(sum(dice.dice), tamal_points(dice))

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

    def test_n_rethrows(self):
        dice = Dice()

        dice.dice = [1, 1, 1, 1, 2]
        (rethrows, point) = n_rethrows(dice, 1)
        self.assertEqual([4], rethrows)
        self.assertEqual(4.17, round(point, 2))

        dice.dice = [2, 1, 2, 2, 2]
        (rethrows, point) = n_rethrows(dice, 2)
        self.assertEqual([1], rethrows)
        self.assertEqual(8.33, round(point, 2))

    def test_unos_rethrow(self):
        dice = Dice()
        dice.dice = [1, 2, 1, 2, 1]

        self.assertEqual([1, 3], unos_rethrows(dice)[0])

    def test_doses_no_rethrow(self):
        dice = Dice()
        dice.dice = [2, 2, 2, 2, 2]

        self.assertEqual(([], 10), doses_rethrows(dice))

    def test_pupusa_de_queso_rethrows(self):
        dice = Dice()

        dice.dice = [2, 4, 1, 3, 5]
        self.assertEqual([], pupusa_de_queso_rethrows(dice))

        # TODO: We actually have multiple choices with same probabilities,
        # maybe make tests more flexible for this

        dice.dice = [2, 4, 1, 3, 1]
        self.assertEqual([4], pupusa_de_queso_rethrows(dice))

        dice.dice = [1, 1, 1, 1, 1]
        self.assertEqual([1, 2, 3, 4], pupusa_de_queso_rethrows(dice))

    def test_pupusa_de_frijol_rethrows(self):
        dice = Dice()

        dice.dice = [1, 2, 4, 4, 5]

        # TODO: We have two possible moves with same probabilities here:
        #    we can target [1, 2, 3, 4] and rethrow 3 and 4,
        # or we can target [2, 3, 4, 5] and rethrow 0 and 3.
        # Maybe we should extend tests to take those into account when
        # comparing results.
        # self.assertEqual([3, 4], pupusa_de_frijol_rethrows(dice))
        self.assertEqual([0, 3], pupusa_de_frijol_rethrows(dice))

        # TODO: Add more tests, this looks a bit tricky.

    def test_elote_rethrows(self):
        dice = Dice()

        dice.dice = [1, 1, 2, 2, 3]
        self.assertEqual([4], elote_rethrows(dice))

        dice.dice = [1, 1, 2, 3, 4]
        # TODO: Again, we have multiple choices with same probabilities here
        self.assertEqual([3, 4], elote_rethrows(dice))

    def test_triple_rethrows(self):
        dice = Dice()

        dice.dice = [1, 2, 1, 2, 1]
        self.assertEqual([], triple_rethrows(dice))

        dice.dice = [1, 2, 1, 2, 3]
        self.assertEqual([1, 3, 4], triple_rethrows(dice))

    def test_cuadruple_rethrows(self):
        dice = Dice()

        dice.dice = [1, 2, 1, 2, 1]
        self.assertEqual([1, 3], cuadruple_rethrows(dice))

        dice.dice = [1, 2, 1, 1, 1]
        self.assertEqual([], cuadruple_rethrows(dice))

    def test_quintupulo_rethrows(self):
        dice = Dice()

        dice.dice = [1, 2, 1, 2, 1]
        self.assertEqual([1, 3], quintupulo_rethrows(dice))

        dice.dice = [1, 2, 1, 1, 1]
        self.assertEqual([1], quintupulo_rethrows(dice))

################################################################################

if __name__ == "__main__":
    unittest.main()
