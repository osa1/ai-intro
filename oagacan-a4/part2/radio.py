import sys
import re

################################################################################
# NOTE [Our solution]
# ~~~~~~~~~~~~~~~~~~~
#
# Very simple search using backtracking. Here's how it works.
#
# For a given node, we look at it's neighbors and make a list of frequencies
# that we can use for this node. If none of the frequencies are available, then
# we need to backtrack. If we can't backtrack, than this configuration doesn't
# have solution.
#
# To backtrack, we pop from the backtrack list. A backtrack list is a list of
# (move_to_revert, alternatives_to_try) pairs. We revert the move, and then try
# other alternatives. If 'alternatives_to_try' is an empty list, then we keep
# backtracking until we find a point with alternatives to try.
#
# NOTE [Data representation]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# TODO
#
################################################################################

FREQ_A    = 'A'
FREQ_B    = 'B'
FREQ_C    = 'C'
FREQ_D    = 'D'
ALL_FREQS = [FREQ_A, FREQ_B, FREQ_C, FREQ_D]

class City:
    def __init__(self, name, fixed_freq=None):
        self.name = name
        self.neighbors = set()

        if fixed_freq != None:
            self.current_freq = fixed_freq
            self.fixed_freq = True
        else:
            self.current_freq = None
            self.fixed_freq = False

        # We haven't tried any assignments so far. This will be check when we
        # backtrack
        self.tried = set()

    def add_neighbor(self, n):
        return self.neighbors.add(n)

    def try_next(self):
        if self.fixed_freq:
            # Just backtrack further, can't assign a different frequency to this
            # city
            return None

        potential_freqs = set(ALL_FREQS)
        for n in self.neighbors:
            if n.current_freq != None:
                potential_freqs.discard(n.current_freq)

        potential_freqs = list(potential_freqs.difference(self.tried))
        for f in potential_freqs:
            self.tried.add(f)
            return f

        self.tried = set()

        # This means we need to backtrack further. Since we will consider this
        # city in a different configuration, we also reset the self.tried.
        return None

    def __eq__(self, other):
        return self.name == other.name

    def __neq__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return "<City " + self.name + " len(neighbors): " + str(len(self.neighbors)) + ">"

    def __repr__(self):
        return str(self)

# TODO: We may end up having more than one graph, make sure the implementation
# handles this case.

def search(cities):
    pass

def generate_graphs(adjs, constraints):
    all_cities = set()
    city_objs  = {}

    for (city, neighbors) in adjs.iteritems():
        fixed_freq = constraints.get(city)

        # if fixed_freq != None:
        #     print "Found a city with fixed freq"

        city_obj = City(city, fixed_freq)
        city_objs[city] = city_obj
        all_cities.add(city_obj)

    # Second pass, connect city objects
    for (city, neighbors) in adjs.iteritems():
        city_obj = city_objs[city]
        for n in neighbors:
            neighbor_obj = city_objs[n]
            city_obj.add_neighbor(n)

    # print "len(all_cities):", len(all_cities)
    # print "all_cities:", all_cities

    return all_cities


################################################################################

def read_constraints(constraints_file_path):
    constraints_file = open(constraints_file_path, "r")
    lines = constraints_file.readlines()
    constraints_file.close()

    constraints = {}
    for line in lines:
        parts = line.split()
        if len(parts) != 0:
            assert not constraints.has_key(parts[0])
            constraints[parts[0]] = parts[1]

    return constraints

def read_graph():
    graph = {}

    files = ["adjacent-states", "../adjacent-states"]
    f = None
    for file_ in files:
        try:
            f = open(file_, "r")
        except IOError:
            continue

    if f == None:
        raise RuntimeError("Can't find graph file. Are you sure one of", files, " exists?")

    lines = f.readlines()
    f.close()

    for line in lines:
        parts = line.split()
        state = parts[0]
        adjacencies = parts[1:]

        current_adjs = graph.get(state, [])
        current_adjs.extend(adjacencies)
        graph[state] = current_adjs

    return graph

################################################################################
# Entry point

if __name__ == "__main__":
    constraints_file = sys.argv[1]
    constraints = read_constraints(constraints_file)
    cities = read_graph()
    generate_graphs(cities, constraints)
