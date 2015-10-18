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
        # print subset_idxs
        for dice in rethrow_possibilities(dice, subset_idxs):
            dice_tuple = tuple(sorted(dice))
            try:
                entry = table[dice_tuple]
                entry["p"] += 1
            except KeyError:
                table[dice_tuple] = { "p" : 1 }

    # Next, we generate maximum points we could get from a dice set, with which
    # card to use to get that points
    for k, v in table.iteritems():
        for card, (card_points, _) in available_cards.iteritems():
            current_max = v.get("max_points", -1)
            cp = card_points(k)
            if cp > current_max:
                v["max_points"] = cp
                v["card"] = card

    # Normalize probabilities
    total = 0
    for v in table.itervalues():
        total += v["p"]

    alpha = 1.0 / float(total)

    for v in table.itervalues():
        v["p"] *= alpha

    for k, v in table.iteritems():
        print k, v

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

    Note that in this type of cards, it always makes sense to re-throw some
    dice, except when all of the dice in the set is == n.
    """
    # index of dices that are not n
    non_Ns_idx = filter_idx(lambda w: w != n, dice)
    non_Ns = len(non_Ns_idx)

    # number of Ns in our initial set
    ns = len(dice) - non_Ns

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
    return n_rethrows(dice, 1)

def doses_rethrows(dice):
    return n_rethrows(dice, 2)

def treses_rethrows(dice):
    return n_rethrows(dice, 3)

def cuatros_rethrows(dice):
    return n_rethrows(dice, 4)

def cincos_rethrows(dice):
    return n_rethrows(dice, 5)

def seises_rethrows(dice):
    return n_rethrows(dice, 6)

###############################################################################

def repetitions(lst):
    m = {}

    for e in lst:
        m[e] = m.get(e, 0) + 1

    return [ v for _, v in m.iteritems() ]

# def prob_points(lst):
#     """
#     Given a list of (dice set, points), calculate average points.
#     Note that dice sets in the list may have different number of dice.
#     """
#     probs = []
#
#     for dice, points in lst:
#         dice_prob = (1.0 / 6.0) ** len(dice)
#         dice_reps = repetitions(dice)
#         prob      = dice_prob / float(mult(map(lambda r: math.factorial(r), dice_reps)))
#
#         probs.append((prob, points))
#
#     return normalize_outcomes(probs)

def pupusa_de_queso_rethrows(dice):
    s = set(dice)
    groups = group_dice(dice)

    if len(s) == 5:
        return ( [], pupusa_de_queso_points(dice) )

    # First condition, we need 5 distinct dice
    elif len(s) < 5:
        # For every group with more than one dice, we re-throw all the dice
        # except first one in that group
        rethrows = []

        for group in groups:
            if len(group) > 1:
                rethrows.extend(group[1:])

        # One last update, if we have both ones and sixes, then we re-throw all
        # of ones or sixes:
        if len(groups[0]) != 0 and len(groups[5]) != 0:
            # Let's re-throw sixes
            # We only add first die because the rest is added in previous loop
            rethrows.apppend(group[5][0])

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

    groups = group_dice(dice)

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

    groups = group_dice(dice)

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

    groups = group_dice(dice)
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

    groups = group_dice(dice)
    biggest_group_idx = max_by(len, groups)
    rethrows = []

    for group_idx, group in enumerate(groups):
        if group_idx != biggest_group_idx:
            rethrows.extend(group)

    return rethrows

def quintupulo_rethrows(dice):
    # Only way to get points is to collect all of them into one group
    groups = group_dice(dice)
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
