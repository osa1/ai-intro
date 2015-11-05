import sys
import re

################################################################################
# NOTE [Our solution]
# ~~~~~~~~~~~~~~~~~~~
#
# This is really the most naive solution + a very simple optimization that gives
# us huge boost. In fact, this is currently so fast that it solves the problem
# without any constraints in 0.013s.
#
# Here's how it works, without the main optimization: It just recursively
# searches, starting from first unassigned city. After every assignment we copy
# the whole state(which is just a map from cities to assignments). We do some
# simple optimizations for fast assignment lookup(like memoizing hash() of
# cities).
#
# Copying is super fast so it's not worth optimizing(run profile.py to
# generate profiling data).
#
# We do constraint propagation: When assigning a frequency during the search, we
# check assigned neighbors. If a neighbor uses frequence A for example, we don't
# try A at all.
#
# This version solves the problems with some constraints in a couple of seconds
# but unconstrained case takes forever. However, we do one very simple
# optimization that gives us _huge_ boost. We start assigning frequencies with
# the state that constraints others the most. E.g. we start with state with most
# number of neighbors.
#
# This really solves the whole thing. Previously unconstrained case was taking
# forever. After this optimization we solve unconstrained case in 0.023s.
# (note that Python startup takes 0.010s)
#
# NOTE [Future improvements]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# There's one more improvement we could do. When we have more than one state
# with same number of neighbors, we could first assign the one with least number
# of possible alternative frequencies.
#
# But current solution already solves the worst case in 0.13s(excluding Python
# startup). So there's really no need for any further optimizations.
#
# NOTE [Recursive implementation is fine]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Why? Because we have 50 states. A depth-first search would go as deep as 50
# call frames, which is perfectly fine. No risk of stack overflow.
#
# Note that Python's default stack size is 1000 on most systems. So our
# implementation handles problems up to 1000 states without any stack overflows.
# Since problem statement doesn't specify anything about number of states, we
# don't bother maintaining a stack.
#
# NOTE [Profiling]
# ~~~~~~~~~~~~~~~~
#
# Here I list times needed to solve constraints-4.
#
# Commit    Time
# -----------------
# 965065d   2.60s
# 837434c   2.31s
# 52f6e70   0.45s
# 343c301   0.013s
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
        self.hash = hash(name)

    def add_neighbor(self, n):
        assert isinstance(n, City)
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
        # assert isinstance(other, City)
        if not isinstance(other, City):
            print "other is not City: " + str(type(other))
        return self.name == other.name

    def __neq__(self, other):
        # assert isinstance(other, City)
        return self.name != other.name

    def __hash__(self):
        return self.hash

def search(assignments, all_cities):
    for city in all_cities:
        if city not in assignments and not city.fixed_freq:
            asgns = generate_valid_assignments(assignments, city)
            if len(asgns) == 0:
                # We have a unassigned city, and we can't assign too! This is an
                # invalid state.
                # print "Can't do any more assignments. Need to assign " + str(city) + "."
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
                    # print "New assignment."
                    break

            return ret

    # All the cities were assigned.
    return assignments

def valid_assignment(assignments):
    for city, assignment in assignments.iteritems():
        for n in city.neighbors:
            if assignment == assignments.get(n):
                return False

    return True

def generate_valid_assignments(assignments, city):
    ret = set(ALL_FREQS)
    for n in city.neighbors:
        # print "neighbor: " + str(n)
        # print "type of neighbor: " + str(type(n))
        ret.discard(assignments.get(n))
    return ret

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
            city_obj.add_neighbor(neighbor_obj)

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
    """
    Read "adjacent-states" file and return a list of
    (city_name, list_of_neighbors) pairs.
    """
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

def compare_ns(c1, c2):
    return cmp(len(c1.neighbors), len(c2.neighbors))

def run(*argv):
    constraints_file = argv[0]
    constraints = read_constraints(constraints_file)
    cities = read_graph()
    graph = list(generate_graphs(cities, constraints))
    graph.sort(cmp=compare_ns, reverse=True)
    ret = search({}, graph)

    ############################################################################
    # Making sure the output is correct

    assert len(ret) == len(cities) - len(constraints)
    for c in ret.iterkeys():
        assert not c.fixed_freq

    assert valid_assignment(ret)

    ############################################################################

    for k, v in ret.iteritems():
        print k.name + ":\t" + v

if __name__ == "__main__":
    run(*sys.argv[1:])
