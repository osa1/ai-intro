import re
import time
from collections import deque

# A city is a (name : String, latitude : Float, longitude : Float) triplet.
# Example: ("Bloomington,_Indiana", 39.165325, -86.5263857)
def parse_city_gps(f):
    """Parse city gps file from given file object."""
    ret = []
    # This one parses to four groups, (city, state, latitude, longitude).
    # pattern = re.compile(
    #         r"\s*([^,]+),([^,\s]+) (-{0,1}\d+\.{0,1}\d*) (-{0,1}\d+\.{0,1}\d*)\s*")
    pattern = re.compile(
            r"^\s*([^\s]+) (-{0,1}\d+\.{0,1}\d*) (-{0,1}\d+\.{0,1}\d*)\s*$")

    for line in f:
        ms = re.match(pattern, line)

        if not ms:
            raise RuntimeError("Can't parse city line:\n" + line)

        ret.append((ms.group(1), float(ms.group(2)), float(ms.group(3))))

    return ret

# A road is (from : String, to : String, distance : Int, max_speed : Int,
# road_name : String) tuple.
def parse_roads(f):
    ret = []
    pattern = re.compile(
            r"^\s*([^\s]+) ([^\s]+) (\d+) (\d+) ([^\s]+)\s*$")

    cant_parse = []

    for line in f:
        ms = re.match(pattern, line)

        if not ms:
            cant_parse.append(line)
        else:
            ret.append((ms.group(1), ms.group(2),
                int(ms.group(3)), int(ms.group(4)), ms.group(5)))

    ### NOTE [Filling missing information]
    #
    # We have some roads with missing distance or max speeds, here how we fill
    # those missing info:
    #
    # First, we assume that missing info is actually max speed and not
    # distance, becuase when we look at the malformed lines, e.g.
    #
    #   Antigonish,_Nova_Scotia Tracadie,_Nova_Scotia 30  NS_104
    #
    # We see that there's extra space between the number and road name. This
    # suggests that the speed was not printed, but the space after it was
    # printed. The extra space would be between the destination and the number
    # if it was the other way around. e.g. something like:
    #
    #   Antigonish,_Nova_Scotia Tracadie,_Nova_Scotia  30 NS_104
    #
    # Then, we take arithmetic mean of all the speeds we read from the file,
    # and use that as speeds of missing lines.
    #
    # The advantage of this method is that it doesn't have any effect on the
    # algorithms, it doesn't make anything more complex. Hopefully it's not too
    # inaccurate either.

    missing_info_pattern = re.compile(
            r"^\s*([^\s]+) ([^\s]+)\s+(\d+)\s+([^\s]+)\s*$")

    average_speed = sum(map(lambda x: x[3], ret)) / len(ret)
    # print "average_speed: ", average_speed

    for line in cant_parse:
        # print "trying to parse: " + line
        ms = re.match(missing_info_pattern, line)
        ret.append((ms.group(1), ms.group(2),
            int(ms.group(3)), average_speed, ms.group(4)))

    return ret

##
##
##

class Visited:
    def __init__(self, what, path, cost):
        self.what = what
        self.path = path
        self.cost = cost

    def __str__(self):
        return "<Visited: " + self.what + \
                "path: " + str(self.path) + \
                " cost: " + str(self.cost) + ">"

##
## We took advantage of duck typing and create stack and queue implementations
## that share the same interface. This is used to implement BFS and DFS without
## duplicating code.
##

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0

class Queue:
    def __init__(self):
        self.queue = deque()

    def push(self, item):
        self.queue.append(item)

    def pop(self):
        return self.queue.popleft()

    def empty(self):
        return len(self.queue) == 0

##
##
##

