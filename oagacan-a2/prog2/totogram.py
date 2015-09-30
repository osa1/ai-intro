import itertools

################################################################################
#
# Here I'm collecting all the NOTEs as per the request from previous
# assignment. In the code I'll refer to NOTEs listed here in relevant parts.
#
# I did some research on graph colorings and I believe this problem is named
# "Hamiltonian coloring", or at least "hamiltonian coloring" was the thing that
# looked most similar. In any case, all of the papers I found were
# incomprehensible, so I had no luck finding relevant algorithms online.
#
# One relevant concept is "detour distance", which basically means longest path
# from node A to B. If we have an edge from A to B named E, we do
# E.val = abs(A.val - B.val), and then we try to minimize maximum detour
# distance in our graph.
#
# NOTE [How I test it]
# ~~~~~~~~~~~~~~~~~~~~
#
# I'm not even sure if there's a P algorithm for testing for optimality of
# results, and I'm not going to spend time on this. Instead here I try to
# optimize search and test functions as much as possible. I run the search for
# 10 seconds, and record the best solution.
#
#

################################################################################

class Node:
    def __init__(self, value):
        self.value = value
        self.edge1 = None
        self.edge2 = None
        self.edge3 = None

    def edges(self):
        return filter(None, [self.edge1, self.edge2, self.edge3])

    def connect(self, other):
        if other in self.edges():
            return

        if not self.edge1:
            self.edge1 = other
        elif not self.edge2:
            self.edge2 = other
        elif not self.edge3:
            self.edge3 = other
        else:
            raise RuntimeError(
                    "Trying to connect to a full node. (node with value %d)" % self.value)

        other.connect(self)

    def rotate_right(self):
        edges = self.edges()
        if len(edges) == 1:
            return

        e1_value = edges[0].value
        e2_value = edges[1].value
        e3_value = edges[2].value
        self.edge1.value = e3_value
        self.edge2.value = e1_value
        self.edge3.value = e2_value

    def rotate_left(self):
        edges = self.edges()
        if len(edges) == 1:
            return

        e1_value = edges[0].value
        e2_value = edges[1].value
        e3_value = edges[2].value
        self.edge1.value = e2_value
        self.edge2.value = e3_value
        self.edge3.value = e1_value

    def swap(self, i1, i2):
        edges = self.edges()
        e1 = edges[i1]
        e2 = edges[i2]
        e1.value, e2.value = e2.value, e1.value

    def local_score(self):
        """Local score is the score 4 connected nodes. A node with just one
        edge doesn't have a local node, we only consider nodes with 3 edges.
        """
        # TODO: I should probably give those nodes a name.
        edges = self.edges()
        if len(edges) == 1:
            return 0

        ret = 0
        for edge in edges:
            ret = max(ret, abs(self.value - edge.value))
        return ret

    def score(self):
        "Score of the whole net."
        # Set is used to make sure we're visiting every 3-node once. Is this
        # too slow? Alternatively we can always mark stuff.
        explored = set()
        waitlist = [self]
        score    = 0

        while len(waitlist) != 0:
            node = waitlist.pop()
            if node not in explored:
                explored.add(node)
                for new_edge in node.edges():
                    waitlist.append(new_edge)
                score = max(score, node.local_score())

        return score

    def bfs_list(self):
        "Generate a list representation of graph, using breadth-first order."
        from collections import deque

        queue = deque([self])

        buf = []
        visiteds = set()
        while len(queue) != 0:
            n = queue.popleft()
            visiteds.add(n.value)
            buf.append(n.value)
            for edge in [n.edge1, n.edge2, n.edge3]:
                if edge and edge.value not in visiteds:
                    queue.append(edge)

        return buf

    def show_bfs(self):
        "Show the tree in breadth-first order."
        return ' '.join(map(str, self.bfs_list()))

    def __net_str(self, from_):
        def aux(indent, lines, single_edge):
            c = ' ' if single_edge else '|'
            ls = lines.split('\n')
            spaces = '\n' + "".join(itertools.repeat(c + '   ', indent))
            return spaces.join(ls)

        edges = [ edge for edge in self.edges() if edge != from_ ]

        if len(edges) == 0:
            return str(self.value)

        strs = [ aux(1, edge.__net_str(self), edge == edges[-1]) for edge in edges ]

        value_str = str(self.value)
        value_space = 4 - len(value_str)
        first_indent = "".join(itertools.repeat('-', value_space))

        buf = []

        for i in xrange(len(strs)):
            edge_str = strs[i]

            if i == 0:
                buf.append(value_str + first_indent + edge_str)
            elif i == len(strs) - 1:
                buf.append("\---" + edge_str)
            else:
                buf.append("|---" + edge_str)

        return '\n'.join(buf)

    def __str__(self):
        return self.__net_str(None)


