import itertools
import math
import random

################################################################################

class ImageData:
    def __init__(self, name, orientation, rgbs):
        self.name = name
        self.orientation = orientation
        self.rgbs = rgbs

    def __str__(self):
        return "ImageData<name: " + self.name + "\n" + \
               "          orientation: " + str(self.orientation) + "\n" + \
               "          rgbs: " + str(self.rgbs) + ">"

    def __repr__(self):
        return self.__str__()


def parse_img_file(file):
    f = open(file, 'r')

    ret = []

    for line in f.readlines():
        parts = line.split()
        name = parts[0]
        orient = int(parts[1])

        assert ((len(parts) - 2) % 3 == 0)

        rgbs = []

        for i in xrange(2, len(parts), 3):
            r = int(parts[i  ])
            g = int(parts[i+1])
            b = int(parts[i+2])

            rgbs.append((r, g, b))

        ret.append(ImageData(name, orient, rgbs))

    return ret

################################################################################
# K-nearest neighbor

def minkowski_dist(p, ds1, ds2):
    """Minkowski distance of given p for two ImageData."""
    for ((r1, g1, b1), (r2, g2, b2)) in itertools.izip(ds1.rgbs, ds2.rgbs):
        s = ( abs(r1 - r2) ** p ) + \
            ( abs(g1 - g2) ** p ) + \
            ( abs(b1 - b2) ** p )

    return s ** (1.0 / float(p))

def nn(k, train_data, img):
    """K-nearest-neighbors."""
    nns = []

    worst_idx = None
    worst_dist = None

    for train_img in train_data:
        # TODO: I think this distance function is basically useless for this
        # purpose. Do I need to do some pre-processing and generate features
        # etc?
        dist = minkowski_dist(1, train_img, img)

        if len(nns) < k:
            nns.append((train_img, dist))
            worst_idx = None
            worst_dist = None
        else:
            # Find neighbor with worst distance if necessary.
            if worst_idx == None:
                for (idx, (n, n_dist)) in enumerate(nns):
                    if n_dist > worst_dist:
                        worst_idx = idx
                        worst_dist = n_dist

            if worst_dist > dist:
                nns[worst_idx] = (train_img, dist)
                worst_idx = None
                worst_dist = None

    assert len(nns) == k

    votes_0 = 0
    votes_90 = 0
    votes_180 = 0
    votes_270 = 0

    for (n, _) in nns:
        if n.orientation == 0:
            votes_0 += 1
        elif n.orientation == 90:
            votes_90 += 1
        elif n.orientation == 180:
            votes_180 += 1
        elif n.orientation == 270:
            votes_270 += 1
        else:
            raise RuntimeError("Invalid orientation: " + str(n.orientation))

    # print "votes_0:", votes_0
    # print "votes_90:", votes_90
    # print "votes_180:", votes_180
    # print "votes_270:", votes_270

    return max([(votes_0, 0), (votes_90, 90), (votes_180, 180), (votes_270, 270)],
            key=lambda x: x[0])[1]

################################################################################
# Neural net

# I fix the threshold function for now. If time permits I can experiment with
# some different ones.

class InputNeuron:
    """
    InputNeuron is just a neuron with fixed input.
    """
    def __init__(self, inputs):
        # An input is a (value, weight) pair. Values never change, but weights
        # do as we learn. EDIT: This is not quite true, we use same net on
        # different images so the values change too. They just change in
        # different times.
        self.__inputs = inputs

    def set_inputs(self, new_inputs):
        """
        Set inputs of the neuron. Note that this doesn't change the weights.
        """
        assert len(new_inputs) == len(self.__inputs)
        for (idx, (new_input, (_, old_weight))) in \
                enumerate(itertools.zip(new_inputs, self.__inputs)):
            self.__inputs[idx] = (new_input, old_weight)

    def output(self):
        return sigmoid(sum([ i * w for (i, w) in self.__inputs ]))


class HiddenNeuron:
    """
    HiddenNeuron is just a neuron that gets it's input from another neuron.
    The inputs are read via input nodes' output() methods.

    NOTE: This is also used in output layer.
    """
    def __init__(self, inputs=None):
        # An input is a (source, weight) pair. Sources should have a output()
        # method.
        if not inputs:
            self.__inputs = []
        else:
            self.__inputs = inputs

    def add_input(self, input, weight):
        self.__inputs.append((input, weight))

    def output(self):
        return sigmoid(sum([ i.output() * w for (i, w) in self.__inputs ]))


class NeuralNet:
    def __init__(self, input_layer, hidden_layer, output_layer):
        self.__input_layer = input_layer
        self.__hidden_layer = hidden_layer
        self.__output_layer = output_layer

    def set_inputs(self, inputs):
        assert len(inputs) == len(self.__input_layer)
        self.__input_layer.set_inputs(inputs)

    def output(self):
        return self.__output_layer.output()

    def __str__(self):
        return ("<NeuralNet with %d input layer neurons, " + \
                "%d hidden layer neurons and 1 output neuron>") \
               % (len(self.__input_layer), len(self.__hidden_layer))


def sigmoid(z):
    """Or Logistic(z) or whatever."""
    return 1.0 / (1 + math.e ** (- z))

def init_net(test_img):
    # Initialize input layer
    input_nodes = []

    for (r, g, b) in test_img.rgbs:
        w1 = init_weight()
        w2 = init_weight()
        w3 = init_weight()
        input_nodes.append(InputNeuron([ (r, w1), (g, w2), (b, w3) ]))

    hidden_nodes = []

    # Now slower with more bugs!

    for _ in test_img.rgbs:
        inputs = [ (i, init_weight()) for i in input_nodes ]
        hidden_nodes.append(HiddenNeuron(inputs))

    output_node_inputs = [ (i, init_weight()) for i in input_nodes ]
    output_node = HiddenNeuron(output_node_inputs)

    print "Total input nodes:", len(input_nodes)
    print "Total hidden nodes:", len(hidden_nodes)

    return NeuralNet(input_nodes, hidden_nodes, output_node)

def init_weight():
    # Don't ask why
    return random.random() * 8 - 4


################################################################################
# Entry

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="assignment 6")
    parser.add_argument("training_file")
    parser.add_argument("test_file")
    parser.add_argument("mode", choices=["knn", "nnet"])
    parser.add_argument("knn/nnet_param", type=int)

    args = vars(parser.parse_args())

    train_data = parse_img_file(args["training_file"])
    print "example distance:", minkowski_dist(1, train_data[0], train_data[1])

    test_data = parse_img_file(args["test_file"])

    # for test in test_data:
    #     ret = nn(10, train_data, test)
    #     result = "(True)" if ret == test.orientation else "(False)"
    #     print "nn:", ret, result
    print "Initializing neural network."
    net = init_net(test_data[0])
    print net
    print net.output()
    print "Done."
