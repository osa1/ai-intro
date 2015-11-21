################################################################################
# CS B551 Fall 2015, Assignment #5
#
# Omer Sinan Agacan (oagacan)
#
# (Based on skeleton code by D. Crandall)
#
################################################################################
# Report
# ~~~~~~
#
# Well, I don't know what to say here. Algorithms are pretty much implemented
# from their descriptions in the relevant wiki pages or online class slides and
# work sheets.
#
# Some implementation details are commented in the code.
#
# Parameters and experiments
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The story with number of samples for MCMC and max marginal: In my tests I
# realized that after 500 samples the the accuracy is not effected by increase
# in samples. (I tried up to 4000 samples)
#
# One interesting experiment was this: In MCMC and max marginal, I tried
# generating initial sample using marginal probability of tags. See my comments
# in __init_sample() method for results(Didn't make any difference).
#
# Results
# ~~~~~~~
#
# ==> So far scored 2000 sentences with 29442 words.
#                    Words correct:     Sentences correct:
#    0. Ground truth:      100.00%              100.00%
#           1. Naive:       91.72%               37.65%
#         2. Sampler:       94.12%               47.35%
#    3. Max marginal:       95.23%               54.45%
#             4. MAP:       72.49%               40.45%
#            5. Best:       95.20%               54.25%
#
################################################################################

import collections
import itertools
import math
import random

SAMPLES = 500

# This is used for giving probabilities to cases that don't happen in the
# training data.
VERY_UNLIKELY = 1e-15

