# Automatic Zacate game player
# B551 Fall 2015
# Omer Sinan Agacan - oagacan
#
# Based on skeleton code by D. Crandall

################################################################################
# NOTE [Brute-force approach]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The way I attack problems is usually this: I first design or maybe even
# implement a brute-force solution, then if needed I optimize on that.
#
# Let's think about how we can come up with a brute-force solution for this
# problem.
#
# Let's say the points we currently get is P. We can consider re-throwing all
# subset of our dice. Given that we have 5 dice, that'd make 2^5 = 32 dice
# sets(actually this is not really a set since we have repetitions).
#
# Then for each subset, we consider what happens if we re-throw that subset.
# Let's say we consider a subset with 4 dice. We have 6^4 = 1296 different
# outcomes, each one has same probability, but we have repetitions. For every
# outcome, we check maximum points we could get.
#
# At this point here's all the information we have:
#
# - Best points we can get, without any re-throws.
# - For each subset of dice, points we can get with a re-throw. Each one has
#   same probability(but we have repetitions).
#
# Now, under what circumstances should we re-throw instead of accepting current
# dice set? I have no ideas, but let's say we re-throw if we have at least 30%
# of probability that we'll get a better point.
#
# Now we need to calculate some probabilities. Our results tables have
# repetitions. If we have two entries in table entry for re-throwing all 5 dice
# that give us same points, this means that probability of having this points is
# actually not 1 / all_possibilities, it's larger.
#
# So we need to remove repetitions and generate probabilities.
#
# Here's how we generate the table for this:
#
# - For each _distinct_ subset of current dice:
#   (by _distinct_ we mean that if we currently have [1, 1, 1, 1, 2],
#   [0, 1], [0, 2], [0, 3] etc. are all the same)
#
#   - We check if the outcome is in the table. If it is, we increment it's
#     probability by one.
#
#   - If it's not in the table, we create the entry with probability one.
#
# - Then, for each entry in the table, we calculate maximum points we get, and
#   note the card that gives this. (of course we take care of previously used
#   cards etc.)
#
# - Then, we normalize probabilities. We apply the usual procedure etc.
#
# - If there's a chance that with more than 30% probability we increase our
#   income, then we do the re-throw.
#
# (We should probably play around with 30% to find a better number here)
#
# Of course, this is a very naive implementation. We don't consider the fact
# that we can re-throw one more time if first time we don't get good result. We
# also don't consider the fact that with current set of dice, we may consider
# having less points, just to save some cards to better sets.
#
# Still, I think it's a good spot between super powerful but hard to code vs.
# easy to code but dumb.
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

################################################################################
# Functions for determining which subset to re-throw for gaining points from
# some particular card.
#
# In cases where we already gain points, we try to increase the points.
################################################################################

# For unos through seises, we just re-throw every dice that doesn't give us any
# points.

###############################################################################
# First, some utils

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

def min_by(f, lsts):
    min_score = sys.maxint

    for idx, lst in enumerate(lsts):
        score = f(lst)
        if score < min_score:
            min_score = score
            min_idx = idx

    return min_idx

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

def mult(lst):
    """
    Like built-in sum(), but multiplies.
    """
    ret = 1
    for e in lst:
        ret *= e
    return ret

###############################################################################
# Brute-force approach, as described in NOTE [Brute-force approach]
###############################################################################

def subsets(lst):
    for set_size in range(len(lst) + 1):
        for comb in itertools.combinations(lst, set_size):
            yield comb

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

###############################################################################

# TODO: These functions should return the probability that after rethrows, we
# get the points. Otherwise they're pretty much useless. Notice that rethrowing
# less number of dice doesn't mean having higher change of getting points.
# (TODO: or does it?) Also, we may choose a move that gives us more points with
# less probability instead of a move that gives us less points with more
# probability etc.

def repeated_perm(p1, n, p2, m):
    return ((p1 ** n) * (p2 ** m)) / (math.factorial(n) * math.factorial(m))

def average(ps):
    sum = 0
    for p, outcome in ps:
        sum += outcome * p
    return sum

def normalize_outcomes(ps):
    total_prob = 0

    for p, _ in ps:
        total_prob += p

    alpha = 1 / total_prob

    return [ (p * alpha, outcome) for (p, outcome) in ps ]

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
