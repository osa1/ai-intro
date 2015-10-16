# Automatic Zacate game player
# B551 Fall 2015
# Omer Sinan Agacan - oagacan
#
# Based on skeleton code by D. Crandall

################################################################################

from ZacateState import Dice
from ZacateState import Scorecard
import random

ALL_CARDS = set(Scorecard.Categories)

class ZacateAutoPlayer:

    def __init__(self):
        pass

    def first_roll(self, dice, scorecard):
        return [0] # always re-roll first die (blindly)

    def second_roll(self, dice, scorecard):
        return [1, 2] # always re-roll second and third dice (blindly)

    def third_roll(self, dice, scorecard):
        # stupidly just randomly choose a category to put this in
        return random.choice(list(self.__available_cards(scorecard)))

    def __available_cards(self, scorecard):
        return ALL_CARDS - set(scorecard.scorecard.keys())


################################################################################
# Calculating points we can add to our score from current set of dice
################################################################################

def __count_die(dice, n):
    ret = 0
    for die in dice.dice:
        if die == n:
            ret += 1
    return ret

def __mult_dice(dice, n):
    """Count die that is equal to n. Score is n * count."""
    return n * __count_die(dice, n)

def unos_points(dice):
    return __mult_dice(dice, 1)

def doses_points(dice):
    return __mult_dice(dice, 2)

def treses_points(dice):
    return __mult_dice(dice, 3)

def cuatros_points(dice):
    return __mult_dice(dice, 4)

def cincos_points(dice):
    return __mult_dice(dice, 5)

def seises_points(dice):
    return __mult_dice(dice, 6)

def pupusa_de_queso_points(dice):
    s = sorted(dice.dice)
    if s == [1, 2, 3, 4, 5] or s == [2, 3, 4, 5, 6]:
        return 40
    return 0

def pupusa_de_frijol_points(dice):
    c1 = 3 in dice.dice and 4 in dice.dice

    c1_1 = 1 in dice.dice and 2 in dice.dice
    c1_2 = 2 in dice.dice and 5 in dice.dice
    c1_3 = 5 in dice.dice and 6 in dice.dice

    if c1 and (c1_1 or c1_2 or c1_3):
        return 30
    return 0

def elote_points(dice):
    ds = set(dice.dice)
    if len(ds) == 2:
        return 25
    return 0

def triple_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 3:
            return sum(dice.dice)
    return 0

def cuadruple_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 4:
            return sum(dice.dice)
    return 0

def quintupulo_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 5:
            return 50
    return 0

def tamal_points(dice):
    return sum(dice.dice)

################################################################################
# Functions for determining which subset to re-throw for gaining points from
# some particular card.
#
# In cases where we already gain points, we try to increase the points.
################################################################################

# For unos through seises, we just re-throw every dice that doesn't give us any
# points.

def filter_idx(p, lst):
    """A helper function that works like filter, except returns indexes of
    elements that passed the test instead of returning a new list.
    """
    idxs = []
    for i in range(len(lst)):
        if p(lst[i]):
            idxs.append(i)
    return idxs

def find_idx(n, lst):
    """A specialized version of 'filter_idx(lambda w: w == n, lst)'.
    """
    idxs = []
    for i in range(len(lst)):
        if n == lst[i]:
            idxs.append(i)
    return idxs

def group_dice(lst):
    """Returns a list of 6 lists, each one holds indexes of corresponding dice
    of it's own index. Example:

    >>> group_dice([1, 2, 3, 5, 5, 1])
    [[0, 5], [1], [2], [], [3, 4], []]
    """
    ret = [ [] for _ in range(6) ]
    for idx in range(len(lst)):
        ret[lst[idx] - 1].append(idx)
    return ret

def unos_rethrows(dice):
    return filter_idx(lambda d: d != 1, dice.dice)

def doses_rethrows(dice):
    return filter_idx(lambda d: d != 2, dice.dice)

def treses_rethrows(dice):
    return filter_idx(lambda d: d != 3, dice.dice)

def cuatros_rethrows(dice):
    return filter_idx(lambda d: d != 4, dice.dice)

def cincos_rethrows(dice):
    return filter_idx(lambda d: d != 5, dice.dice)

def seises_rethrows(dice):
    return filter_idx(lambda d: d != 6, dice.dice)

def pupusa_de_queso_rethrows(dice):
    s = set(dice.dice)
    groups = group_dice(dice.dice)

    # I'm not sure if we should handle this case, but first check if we need to
    # re-throw at all
    if len(s) == 5:
        return []

    # First condition, we need 5 distinct dice
    elif len(s) < 5:
        # For every group with more than one dice, we re-throw all the dice
        # except first one in that group
        rethrows = []

        for group in groups:
            if len(group) > 1:
                rethrows.extend(group[1:])

        # TODO: This is not quite right. We may want to throw al 6s if we have
        # a one, for example.

        return rethrows

    # Second condition, either 1 or 6 must be missing
    else:
        if len(groups[0]) > 1 and len(groups[5]) > 1:
            if len(groups[0]) < len(groups[5]):
                return groups[0]
            return groups[5]
        else:
            # There's a group with more than one die, find it
            for group in groups:
                if len(group) > 1:
                    return [group[0]]

    raise RuntimeError("Checks are not exhaustive.")

def pupusa_de_frijol_rethrows(dice):
    # One of these conditions should hold:
    #   - 5 and 6 are missing
    #   - 1 and 6 are missing
    #   - 1 and 2 are missing
    pass


################################################################################

if __name__ == "__main__":
    import sys
    print "You should be running zacate.py"
    sys.exit(1)
