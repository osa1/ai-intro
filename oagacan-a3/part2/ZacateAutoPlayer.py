# Automatic Zacate game player
# B551 Fall 2015
# Omer Sinan Agacan - oagacan
#
# Based on skeleton code by D. Crandall

################################################################################

from ZacateState import Dice
from ZacateState import Scorecard

import math
import random
import sys

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

    for idx, lst in enumerate(lsts):
        score = f(lst)
        if score > max_score:
            max_score = score
            max_idx = idx

    return max_idx

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

def n_rethrows(dice, n):
    """
    Return a set of dice to re-throw to maximize expected points from this dice
    set. Points are calculated according to first six cards("unos", "doses",
    "treses" etc. for example we multiply number of 2s with 2 for "doses",
    number of 3s with 3 for "treses" etc.).
    """
    # index of dices that are not n
    non_Ns_idx = filter_idx(lambda w: w != n, dice.dice)
    non_Ns = len(non_Ns_idx)

    # number of Ns in our initial set
    ns = len(dice.dice) - non_Ns

    outcomes = []

    for i in range(non_Ns + 1):
        # repeated permutation of 'i' wanted dice and 'non_Ns - i' any other dice
        prob = repeated_perm((1.0 / 6.0) ** i, i, (5.0 / 6.0) ** (non_Ns - i), non_Ns)
        # the points we get with this probability
        point = (ns + i) * n

        outcomes.append((prob, point))

    # since we consider all possibilities, probabilities should add up to 1
    outcomes = normalize_outcomes(outcomes)

    avg_points = average(outcomes)

    return (non_Ns_idx, avg_points)

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
    if pupusa_de_frijol_points(dice) != 0:
        return []

    # One of these conditions should hold:
    #   - We have 1, 2, 3, 4
    #   - We have 2, 3, 4, 5
    #   - We have 3, 4, 5, 6

    groups = group_dice(dice.dice)

    # Consider case 1
    case1_rethrows = []
    for group_idx, group in enumerate(groups):
        if group_idx in [1, 2, 3, 4]:
            case1_rethrows.extend(group[1:])
        else:
            case1_rethrows.extend(group)

    # Consider case 2
    case2_rethrows = []
    for group_idx, group in enumerate(groups):
        if group_idx in [2, 3, 4, 5]:
            case2_rethrows.extend(group[1:])
        else:
            case2_rethrows.extend(group)

    # Consider case 3
    case3_rethrows = []
    for group_idx, group in enumerate(groups):
        if group_idx in [3, 4, 5, 6]:
            case3_rethrows.extend(group[1:])
        else:
            case3_rethrows.extend(group)

    rethrows = [case1_rethrows, case2_rethrows, case3_rethrows]
    return rethrows[min_by(len, rethrows)]

def elote_rethrows(dice):
    # 3 same + 2 same

    if elote_points(dice) != 0:
        return []

    groups = group_dice(dice.dice)

    # Two pass, because len(groups) == 5.
    biggest_group_idx = max_by(len, groups)

    second_biggest_group_idx = None
    second_biggest_group_len = None

    for group_idx, group in enumerate(groups):
        if group_idx == biggest_group_idx:
            continue

        if second_biggest_group_idx == None or len(group) > second_biggest_group_len:
            second_biggest_group_idx = group_idx
            second_biggest_group_len = len(group)

    # Now that we choose which groups to collect dice into, re-throw everything
    # else.
    rethrows = []

    for group_idx, group in enumerate(groups):
        if group_idx != biggest_group_idx and group_idx != second_biggest_group_idx:
            rethrows.extend(group)

    return rethrows

def triple_rethrows(dice):
    # 3 same

    # TODO: This algorithm is probably borked. Let's say we have this:
    # [1, 1, 2, 2, 3]
    # Should we re-throw all 2s? We should calculate and see what's the best
    # move here.

    if triple_points(dice) != 0:
        return []

    groups = group_dice(dice.dice)
    biggest_group_idx = max_by(len, groups)
    rethrows = []

    for group_idx, group in enumerate(groups):
        if group_idx != biggest_group_idx:
            rethrows.extend(group)

    return rethrows

def cuadruple_rethrows(dice):
    # 4 same
    # This is like triple_rethrows, except we don't need to consider cases like
    # [1, 1, 2, 2, 3]

    if cuadruple_points(dice) != 0:
        return []

    groups = group_dice(dice.dice)
    biggest_group_idx = max_by(len, groups)
    rethrows = []

    for group_idx, group in enumerate(groups):
        if group_idx != biggest_group_idx:
            rethrows.extend(group)

    return rethrows

def quintupulo_rethrows(dice):
    # Only way to get points is to collect all of them into one group
    groups = group_dice(dice.dice)
    biggest_group_idx = max_by(len, groups)
    rethrows = []

    # The algorithm is same as cuadruple, but probabilities are difference.
    # Currently we're not calculating probabilities so essentially they're same
    # until probabilities are fixed. FIXME
    for group_idx, group in enumerate(groups):
        if group_idx != biggest_group_idx:
            rethrows.extend(group)

    return rethrows

def tamal_rethrows(dice):
    # This case is interesting. We get points no matter what, but we can
    # increase points with some trivial re-throws. For example, we can always
    # re-throw ones. I'm leaving this case for now. TODO
    return []

################################################################################
# Player
################################################################################

ALL_CARDS = set(Scorecard.Categories)

# A map from category names to point and re-throw functions
CATFNS = {
        "unos": (unos_points, unos_rethrows),
        "doses": (doses_points, doses_rethrows),
        "treses": (treses_points, treses_rethrows),
        "cuatros": (cuatros_points, cuatros_rethrows),
        "cincos": (cincos_points, cincos_rethrows),
        "seises": (seises_points, seises_rethrows),
        "pupusa de queso": (pupusa_de_queso_points, pupusa_de_queso_rethrows),
        "pupusa_de_frijol": (pupusa_de_frijol_points, pupusa_de_frijol_rethrows),
        "elote": (elote_points, elote_rethrows),
        "triple": (triple_points, triple_rethrows),
        "cuadruple": (cuadruple_points, cuadruple_rethrows),
        "quintupulo": (quintupulo_points, quintupulo_rethrows),
        "tamal": (tamal_points, tamal_rethrows)
        }

class ZacateAutoPlayer:

    # An attempt:
    # We generate best points we can get right now, and points we can get with
    # a re-throw, with possibilities.
    #
    # Some potential moves will risk current points. In that case we need to
    # consider possibilities and somehow decide whether to re-throw.
    #
    # It may be the case that re-throwing a set of dice will possibly make
    # multiple cards available. We should somehow check for that.

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

if __name__ == "__main__":
    import sys
    print "You should be running zacate.py"
    sys.exit(1)
