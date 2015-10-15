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


################################################################################

if __name__ == "__main__":
    unittest.main()
