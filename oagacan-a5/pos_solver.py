################################################################################
# CS B551 Fall 2015, Assignment #5
#
# Omer Sinan Agacan (oagacan)
#
# (Based on skeleton code by D. Crandall)
#
################################################################################
# Report
#
################################################################################

import itertools
import math
import random

class Solver:

    def __init__(self):
        self.__first_tags = None
        self.__next_tags  = None
        self.__tag_words  = None

    def posterior(self, sentence, label):
        """
        Calculate the log of the posterior probability of a given sentence with
        a given part-of-speech labeling.
        """
        return 0

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
        self.__next_tags  = self.__calculate_next_tags(data)
        self.__tag_words  = self.__calculate_tag_words(data)

        # print "self.__first_tags:", self.__first_tags
        # print "self.__next_tags:", self.__next_tags
        # print "self.__tag_words:", self.__tag_words

    def __calculate_first_tags(self, data):
        # Note the tag of first word of every sentence. Then normalize the
        # probabilities.
        appears = {}
        total_tags = 0
        for (_, tags) in data:
            tag  = tags[0]
            appears[tag] = appears.get(tag, 0) + 1
            total_tags += 1

        # Normalize probabilities
        m = 1.0 / float(total_tags)

        for first_tag, first_tag_amt in appears.iteritems():
            appears[first_tag] = first_tag_amt * m

        ################################################
        # Debugging, make sure probabilities add up to 1
        total = 0.0
        for first_tag_amt in appears.itervalues():
            total += first_tag_amt
        assert round(total) == 1
        ################################################

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

        ################################################
        # Debugging, make sure probabilities add up to 1
        for next_tag in next_tags.itervalues():
            total = 0.0
            for t_amt in next_tag.itervalues():
                total += t_amt
            assert round(total) == 1.0
        ################################################

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

        ################################################
        # Debugging, make sure probabilities add up to 1
        for tag_table in tag_words.itervalues():
            total = 0.0
            for word_ct in tag_table.itervalues():
                total += word_ct
            assert round(total) == 1
        ################################################

        return tag_words

    # Functions for each algorithm.
    #
    def naive(self, sentence):
        return [ [ [ "noun" ] * len(sentence) ], [] ]

    def mcmc(self, sentence, sample_count):
        return [ [ [ "noun" ] * len(sentence) ] * sample_count, [] ]

    def best(self, sentence):
        return [ [ [ "noun" ] * len(sentence) ], [] ]

    def max_marginal(self, sentence):
        return [ [ [ "noun" ] * len(sentence) ], [[0] * len(sentence),] ]

    def viterbi(self, sentence):
        return [ [ [ "noun" ] * len(sentence) ], [] ]


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
