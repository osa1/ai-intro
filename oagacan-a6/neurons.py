import itertools
import math
import random

class Neuron:
    def __init__(self, add_bias=True):
        self.inputs  = []
        if add_bias:
            self.inputs.append(Edge(Bias(), self))

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

            raise RuntimeError("u suck at programming")

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
            raise RuntimeError("u suck at programming")

        for input_idx, input_edge in enumerate(self.inputs):
            sigmoid_prime = self.output_cache * (1 - self.output_cache)
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
    def __init__(self, output):
        Neuron.__init__(self, add_bias=False)
        self.__output = output

    # def output(self):
    #     print "FixedOutputNeuron output"
    #     return self.__output

    def set_output(self, output):
        self.__output = output

    # def update_weights(self, alpha):
    #     pass


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
    def __init__(self, example_img):
        # Initialize input layer
        self.__fixed_input_nodes = []
        self.__input_nodes = []

        for rgb in example_img.rgbs_merged:
            input_neuron = Neuron()
            input = FixedOutputNeuron(rgb)
            Edge(input, input_neuron)

            # self.__input_nodes.append(input_neuron)
            self.__fixed_input_nodes.append(input)
            self.__input_nodes.append(input_neuron)

        # Initialize hidden layer
        self.__hidden_nodes = []
        for _ in example_img.rgbs_merged:
            hidden_neuron = Neuron()
            for input_neuron in self.__input_nodes:
                Edge(input_neuron, hidden_neuron)
            self.__hidden_nodes.append(hidden_neuron)

        self.__output_node = Neuron()
        for hidden_neuron in self.__hidden_nodes:
            Edge(hidden_neuron, self.__output_node)

    def set_inputs(self, inputs):
        assert len(inputs) == len(self.__fixed_input_nodes)
        for (node, input) in itertools.izip(self.__fixed_input_nodes, inputs):
            node.set_output(input)

    def output(self, img):
        self.clear_caches()
        self.set_inputs(img.rgbs_merged)
        return self.__output_node.output()

    def clear_caches(self):
        self.__output_node.clear_caches()

    def update_weights(self, alpha):
        for input_node in self.__fixed_input_nodes:
            input_node.update_weights(alpha)

    def propagate_error(self, label):
        for input_node in self.__fixed_input_nodes:
            input_node.error(label)

    def weights(self):
        edges = set()
        stack = [self.__output_node]

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
            print "iteration", (i + 1)
            for (img_i, img) in enumerate(train_set):
                print "\rtraining", img_i,
                self.clear_caches()
                self.set_inputs(img.rgbs_merged)
                self.__output_node.output()
                self.propagate_error(img.orientation)
                self.update_weights(alpha)
            print "weights after training:", self.weights()
            print


################################################################################

def sigmoid(z):
    """Or Logistic(z) or whatever."""
    # print "sigmoid input:", z
    return 1.0 / (1.0 + math.exp(- z))

# This is currently not used, we cache the output in nodes and directly
# calculate this instead. (e.g. last_output * (1 - last_output))
def sigmoid_prime(z):
    """dsigmoid / dz"""
    s = sigmoid(z)
    return s * (1 - s)
