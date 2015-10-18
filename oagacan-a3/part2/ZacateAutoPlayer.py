# Automatic Zacate game player
# B551 Fall 2015
# Omer Sinan Agacan - oagacan
#
# Based on skeleton code by D. Crandall

################################################################################
# NOTE [Our solution]
# ~~~~~~~~~~~~~~~~~~~
#
# Our solution is very simple. First, it doesn't take extra 35 points that comes
# from first 6 cards. Second, it's almost like a brute-force search, simply
# because 1) it was feasible(runs fast enough)  2) it returned good results(can
# achieve 200 mean score) 3) it was very easy to program.
#
# Other more advanced probabilistic solutions that I've tried(see git history),
# were too hard to program.
#
# Here's how the current solution works:
#
# We simply consider all possible re-throws. Let's say we can re-throw [1, 4].
# We consider all possible outcomes, and we take the average of maximum points
# we can get from that each possible outcome. In this example, since we're
# re-throwing 2 dice, we can have 6 ** 2 different outcomes. For every outcome,
# we consider available cards, and we note the maximum points we can get.
#
# After noting averages of every possible re-throw, we simply choose the best
# one.
#
# Note that this algorithm handles not re-throwing also. If the re-throw [] is
# gives us best result, it simply returns [] which means not re-throwing
# anything.
#
# This is too naive in so many ways. First, the best player might consider
# whether this is the first re-throw or the second, and depending on that it
# might do different moves. Second, this way of maximizing the score is probably
# not the best way. Even though I coulnd't think of a specific example, I think
# to truly maximize the points, we may sometimes want to just use a bad card at,
# only to save good cards to next turns.
#
# Heart of the algorithm is search() and best_card() functions.
#
# Best observed result: 204.58 (mean)
#
################################################################################

from ZacateState import Dice
from ZacateState import Scorecard

import itertools
import math
import random
import sys

################################################################################
# Calculating points we can add to our score from current set of dice
################################################################################

def __count_die(dice, n):
    ret = 0
    for die in dice:
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
    s = sorted(dice)
    if s == [1, 2, 3, 4, 5] or s == [2, 3, 4, 5, 6]:
        return 40
    return 0

def pupusa_de_frijol_points(dice):
    c1 = 3 in dice and 4 in dice

    c1_1 = 1 in dice and 2 in dice
    c1_2 = 2 in dice and 5 in dice
    c1_3 = 5 in dice and 6 in dice

    if c1 and (c1_1 or c1_2 or c1_3):
        return 30
    return 0

def elote_points(dice):
    ds = set(dice)
    if len(ds) == 2:
        return 25
    return 0

def triple_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 3:
            return sum(dice)
    return 0

def cuadruple_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 4:
            return sum(dice)
    return 0

def quintupulo_points(dice):
    for i in range(1, 7):
        if __count_die(dice, i) >= 5:
            return 50
    return 0

def tamal_points(dice):
    return sum(dice)

###############################################################################
# First, some utils

def max_by(f, lsts):
    # This is yet another weird Python "convenience", it doesn't provide
    # sys.minint, and -sys.maxint is in range. minint is actually
    # (-sys.maxint - 1).
    max_score = - sys.maxint
    max_idx = None

    for idx, lst in enumerate(lsts):
        score = f(lst)
        if score > max_score:
            max_score = score
            max_idx = idx

    return max_idx

def subsets(lst):
    for set_size in range(len(lst) + 1):
        for comb in itertools.combinations(lst, set_size):
            yield comb

###############################################################################
# Brute-force approach, as described in NOTE [Brute-force approach]
###############################################################################

def rethrow_possibilities(dice, rethrow_idxs):
    # TODO: Implementing this as a generator is tricky, we're returning a list
    # for now.
    rethrows = len(rethrow_idxs)
    ret = [ dice[:] for _ in range(6 ** rethrows) ]

    prods = itertools.product(range(1, 7), repeat=rethrows)

    for i, p in enumerate(prods):
        for idx_idx, idx in enumerate(rethrow_idxs):
            ret[i][idx] = p[idx_idx]

    return ret

def search(dice, available_cards):
    idxs = range(len(dice))

    table = {}

    for subset_idxs in subsets(idxs):
        subset_idxs_tuple = tuple(sorted(subset_idxs))

        rethrow_points = 0
        rethrows       = 0

        for outcome in rethrow_possibilities(dice, subset_idxs):
            outcome_tuple = tuple(sorted(outcome))

            rethrow_points += best_card(outcome, available_cards)[1]
            rethrows       += 1

        table[subset_idxs_tuple] = float(rethrow_points) / float(rethrows)

    return table

def best_card(dice, cards):
    max_points = -1

    for c, p in cards.iteritems():
        points = p(dice)
        if points > max_points:
            max_points = points
            max_card = c

    return (max_card, max_points)

################################################################################
# Player
################################################################################

ALL_CARDS = set(Scorecard.Categories)

# A map from category names to point and re-throw functions
CATFNS = {
        "unos": unos_points,
        "doses": doses_points,
        "treses": treses_points,
        "cuatros": cuatros_points,
        "cincos": cincos_points,
        "seises": seises_points,
        "pupusa de queso": pupusa_de_queso_points,
        "pupusa de frijol": pupusa_de_frijol_points,
        "elote": elote_points,
        "triple": triple_points,
        "cuadruple": cuadruple_points,
        "quintupulo": quintupulo_points,
        "tamal": tamal_points,
        }

def available_cards(scorecard):
    keys = ALL_CARDS - set(scorecard.scorecard.keys())

    ret = {}
    for key in keys:
        ret[key] = CATFNS[key]
    return ret


class MyPlayer1:

    def __init__(self):
        pass

    def do_ur_best(self, dice, scorecard):
        cards = available_cards(scorecard)
        outcomes = search(dice.dice, cards).items()
        best_outcome_idx = max_by(lambda (k, v): v, outcomes)
        return list(outcomes[best_outcome_idx][0])

    def first_roll(self, dice, scorecard):
        return self.do_ur_best(dice, scorecard)

    def second_roll(self, dice, scorecard):
        return self.do_ur_best(dice, scorecard)

    def third_roll(self, dice, scorecard):
        cards = available_cards(scorecard)
        return best_card(dice.dice, cards)[0]


class TotalN00b:
    def first_roll(self, dice, scorecard):
        return [0] # always re-roll first die (blindly)

    def second_roll(self, dice, scorecard):
        return [1, 2] # always re-roll second and third dice (blindly)

    def third_roll(self, dice, scorecard):
        # stupidly just randomly choose a category to put this in
        return random.choice(list(self.__available_cards(scorecard)))

    def __available_cards(self, scorecard):
        return ALL_CARDS - set(scorecard.scorecard.keys())


# ZacateAutoPlayer = TotalN00b
ZacateAutoPlayer = MyPlayer1

################################################################################

if __name__ == "__main__":
    import sys
    print "You should be running zacate.py"
    sys.exit(1)
