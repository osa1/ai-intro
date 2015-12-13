################################################################################
# This is my first attempt, which failed miserably. The structure is hard to
# work with, and I forgot to add biases. The back-propagation algorithms follows
# the definition in Figure 18.24. Ridiculously inefficient.
################################################################################

import math
import itertools
import random

# Adding this awful global state for now.
ALPHA = 0.00002

# I fix the threshold function for now. If time permits I can experiment with
# some different ones.

class InputNeuron:
    """
    InputNeuron is just a neuron with single, fixed input.
    """
    def __init__(self, input, input_w):
        self.input = input
        self.input_w = input_w

        self.outputs = []

    def set_input(self, new_input):
        self.input = new_input

    def add_output(self, output_node, output_w):
        self.outputs.append((output_node, output_w))

    def in_(self):
        """ in_j """
        return self.input * self.input_w

    def output(self):
        """ a_j """
        return sigmoid(self.in_())

    def output_prime(self):
        """ a_j' """
        return sigmoid_prime(self.in_())


class HiddenNeuron:
    """
    HiddenNeuron is just a neuron that gets it's inputs from other neurons.
    The inputs are read via input nodes' output() and output_prime() methods.

    NOTE: This is also used in output layer.
    """
    def __init__(self, inputs=None):
        # An input is a (source, weight) pair. Sources should have output() and
        # output_prime() methods.
        if not inputs:
            self.inputs = []
        else:
            self.inputs = inputs

        self.outputs = []

    def add_input(self, input_node, input_w):
        self.inputs.append((input_node, input_w))

    def add_output(self, output_node, output_w):
        self.outputs.append((output_node, output_w))

    def in_(self):
        """ in_j """
        return sum([ i.output() * w for (i, w) in self.inputs ])

    def output(self):
        """ a_j """
        return sigmoid(self.in_())

    def output_prime(self):
        """ a_j' """
        return sigmoid_prime(self.in_())


class NeuralNet:
    def __init__(self, input_layer, hidden_layer, output_layer):
        self.input_layer = input_layer
        self.hidden_layer = hidden_layer
        self.output_layer = output_layer

    def set_inputs(self, inputs):
        # THIS DOESN'T and SHOULDN'T CHANGE WEIGHTS !!1
        assert len(inputs) == len(self.input_layer)
        for (node, input) in itertools.izip(self.input_layer, inputs):
            node.set_input(input)

    def connect_img(self, img):
        assert len(self.input_layer) == len(img.rgbs)
        for (input_node, rgb) in itertools.zip(self.input_layer, img.rgbs_merged):
            input_node.set_input(rgb)

    def output(self):
        return self.output_layer.output()

    def __str__(self):
        return ("<NeuralNet with %d input layer neurons, " + \
                "%d hidden layer neurons and 1 output neuron>") \
               % (len(self.input_layer), len(self.hidden_layer))


def sigmoid(z):
    """Or Logistic(z) or whatever."""
    # print "sigmoid input:", z
    return 1.0 / (1 + math.exp(- z))

def sigmoid_prime(z):
    """dsigmoid / dz"""
    s = sigmoid(z)
    return s * (1 - s)

def init_net(test_img):
    # Initialize input layer
    input_nodes = []

    for rgb in test_img.rgbs_merged:
        w = init_weight()
        input_nodes.append(InputNeuron(rgb, w))

    # Initialize hidden layer
    hidden_nodes = []

    # Now slower with more bugs!

    for _ in test_img.rgbs:
        hn = HiddenNeuron()

        for i in input_nodes:
            w = init_weight()
            hn.add_input(i, w)
            i.add_output(hn, w)

        hidden_nodes.append(hn)

    # Initialize output layer (we have only one node in output layer)

    output_node = HiddenNeuron()
    for i in hidden_nodes:
        w = init_weight()
        output_node.add_input(i, w)
        i.add_output(output_node, w)

    print "Total input nodes:", len(input_nodes)
    print "Total hidden nodes:", len(hidden_nodes)

    return NeuralNet(input_nodes, hidden_nodes, output_node)

def init_weight():
    # Don't ask why
    # return random.random() * 8 - 4
    # return random.random() - 0.5
    return (random.random() - 0.5) / 1000000.0

def back_prop_learning(net, training_set):
    # FIXME: This implementation is really inefficient: We keep calculating same
    # numbers, there's a lot of room for refactoring(maybe memoization).

    for (img_idx, img) in enumerate(training_set):

        print "\rProcessing img", img_idx,

        inputs = img.rgbs_merged
        # print "setting inputs:", inputs
        net.set_inputs(inputs)

        net_output = net.output()
        # print "net output:", net_output
        expected_output = float(img.orientation)

        # One output -> one delta
        output_delta = net.output_layer.output_prime() * (expected_output - net_output)

        hidden_layer_deltas = []
        for n in net.hidden_layer:
            # We know every hidden layer node has exactly one output, so I'm
            # writing this slightly simplified version
            hidden_layer_deltas.append(n.output_prime() * n.outputs[0][1] * output_delta)

        input_layer_deltas = []
        for n in net.input_layer:
            s = 0
            for hidden_n_idx in xrange(len(net.hidden_layer)):
                # WARNING: We require input node's outputs are ordered the same
                # as net's hidden layer. Awful code.
                d = hidden_layer_deltas[hidden_n_idx]
                w = n.outputs[hidden_n_idx][1]
                s += d * w
            input_layer_deltas.append(n.output_prime() * s)

        #############################################
        # Update every weight in network using deltas

        # Input layer
        for (n_idx, n) in enumerate(net.input_layer):
            n.input_w += ALPHA * n.input * input_layer_deltas[n_idx]
            # Resetting output list to be able to add outputs with new weights
            # below
            n.outputs = []

        # Hidden layer
        for (hn_idx, hn) in enumerate(net.hidden_layer):
            for (hn_input, hn_input_w) in hn.inputs:
                hn_input_w += ALPHA * hn_input.output() * hidden_layer_deltas[hn_idx]
                hn_input.outputs.append((hn, hn_input_w))

            # Similarly reset output list here to be able to add correct output
            # with updated weight below
            hn.outputs = []

        # Output layer
        for (output_input, output_input_w) in net.output_layer.inputs:
            output_input_w += ALPHA * output_input.output() * output_delta
            output_input.outputs.append((net.output_layer, output_input_w))

    print

def classify(net, test_data):
    for (img_idx, img) in enumerate(test_data):
        print "Classifying img", img_idx
        net.set_inputs(img.rgbs_merged)
        print "output:", net.output(),