class Solver:

    def __init__(self):
        # P(S0)
        self.__first_tags = None

        # P(S_{t+1} | S_t)
        self.__next_tags  = None

        # P(W_t | S_t)
        self.__tag_words  = None

        # Using first_tags and next_tags, we can calculate marginal probability
        # for S_n. Since we don't know the upper bound of Ns we will need, we
        # calculate these on demand and memoize here as an optimizations.
        #
        # Initially None to avoid errors. We should initialize this with a
        # singleton list of [self.__first_tags] when we calculate
        # self.__first_tags.
        self.__tag_n      = None

        # A list of all tags
        self.__all_tags   = None

    def posterior(self, sentence, tags):
        """
        Calculate the log of the posterior probability of a given sentence with
        a given part-of-speech labeling.
        """
        prob = 1.0
        for (word_idx, (word, tag)) in enumerate(itertools.izip(sentence, tags)):
            if word_idx == 0:
                prob *= self.__first_tags[tag] * self.__tag_words[tag].get(word, VERY_UNLIKELY)
            else:
                prob *= self.__next_tags[tags[word_idx - 1]].get(tag, VERY_UNLIKELY) \
                        * self.__tag_words[tag].get(word, VERY_UNLIKELY)

        # Even though we're not giving 0 probability to anything, I believe
        # sometimes the number gets so small it's becomes 0 at the hardware
        # level. log 0 is undefined, but here let's just use NaN as an
        # indicator.
        if round(prob) == 0:
            return float('nan')

        return math.log(prob, 10)

    def train(self, data):
        """
        Do the training!

        The input is a list of pairs of tuples:
        [ ( (word1, word2, ...), (tag1, tag2, ...) ) ]
        """
        # We need 3 type of information:
        #
        # 1. P(S_1): Probabilities of tags to be appear as first word.
        #
        # 2. P(S_{t+1} | S_t): Probabilities of tags to appear as the next word,
        #    given the tag of current word.
        #
        # 3. P(W_t | S_t): Probabilities of words given tags.
        #
        # We do this the simplest way and do 3 passes on the data, each one
        # generating one of these.
        self.__first_tags = self.__calculate_first_tags(data)
        self.__tag_n      = [self.__first_tags]

        self.__next_tags  = self.__calculate_next_tags(data)
        self.__tag_words  = self.__calculate_tag_words(data)
        self.__all_tags   = self.__tag_words.keys()

        # print "self.__first_tags:", self.__first_tags
        # print "self.__next_tags:", self.__next_tags
        # print "self.__tag_words:", self.__tag_words

        # print "Calculating marginal probabilities for first 10 tags."
        for i in xrange(10):
            self.__calculate_tag_n(i)

        for i in xrange(10):
            # print "P(S_%d) = " % i
            marginal_p = self.__calculate_tag_n(i)
            # print marginal_p

            # Make sure the probabilities are normalized
            total = 0.0
            for v in marginal_p.itervalues():
                total += v
            assert round(total) == 1

    def __calculate_first_tags(self, data):
        # Note the tag of first word of every sentence. Then normalize the
        # probabilities.
        appears = {}
        total_tags = 0
        for (_, tags) in data:
            tag = tags[0]
            appears[tag] = appears.get(tag, 0) + 1
            total_tags += 1

        # Normalize probabilities
        m = 1.0 / float(total_tags)

        for first_tag, first_tag_amt in appears.iteritems():
            appears[first_tag] = first_tag_amt * m

        return appears

    def __calculate_next_tags(self, data):
        next_tags = {}
        for (_, tags) in data:
            for i in xrange(0, len(tags) - 1):
                t1 = tags[i]
                t2 = tags[i + 1]

                t1_table = next_tags.get(t1)
                if not t1_table:
                    t1_table = {}
                    next_tags[t1] = t1_table

                t1_table[t2] = t1_table.get(t2, 0) + 1

        # Normalize probabilities
        for next_tag_table in next_tags.itervalues():
            total = 0
            for t_amt in next_tag_table.itervalues():
                total += t_amt

            m = 1.0 / float(total)

            for t, t_amt in next_tag_table.iteritems():
                next_tag_table[t] = float(t_amt) * m

        return next_tags

    def __calculate_tag_words(self, data):
        tag_words = {}

        for (words, tags) in data:
            for (word, tag) in itertools.izip(words, tags):
                tag_table = tag_words.get(tag)
                if not tag_table:
                    tag_table = {}
                    tag_words[tag] = tag_table

                tag_table[word] = tag_table.get(word, 0) + 1

        # Normalize probabilities
        for (tag, words) in tag_words.iteritems():
            total = 0.0
            for word_ct in words.itervalues():
                total += word_ct

            m = 1.0 / total

            for word, word_ct in words.iteritems():
                words[word] = word_ct * m

        return tag_words

    def __calculate_tag_n(self, n):
        """
        Calculate marginal probability of P(S_n). This function memoizes it's
        results.

        (NOTE: First word is n=0, not n=1)
        """
        if len(self.__tag_n) > n:
            return self.__tag_n[n]

        p_N_prev = self.__calculate_tag_n(n-1)
        p_N      = {}

        for current_tag in self.__all_tags:
            p_current_tag = 0.0
            for prev_tag in self.__all_tags:
                p_prev_tag    = p_N_prev.get(prev_tag, 0.0)
                # Current tag given prev tag
                p_current_tag += p_prev_tag * self.__next_tags[prev_tag].get(current_tag, 0.0)

            p_N[current_tag] = p_current_tag

        # Normalize p_N
        total = 0.0
        for v in p_N.itervalues():
            total += v

        alpha = 1.0 / total
        for k, v in p_N.iteritems():
            p_N[k] = v * alpha

        # Memoize the result
        assert len(self.__tag_n) == n
        self.__tag_n.append(p_N)

        return p_N

    def naive(self, sentence):
        # List of P(S_i)s. ith index means P(S_{i+1}). (note that we already
        # know P(S0), it's recorded in 'self.__first_tags')
        p_Si_lst = []

        # NOTE: We can memoize p_Si_lst up to some i, say, 50, and the use it
        # without re-generating the whole thing from scratch here. Performance
        # is not important in this assignment, so I'll just use this.

        # This is essentially an implementation of variable elimination for
        # reducing figure 1A to 1B.
        for i in xrange(1, len(sentence)):
            # The calculation we do:
            # P(S_i) = P(S_{i} | S_{i-1}) . P(S{i-1})

            # p_prev = P(S_{i-1})
            p_prev = None
            if i == 1:
                p_prev = self.__first_tags
            else:
                p_prev = p_Si_lst[i - 2]

            p_Si = {}
            alpha = 0.0
            for current_tag in self.__all_tags:
                p_Si[current_tag] = 0.0
                for prev_tag in self.__all_tags:
                    p_prev_tag = p_prev[prev_tag]
                    p_current_tag = p_prev_tag * self.__next_tags[prev_tag].get(current_tag, 0.0)
                    alpha += p_current_tag
                    p_Si[current_tag] += p_current_tag

            # Normalize p_Si
            for k, v in p_Si.iteritems():
                p_Si[k] = v / alpha

            # Record p_Si before moving to p_S{i+1}
            p_Si_lst.append(p_Si)

        # print "Naive inference done, results:", p_Si_lst

        # Do the actual tagging, using the inferred P(S_i | W_i)s.
        tags = []
        for (word_idx, word) in enumerate(sentence):
            # Which tag makes P(S_i, W) maximum?
            max_tag = None
            max_word_prob = -1

            if word_idx == 0:
                p_Si = self.__first_tags
            else:
                p_Si = p_Si_lst[word_idx - 1]

            for tag in self.__all_tags:
                p_word = p_Si[tag] * self.__tag_words[tag].get(word, 0)
                if p_word > max_word_prob:
                    max_word_prob = p_word
                    max_tag = tag

            tags.append(max_tag)

        return [ [ tags ], [] ]

    def __init_sample(self, n_words):
        """
        First sample of tags for n_words words. The sample is generated using
        marginal probabilities of tags.
        """
        # NOTE: One interesting benchmark would be to just measure how much a
        # good initial assignment makes difference. First, if I assign randomly
        # here, does it make it any better or worse? Second, what's the amount
        # of iterations that compensates for the difference?
        #
        # EDIT: Just tried this:
        #
        # return [ "noun" for _ in xrange(n_words) ]
        #
        # The result is, even with just 500 samples it makes no difference. A
        # completely random or deliberately bad initial sample is perfectly
        # fine if we sample several hundred times.
        #
        # I didn't test for what's the lowest amount of samples for
        # compensating this though.
        #
        # Still using the old, unnecessarily fancy version here for no reason.
        return [ max_p(self.__calculate_tag_n(i).iteritems())[0] for i in xrange(n_words) ]

    def __mcmc(self, sentence, sample):
        """
        Use the Markov blanket rule to calculate next sample:

        P(S_n) = normalized( P(S_n | S_{n-1}) P(S_{n+1} | S_n) P(W_n | S_n) )
        """
        n_words = len(sentence)

        for word_pos, word in enumerate(sentence):
            # Initialize with P(S_n | S_{n-1})
            if word_pos != 0:
                ps = self.__next_tags[sample[word_pos - 1]].copy()
            else:
                ps = { tag: 1 for tag in self.__all_tags }

            # P(S{n+1} | S_n)
            if word_pos != n_words - 1:
                next_tag = sample[word_pos + 1]
                for current_tag, current_tag_p in ps.iteritems():
                    ps[current_tag] = current_tag_p * self.__next_tags[current_tag].get(next_tag, 0.0)

            # P(W_n | S_n)
            for current_tag, current_tag_p in ps.iteritems():
                ps[current_tag] = current_tag_p * self.__tag_words[current_tag].get(word, 0.0)

            # Finally, actually do the sampling. First, let's normalize the
            # probabilities just for convenience.
            total = 0.0
            # print "ps, before normalization", ps
            for p in ps.itervalues():
                total += p

            # TODO: Understand why is this happening
            if total != 0:
                alpha = 1.0 / total
                for tag, tag_p in ps.iteritems():
                    ps[tag] = tag_p * alpha

            # Roll a dice
            dice = random.random()

            # List of (tag, probability)
            lst = list(ps.iteritems())

            # Sample!
            choice = weighted_choice(lst)
            # print "choice:", choice

            sample[word_pos] = choice
            # print "New sample:", sample

        return sample

    def mcmc(self, sentence, sample_count):
        n_words = len(sentence)

        # Initial sample of unobserved variables S_0, ..., S_{n-1}
        S_inits = self.__init_sample(n_words)
        # print "Initial sample:", S_inits

        sample = S_inits
        for _ in xrange(SAMPLES):
            # print "Iteration:", i+1
            sample = self.__mcmc(sentence, sample)

        # Collect 'sample_count' samples.
        ret = []
        for _ in xrange(sample_count):
            sample = self.__mcmc(sentence, sample[:])
            ret.append(sample)

        return [ ret, [] ]

    def max_marginal(self, sentence):
        # In the mcmc part I figured 3k is a good number for samples. I'm using
        # same number here.
        n_words = len(sentence)
        sample  = self.__init_sample(n_words)
        samples = []

        for _ in xrange(SAMPLES):
            sample = self.__mcmc(sentence, sample[:])
            samples.append(sample)

        # We count tags on the fly, instead of generating tables of marginal
        # probabilities etc.
        tags  = []
        probs = []
        for word_idx in xrange(n_words):
            word_tags = [ sample[word_idx] for sample in samples ]
            counter = collections.Counter(word_tags)
            counter_normalized = normalize(list(counter.iteritems()))

            max_tag = max_p(counter.iteritems())[0]
            max_tag_prob = find_lst(counter_normalized, max_tag)

            tags.append(max_tag)
            probs.append(max_tag_prob)

        assert len(tags) == n_words

        return [ [ tags ], [ probs ] ]

    def __viterbi(self, sentence, t):
        observed = sentence[t]

        if t == 0:
            return [ ([tag], tag_prob * self.__tag_words[tag].get(observed, 0.0)) \
                     for (tag, tag_prob) in self.__first_tags.iteritems() ]
        else:
            (prev_path, prev_path_prob) = max_p(self.__viterbi(sentence, t - 1))

            ret = []

            last_tag = prev_path[-1]

            for next_tag in self.__all_tags:
                next_tag_prob = \
                        prev_path_prob * \
                        self.__next_tags[last_tag].get(next_tag, 0.0) * \
                        self.__tag_words[next_tag].get(observed, 0.0)

                next_tag_path = prev_path[:]
                next_tag_path.append(next_tag)
                ret.append((next_tag_path, next_tag_prob))

            return ret

    def viterbi(self, sentence):
        paths = self.__viterbi(sentence, len(sentence) - 1)
        return [ [ max_p(paths)[0] ] , [] ]

    def best(self, sentence):
        # Just tried, max marginal works the best.
        # Honestly I spent so much time with this assignment, I don't want to
        # spend any more time with experimenting with parameters etc. I'm just
        # using whatever is the best in what I have.
        return self.max_marginal(sentence)

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself.
    # It's supposed to return a list with two elements:
    #
    #  - The first element is a list of part-of-speech labelings of the sentence.
    #    Each of these is a list, one part of speech per word of the sentence.
    #    Most algorithms only return a single labeling per sentence, except for the
    #    mcmc sampler which is supposed to return 5.
    #
    #  - The second element is a list of probabilities, one per word. This is
    #    only needed for max_marginal() and is the marginal probabilities for each word.
    #
    def solve(self, algo, sentence):
        if algo == "Naive":
            return self.naive(sentence)
        elif algo == "Sampler":
            return self.mcmc(sentence, 5)
        elif algo == "Max marginal":
            return self.max_marginal(sentence)
        elif algo == "MAP":
            return self.viterbi(sentence)
        elif algo == "Best":
            return self.best(sentence)
        else:
            print "Unknown algo!"


################################################################################
# Some utilities

def max_p(ps):
    """
    Given an iterator of (key, probability),
    returns (the key with largest probability, probability).
    """
    max   = 0
    max_k = None

    for k, v in ps:
        if max_k == None or max < v:
            max_k = k
            max   = v

    return (max_k, max)

def normalize(ps):
    """
    Given an list of (key, probability), return a list of same keys with
    normalized probabilities.
    """
    # DON'T PASS ITERATORS! We need to iterate two times, in general it's not
    # possible to reset iterators.
    assert isinstance(ps, list)

    ret = []
    total = 0.0

    for _, v in ps:
        total += v

    alpha = 1.0 / total

    for k, v in ps:
        ret.append((k, v * alpha))

    return ret

def find_lst(ps, key):
    for k, v in ps:
        if k == key:
            return v
    return None

# From http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"
