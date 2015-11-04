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
        self.fixed_freq = fixed_freq

    def add_neighbor(self, n):
        return self.neighbors.add(n)

    def __str__(self):
        if self.fixed_freq == None:
            fixed_freq_str = "Nope"
        else:
            fixed_freq_str = "Yes: " + str(self.fixed_freq)

        return "<City " + self.name + \
                " len(neighbors): " + str(len(self.neighbors)) + \
                " fixed_freq: " + fixed_freq_str + \
                ">"

    def __repr__(self):
        return str(self)

    ############################################################################
    # Essentially we treat every city as a singleton. This is probably not a
    # good practice but works fine for this assignment.

    def __eq__(self, other):
        return self.name == other.name

    def __neq__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

# TODO: We may end up having more than one graph, make sure the implementation
# handles this case.

def search(assignments, all_cities):
    if not valid_assignment(assignments):
        # I'm not sure if this can happen, because we only do valid assignments.
        # (i.e. generate_valid_assignments() should only generate _valid_
        # assignments, in which case this should not happen)
        # TODO: Removing this should be fine if the algorithm is correct.
        return None

    for city in all_cities:
        if city not in assignments:
            asgns = generate_valid_assignments(assignments, city)
            if len(asgns) == 0:
                # We have a unassigned city, and we can't assign too! This is an
                # invalid state.
                return None

            # We have to assign something in this loop.
            ret = None
            for asgn in asgns:
                # We're going to try all the alternatives
                new_assignments = assignments.copy()
                new_assignments[city] = asgn
                ret = search(new_assignments, all_cities)
                if ret:
                    # There may be other solutions, but no need to search
                    # further.
                    break

            return ret

    # All the cities were assigned. First condition already checked that the
    # assginments were valid. (TODO: Hm, maybe the first condition is necessary?
    # Check this again when sober)
    return assignments


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
    graph = generate_graphs(cities, constraints)
    ret = search({}, graph)
    print ret
