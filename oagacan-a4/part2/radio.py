import sys
import re

def run(constraints_file_path):
    constraints_file = open(constraints_file_path, "r")
    lines = constraints_file.readlines()
    constraints_file.close()

    constraints = {}
    for line in lines:
        parts = line.split()
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

if __name__ == "__main__":
    constraints_file = sys.argv[1]
    print(run(constraints_file))
    print(read_graph())