################################################################################

def init_graph(k):
    assert k > 0
    if k == 1:
        return Node(1)

    val = 1

    (node_1, val) = init_graph_aux(k - 1, val)
    (node_2, val) = init_graph_aux(k - 1, val)
    (node_3, val) = init_graph_aux(k - 1, val)

    node = Node(val)

    node.connect(node_1)
    node.connect(node_2)
    node.connect(node_3)

    return node

def init_graph_aux(k, val):
    assert k > 0

    if k == 1:
        return (Node(val), val + 1)

    (node_1, val) = init_graph_aux(k - 1, val)
    (node_2, val) = init_graph_aux(k - 1, val)

    node = Node(val)

    node.connect(node_1)
    node.connect(node_2)

    return (node, val + 1)

def gen_lst(k):
    "Generate a list of ordered numbers for the tree with depth k."
    if k == 1:
        return [1]

    nodes = 3 * ((2 ** (k - 1)) - 1) + 1
    return range(1, nodes + 1)

def gen_graph(k, lst):
    if k == 1:
        return Node(lst.pop())

    node_1 = gen_graph_aux(k - 1, lst)
    node_2 = gen_graph_aux(k - 1, lst)
    node_3 = gen_graph_aux(k - 1, lst)

    node = Node(lst.pop())

    node.connect(node_1)
    node.connect(node_2)
    node.connect(node_3)

    return node

def gen_graph_aux(k, lst):
    if k == 1:
        return Node(lst.pop())

    node_1 = gen_graph_aux(k - 1, lst)
    node_2 = gen_graph_aux(k - 1, lst)

    node = Node(lst.pop())

    node.connect(node_1)
    node.connect(node_2)

    return node

def gen_random_graph(k):
    import random
    lst = gen_lst(k)
    random.shuffle(lst)
    return gen_graph(k, lst)

################################################################################

def check_invariants(node, print_net=False):
    """
    Does some sanity checking:

    1. Make sure every node has either 1 or 3 connections.
    2. Make sure that no two edges from same node connects to same node.
    3. Make sure that the node A is connected to is also connected to A.

    Expensive check, only for testing purposes.
    """
    visiteds = set()
    waitlist = [node]

    while len(waitlist) != 0:
        node = waitlist.pop()

        if node in visiteds:
            continue

        visiteds.add(node)

        edges = node.edges()
        for edge in edges:
            waitlist.append(edge)

        edges_n = len(edges)
        edges_set = set(edges)

        if edges_n != 1 and edges_n != 3:
            if print_net:
                print node
            raise RuntimeError(
                    "Invariant violation: Found a node with %d edges.\n\t(node with value %d)" \
                            % (edges_n, node.value))

        if len(edges_set) != len(edges):
            if print_net:
                print node
            raise RuntimeError(
                    "Invariant violation: " + \
                            "Found a node with multiple edges connected to same node.\n\t" + \
                            "(node with value %d)" % node.value)

        for edge in edges:
            if node not in edge.edges():
                if print_net:
                    print node
                raise RuntimeError(
                        "Invariant violation: Neighbor node is not connected to current node.\n\t" + \
                                "(current node: node with value %d," + \
                                " neighbor node: node with value %d)" % (node.value, edge.value))

################################################################################

def init_and_search():
    pass

################################################################################

if __name__ == "__main__":
    lst = gen_random_graph(3)
    print lst
    print lst.show_bfs()