class Map:
    def __init__(self, cities, roads):
        self.city_map = {}
        for city in cities:
            existing_city = self.city_map.get(city[0])
            if existing_city and not existing_city == city[1:]:
                raise RuntimeError(
                        "City already exists in the database, with different lat/long.\n" + \
                        "Existing entry: " + str(existing_city) + "\n" + \
                        "New entry: " + str(city))
            else:
                self.city_map[city[0]] = (city[1], city[2])

        self.road_map = {}
        for (k, v) in self.city_map.iteritems():
            self.road_map[k] = []
            self.road_map[v[0]] = []

        for road in roads:
            # TODO: Maybe we need a Road class.
            from_ = road[0]
            to    = road[1]
            dist  = road[2]
            speed = road[3]
            name  = road[4]

            if self.road_map.has_key(from_):
                self.road_map[from_].append((to, dist, speed, name))
            else:
                # This happens in two cases:
                #
                # - As noted in the assignment text, we have road intersection
                #   points that are not listed in GPS file.
                #
                # - I also realized that there are some cities(not road
                #   intersections) that are not listed in GPS.
                #   (like Acton-Vale,_Quebec)
                #
                # I don't know how to handle those roads in search algorithms
                # yet, but here we just add them to the database, using None
                # for unknown information.

                # raise RuntimeError("Found a road from nowhere: " + from_)
                # print("WARNING: Found a road from nowhere: " + from_)
                self.city_map[from_] = (None, None)
                self.road_map[from_] = [(to, dist, speed, name)]

            # Roads are non-directed, so do the same from to to from_
            if self.road_map.has_key(to):
                self.road_map[to].append((from_, dist, speed, name))
            else:
                self.city_map[to] = (None, None)
                self.road_map[to] = [(from_, dist, speed, name)]

    def __str__(self):
        return "<Map with " + str(len(self.city_map)) + \
               " cities and " + str(self.__len_roads()) + " roads>"

    def __len_roads(self):
        ret = 0
        for (_, v) in self.road_map.iteritems():
            ret += len(v)
        return ret

    def outgoing(self, city):
        return self.road_map.get(city)

    def uninformed_search(self, start_city, end_city, frontier_cls, timeit=False):
        assert start_city in self.city_map
        assert end_city in self.city_map

        if timeit:
            begin = time.clock()

        visiteds = {}
        frontier = frontier_cls()
        frontier.push(Visited(start_city, [], 0))

        while not frontier.empty():
            current = frontier.pop()
            # print "current:", current.what

            visiteds[current.what] = current

            if current.what == end_city:
                if timeit:
                    end = time.clock()
                    print("Search took " + str(end - begin) + " seconds.")

                return current

            for outgoing_road in self.outgoing(current.what):
                # print "adding outgoing road:", str(outgoing_road)
                next_city = outgoing_road[0]
                next_city_cost = current.cost + 1

                next_city_visited = visiteds.get(next_city)
                if next_city_visited:
                    if next_city_visited.cost <= next_city_cost:
                        continue

                new_path = current.path[:]
                new_path.append(next_city)

                frontier.push(Visited(next_city, new_path, next_city_cost))

        if timeit:
            end = time.clock()
            print("Search took " + str(end - begin) + " seconds.")

    def bfs(self, start_city, end_city, timeit=False):
        """Runs an uninformed breadth-first search, from start_city to
        end_city. Since the search is uninformed, we don't care about route
        options here."""
        return self.uninformed_search(start_city, end_city, Queue, timeit=timeit)

    def dfs(self, start_city, end_city, timeit=False):
        """Runs an uninformed depth-first search, from start_city to end_city.
        Since the search is uninformed, we don't care about route options
        here."""
        return self.uninformed_search(start_city, end_city, Stack, timeit=timeit)

    def astar(self, start_city, end_city, heuristic, timeit=False):
        assert start_city in self.city_map
        assert end_city in self.city_map

        # I'd prefer a heap class with it's own methods...
        from heapq import heappush, heappop

        pq = [(0, Visited(start_city, [], 0))]

        visiteds = {}

        while len(pq) != 0:
            current = heappop(pq)[1]

            visiteds[current.what] = current

            if current.what == end_city:
                return current

            for outgoing_road in self.outgoing(current.what):
                next_city = outgoing_road[0]
                next_city_cost = current.cost + outgoing_road[2]

                next_city_visited = visiteds.get(next_city)
                if next_city_visited:
                    if next_city_visited.cost <= next_city_cost:
                        continue

                new_path = current.path[:]
                new_path.append(next_city)

                next_city_obj = self.city_map[next_city]

                f = current.cost + heuristic(end_city, next_city, next_city_obj)
                heappush(pq, (f, Visited(next_city, new_path, next_city_cost)))


def heuristic_constant(target, next, (next_lat, next_long)):
    """A heuristic that assigns same cost to every node(except the target,
    which is assigned 0). Effectively this makes A* same as BFS."""
    if target == next:
        return 0
    return 1


##
## Utilities
##

def try_open(paths):
    for path in paths:
        try:
            f = open(path, "r")
        except IOError:
            continue
        return f

def distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two latitude, longitude points using
    Haversine formula. Returns in kilometers.

    http://www.movable-type.co.uk/scripts/latlong.html
    """
    import math

    r = 6371000 # metres

    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) * math.sin(d_phi / 2) + \
        math.cos(phi_1) * math.cos(phi_2) * \
        math.sin(d_lam/2) * math.sin(d_lam / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = r * c
    return d

def to_miles(km):
    return km * 0.621371

def distance_miles(lat1, lon1, lat2, lon2):
    """Like 'distance', but returns in miles."""
    # Instead of modifying a code that I don't understand(distance function,
    # implemented from the tutorial linked in the function docs), I prefer
    # getting the answer from it and converting it to the format I like here.
    return to_miles(distance(lat1, lon1, lat2, lon2))

##
## Entry
##

if __name__ == "__main__":
    # In my dev env. text files are in parent directory, but assuming
    # instructors may be running it from top-level, we're checking parent
    # directory and current directory for files here.
    gps_file = try_open(["city-gps.txt", "../city-gps.txt"])
    if not gps_file:
        print "Can't find city-gps.txt in current directory or parent directory."
        exit(1)

    try:
        cities = parse_city_gps(gps_file)
    except RuntimeError as e:
        print "Can't parse cities. Error:"
        print e
    finally:
        gps_file.close()

    for city in cities:
        print city

    road_file = try_open(["road-segments.txt", "../road-segments.txt"])
    if not road_file:
        print "Can't find road-segments.txt in current directory or parent directory."
        exit(1)

    try:
        roads = parse_roads(road_file)
    except RuntimeError as e:
        print "Can't parse roads. Error:"
        print e
    finally:
        road_file.close()

    for road in roads:
        print road

    city1 = cities[0]
    city2 = cities[1]
    print "==="
    print city1
    print city2

    print(distance_miles(city1[1], city1[2], city2[1], city2[2]))
    m = Map(cities, roads)
    print str(m)
    # print m.outgoing("Ada,_Oklahoma")
    print(m.bfs("Ada,_Oklahoma", "Albany,_California"), timeit=True)
    print(m.astar("Ada,_Oklahoma", "Albany,_California", heuristic_constant, timeit=True))
    print(m.dfs("Ada,_Oklahoma", "Albany,_California", timeit=True))
