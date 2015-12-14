import itertools
import math
import random

from confusion_matrix import print_confusion_matrix

class Neuron:
    def __init__(self, add_bias=True):
        self.inputs  = []
        if add_bias:
            Edge(Bias(), self)
            # Thanks to my awful design
            # self.inputs.append(Edge(Bias(), self))

        self._outputs = []

        # We cache some numbers here
        self.output_cache = None
        self.inputs_cache = None
        self.error_cache = None

    def add_input_edge(self, input_edge):
        self.inputs.append(input_edge)

    def add_output_edge(self, output_edge):
        self._outputs.append(output_edge)

    def output(self):
        """ a_j in the book """
        # print "Neuron output"

        if self.output_cache is not None:
            # print self, "returning from cache"
            return self.output_cache

        self.inputs_cache = []

        sum = 0
        for input_edge in self.inputs:
            input = input_edge.from_.output()
            self.inputs_cache.append(input)
            sum += input * input_edge.w

        self.output_cache = sigmoid(sum)
        # print "node output:", self.output_cache, sum
        return self.output_cache

    def error(self, label):
        if self.error_cache is not None:
            return self.error_cache

        if self.output_cache is None:
            # Debugging
            print self.output_cache
            print self.inputs_cache
            print self.error_cache
            print self.inputs
            print self._outputs

            raise RuntimeError("u suck at programming - 1")

        if len(self._outputs) == 0:
            # Output node
            self.error_cache = label - self.output_cache
        else:
            self.error_cache = sum([ edge.w * edge.to.error(label) for edge in self._outputs ])

        return self.error_cache

    def update_weights(self, alpha):
        # print "updating weights"
        if self.output_cache is None or \
                self.inputs_cache is None or \
                self.error_cache is None:
            print "output cache:", self.output_cache
            print "inputs cache:", self.inputs_cache
            print "error cache:", self.error_cache
            raise RuntimeError("u suck at programming - 2", self.__class__.__name__)

        sigmoid_prime = self.output_cache * (1 - self.output_cache)
        for input_idx, input_edge in enumerate(self.inputs):
            diff = alpha * sigmoid_prime * self.error_cache * self.inputs_cache[input_idx]
            # print "update_weights diff:", diff
            input_edge.w += diff

        for out_edge in self._outputs:
            out_edge.to.update_weights(alpha)

    def clear_caches(self):
        if self.output_cache is not None:
            self.output_cache = None
            self.inputs_cache = None
            self.error_cache = None

            for in_edge in self.inputs:
                in_edge.from_.clear_caches()


class FixedOutputNeuron(Neuron):
    def __init__(self, output=None):
        Neuron.__init__(self, add_bias=False)
        self.__output = output

    def output(self):
        # print "FixedOutputNeuron output"
        return self.__output

    def set_output(self, output):
        self.__output = output

    def update_weights(self, alpha):
        pass


class Bias(FixedOutputNeuron):
    def __init__(self):
        FixedOutputNeuron.__init__(self, 1.0)

    # def update_weights(self, alpha):
    #     pass

    def output(self):
        # print "Bias output"
        return FixedOutputNeuron.output(self)


class Edge:
    def __init__(self, from_, to):
        assert isinstance(from_, Neuron)
        assert isinstance(to, Neuron)
        self.from_ = from_
        self.to = to
        self.w = random.uniform(0, 1)

        from_.add_output_edge(self)
        to.add_input_edge(self)


class NeuralNet:
    def __init__(self, inputs, hidden_nodes):
        # Initialize input layer
        self.fixed_input_nodes = []
        self.input_nodes = []

        for _ in xrange(inputs):
            input_neuron = Neuron()
            input = FixedOutputNeuron()
            Edge(input, input_neuron)

            # self.input_nodes.append(input_neuron)
            self.fixed_input_nodes.append(input)
            self.input_nodes.append(input_neuron)

        # Initialize hidden layer
        self.hidden_nodes = []
        for _ in xrange(hidden_nodes):
            hidden_neuron = Neuron()
            for input_neuron in self.input_nodes:
                Edge(input_neuron, hidden_neuron)
            self.hidden_nodes.append(hidden_neuron)

        self.output_node = Neuron()
        for hidden_neuron in self.hidden_nodes:
            Edge(hidden_neuron, self.output_node)

    def __str__(self):
        return "<NeuralNet - %d fixed input nodes, %d input nodes, %d hidden nodes>" \
                % (len(self.fixed_input_nodes), len(self.input_nodes), len(self.hidden_nodes))

    def set_inputs(self, inputs):
        assert len(inputs) == len(self.fixed_input_nodes)
        self.clear_caches()
        for (node, input) in itertools.izip(self.fixed_input_nodes, inputs):
            node.set_output(input)
        # import pdb; pdb.set_trace()

    def output(self, test_data):
        self.clear_caches()
        self.set_inputs(test_data)
        return self.output_node.output()

    def clear_caches(self):
        self.output_node.clear_caches()

    def update_weights(self, alpha):
        for input_node in self.input_nodes:
            input_node.update_weights(alpha)

    def propagate_error(self, label):
        for input_node in self.input_nodes:
            input_node.error(label)

    def weights(self):
        edges = set()
        stack = [self.output_node]

        while len(stack) != 0:
            node = stack.pop()
            for input_edge in node.inputs:
                edges.add(input_edge)
                stack.append(input_edge.from_)

        weights = []
        for edge in edges:
            weights.append(edge.w)

        return weights

    def train(self, train_set, iterations, alpha=0.9):
        for i in xrange(iterations):
            print "Iteration", (i + 1)
            for (iter, (input, label)) in enumerate(train_set):
                print "\rTraining img", iter,
                self.clear_caches()
                self.set_inputs(input)
                self.output_node.output()
                self.propagate_error(label)
                self.update_weights(alpha)
            # print "weights after training:", self.weights()
            print


################################################################################

def sigmoid(z):
    """Or Logistic(z) or whatever."""
    # print "sigmoid input:", z
    return 1.0 / (1.0 + math.exp(- z))
    # return math.tanh(z)

# This is currently not used, we cache the output in nodes and directly
# calculate this instead. (e.g. last_output * (1 - last_output))
def sigmoid_prime(z):
    """dsigmoid / dz"""
    return z * (1 - z)

################################################################################
# Entry

def run_nnet(train_data, test_data, param):
    net = NeuralNet(len(test_data[0].rgbs_merged), param)

    train_data_ = [ (img.rgbs_merged, img.orientation) for img in train_data ]

    print "Neural net: Training..."
    net.train(train_data_, 5)

    classified_0   = []
    classified_90  = []
    classified_180 = []
    classified_270 = []

    print "Neural net: Classification..."
    for test in test_data:
        ret = int(round(net.output(test.rgbs_merged)))

        ret_df = [(abs(0   - ret),   0),
                  (abs(90  - ret),  90),
                  (abs(180 - ret), 180),
                  (abs(270 - ret), 270)]

        ret = min(ret_df, key=lambda (x, _): x)[1]


        ret_str = "(" + str(ret == test.orientation) + ")"
        print test.name, "classified as", ret, ret_str

        if ret == 0:
            classified_0.append(test)
        elif ret == 90:
            classified_90.append(test)
        elif ret == 180:
            classified_180.append(test)
        elif ret == 270:
            classified_270.append(test)
        else:
            raise RuntimeError("Bug: nnet returned %s" % str(ret))

    f = open("nnet_output.txt", "w")
    print_confusion_matrix(f, classified_0, classified_90, classified_180, classified_270)
    f.close()
