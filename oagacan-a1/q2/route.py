import re
import time
from collections import deque

################################################################################
## Parsers

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

        ret.append(City(ms.group(1), float(ms.group(2)), float(ms.group(3))))

    return ret

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
            ret.append(Road(ms.group(1), ms.group(2),
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

    average_speed = sum(map(lambda x: x.max_speed, ret)) / len(ret)
    # print "average_speed: ", average_speed

    for line in cant_parse:
        # print "trying to parse: " + line
        ms = re.match(missing_info_pattern, line)
        ret.append(Road(ms.group(1), ms.group(2),
            int(ms.group(3)), average_speed, ms.group(4)))

    return ret

def parse_map():
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

    return Map(cities, roads)

################################################################################
## Some intermediate data structures

class Visited:
    def __init__(self, what, path, cost):
        self.what = what
        self.path = path

        # NOTE: This is total cost up to this point, not the cost of moving to
        # this point from previous point.
        self.cost = cost

    def __str__(self):
        return "<Visited: " + self.what + \
                " path: " + str(self.path) + \
                " cost: " + str(self.cost) + ">"

    def __repr__(self):
        return self.__str__()


# We took advantage of duck typing and create stack and queue implementations
# that share the same interface. This is used to implement BFS and DFS without
# duplicating code.

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


class Road:
    def __init__(self, from_, to, distance, max_speed, name):
        self.from_ = from_
        self.to = to
        self.distance = distance
        self.max_speed = max_speed
        self.name = name

    def invert(self):
        return Road(self.to, self.from_, self.distance, self.max_speed, self.name)

    def __str__(self):
        return "<Road " + self.name + " from: " + self.from_ + \
                " to: " + self.to + " distance: " + str(self.distance) + \
                " speed limit: " + str(self.max_speed) + ">"

    def __repr__(self):
        return self.__str__()


class City:
    def __init__(self, name, lat, long):
        self.name = name
        self.lat = lat
        self.long = long

    def __eq__(self, other):
        return self.name == other.name and \
                self.lat == other.lat and \
                self.long == other.long

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<City " + self.name + " latitude: " + str(self.lat) + \
                " longitude: " + str(self.long) + ">"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.name)


################################################################################
## Main class, implements search algorithms

# TODO: Remove maps by actually linking cities together, using roads.

class Map:
    def __init__(self, cities, roads):
        self.city_map = {}
        for city in cities:
            existing_city = self.city_map.get(city.name)
            if existing_city and existing_city != city:
                raise RuntimeError(
                        "City already exists in the database, with different lat/long.\n" + \
                        "Existing entry: " + str(existing_city) + "\n" + \
                        "New entry: " + str(city))
            else:
                self.city_map[city.name] = city

        self.road_map = {}
        for city in cities:
            self.road_map[city.name] = []

        for road in roads:
            # TODO: Maybe we need a Road class.
            from_ = road.from_
            to = road.to

            if self.road_map.has_key(from_):
                self.road_map[from_].append(road)
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
                self.city_map[from_] = City(from_, None, None)
                self.road_map[from_] = [road]

            # Roads are non-directed, so do the same from to to from_
            if self.road_map.has_key(to):
                self.road_map[to].append(road.invert())
            else:
                self.city_map[to] = City(to, None, None)
                self.road_map[to] = [road.invert()]

    def __str__(self):
        return "<Map with " + str(len(self.city_map)) + \
               " cities and " + str(self.__len_roads()) + " roads>"

    def __len_roads(self):
        ret = 0
        for (_, v) in self.road_map.iteritems():
            ret += len(v)
        return ret / 2 # divide by 2 because we duplicate roads for bi-directionality.

    def __neighbors(self, city):
        return { self.city_map[r.to] for r in self.road_map[city.name] }

    def __try_fill_missing_gps(self, city):
        ns = self.__neighbors(city)
        points = []

        for n in ns:
            if n.lat and n.long:
                points.append((n.lat, n.long))

        if len(points) == 0:
            return False
        if len(points) == 1:
            # This is not ideal, but I can't see anything better to do right
            # now. Make the location same as it's only neighbor.
            city.lat = points[0][0]
            city.long = points[0][1]
            return True
        else:
            # print "Calculating middle point of", len(points), "points."
            (lat, long) = middle_point(points)

            city.lat = lat
            city.long = long

            return True

    def fill_missing_gps(self):
        """Generate GPS positions for cities with missing GPS positions. We
        generate locations by looking at neighbors(e.g. cities with a road to
        this city with missing info) and generating GPS coordinates of middle
        point of all neighbor cities.

        Since most of the cities with missing information are actually
        intersection points of roads(instead of actual cities), they should
        have at least two neighbors.

        (We have yet to see a city with missing info and one/zero neighbors, so
        we don't handle that case)
        """
        # TODO: It's weird that missing speed info is filled by parser, while
        # GPS is filled by State here. Parser should generate a None if speed
        # info is missing and we should handle it here similarly.

        # print some stats, for testing
        missing = 0
        not_missing = 0
        for _, city in self.city_map.iteritems():
            if not (city.lat and city.long):
                # print "found city with missing info: " + str(city)
                missing += 1
            else:
                not_missing += 1
        # print "Missing:", missing, "not missing:", not_missing
        # Ouch! "Missing: 1052 not missing: 5477"

        resolveds   = []
        unresolveds = []

        for _, city in self.city_map.iteritems():
            if city.lat and city.long:
                resolveds.append(city)
            else:
                if self.__try_fill_missing_gps(city):
                    resolveds.append(city)
                else:
                    unresolveds.append(city)

        # print str(len(resolveds)), "resolved cities."
        # print str(len(unresolveds)), "unresolved cities."

        # We run a very simple quadratic algorithm here. We loop until we
        # resolve all the unresolved cases, as long as we make progress(e.g.
        # solve at least one unresolved case) at each iteration.
        #
        # Apparently Quebec is an unknown place on earth.
        made_progress = True
        idx = len(unresolveds) - 1
        while made_progress:
            made_progress = False
            l = len(unresolveds)
            unresolveds = [ u for u in unresolveds if not self.__try_fill_missing_gps(u) ]
            if l != len(unresolveds):
                made_progress = True

        assert len(unresolveds) == 0

    def outgoing(self, city):
        return self.road_map.get(city)

    def uninformed_search(self, start_city, end_city, frontier_cls, timeit=False):
        if start_city not in self.city_map:
            raise RuntimeError('Unknown city "' + start_city + '", aborting.')

        if end_city not in self.city_map:
            raise RuntimeError('Unknown city "' + end_city + '", aborting.')

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
                next_city = outgoing_road.to

                if visiteds.has_key(next_city):
                    continue

                new_path = current.path[:]
                new_path.append((next_city, outgoing_road))

                frontier.push(Visited(next_city, new_path, 0))

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

    def astar(self, start_city, end_city, heuristic, cost_fn, timeit=False):
        if start_city not in self.city_map:
            raise RuntimeError('Unknown city "' + start_city + '", aborting.')

        end_city_obj = self.city_map.get(end_city)
        if not end_city_obj:
            raise RuntimeError('Unknown city "' + end_city + '", aborting.')

        # I'd prefer a heap class with it's own methods...
        from heapq import heappush, heappop

        if timeit:
            begin = time.clock()

        pq = [(0, Visited(start_city, [], 0))]

        visiteds = {}

        while len(pq) != 0:
            current = heappop(pq)[1]

            visiteds[current.what] = current

            if current.what == end_city:
                if timeit:
                    end = time.clock()
                    print("Search took " + str(end - begin) + " seconds.")

                return current

            for outgoing_road in self.outgoing(current.what):
                next_city = outgoing_road.to
                next_city_obj = self.city_map[next_city]

                current_city_obj = self.city_map[current.what]

                actual_cost = current.cost + cost_fn(outgoing_road)
                f = actual_cost + heuristic(
                        end_city_obj, current_city_obj, next_city_obj, outgoing_road, current.path)

                next_city_visited = visiteds.get(next_city)
                if next_city_visited:
                    if next_city_visited.cost <= actual_cost:
                        continue

                new_path = current.path[:]
                new_path.append((next_city_obj, outgoing_road))

                heappush(pq, (f, Visited(next_city, new_path, actual_cost)))

        if timeit:
            end = time.clock()
            print("Search took " + str(end - begin) + " seconds.")


################################################################################
## Heuristics

def heuristic_constant(current_city, next_city, target_city, road, visiteds):
    """A heuristic that assigns same cost to every node(except the target,
    which is assigned 0). Effectively this makes A* same as BFS."""
    if target_city.name == next_city.name:
        return 0
    return 1

def heuristic_straight_line(current_city, next_city, target_city, road, visiteds):
    """Straight line distance heuristic. Distance is calcuated using Haversine
    formula from latitude and longitudes."""
    if not (target_city.lat and target_city.long):
        # We can't do anything useful here, just assign minimum cost to every
        # node.
        return 1

    if not (next_city.lat and next_city.long):
        # We assign a cost for the best possible case: Starting with last known
        # location with latitudes and longitudes, we sum the distances we took,
        # and assume that that distance was a straight line from the city
        # towards target. Since you can't take that distance while getting more
        # closer to the target, this is admissible.
        #
        # If multiple cities in the visiteds list has unknown lat/long, we sum
        # distances of roads used, and assume that distance was towards the
        # goal.
        dists = 0
        for (visited, used_road) in reversed(visiteds):
            dists += used_road.distance
            if visited.lat and visited.long:
                diff = distance_miles(target_city.lat, target_city.long, visited.lat, visited.long)
                # This is where I realized this heuristic is actually not
                # admissable. Assume three unknown cities, each with same
                # distance from the target. If we visit each one we should have
                # same heuristic, but instead our cost may get bigger as we
                # move from one to other. This is again unlikely, but still,
                # FIXME.
                #
                # TODO: One thing we can do is to generate middle point of all
                # the neighbor cities and assume that's the point. But would
                # that be admissible?
                #
                # Another safe but potentially inefficient heuristic is to give
                # smallest cost to cities with unknown positions.
                return abs(diff - dists)

        # What? It seems like all of the cities in the list has unknown
        # lat/long. This seems very unlikely, but we don't want to crash in the
        # case of an exceptional input. Just return minimum cost to not
        # eliminate any potential solutions.
        return 1

    # Hopefully this is what we use most of the time.
    return distance_miles(target_city.lat, target_city.long, next_city.lat, next_city.long)

################################################################################
## Cost functions

# Cost functions calculate cost of moving from one node to another node, using
# the given road.

# NOTE: Currently they're more general than needed. For this assignment all we
# need to know in cost functions is the road used, but no big deal.

def cost_distance(used_road):
    """Use when the cost is the distance we take."""
    return used_road.distance

def cost_segments(used_road):
    """Use when the cost is amount of turns we make."""
    return 1

def cost_time(used_road):
    """Use when the cost is total time spent on the road."""
    return used_road.distance / used_road.max_speed

################################################################################
## Utilities

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

def middle_point(points):
    """Calculate geographic midpoint of given points. There should be at least
    two points. Algorithm is taken from http://www.geomidpoint.com/calculation.html
    """
    assert len(points) >= 2

    import math

    xs = []
    ys = []
    zs = []

    for (lat, long) in points:
        lat_rads = math.radians(lat)
        long_rads = math.radians(long)

        x = math.cos(lat_rads) * math.cos(long_rads)
        y = math.cos(lat_rads) * math.sin(long_rads)
        z = math.sin(lat_rads)

        xs.append(x)
        ys.append(y)
        zs.append(z)

    x = sum(xs) / len(xs)
    y = sum(ys) / len(ys)
    z = sum(zs) / len(zs)

    long = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)

    lat_dgr = math.degrees(lat)
    long_dgr = math.degrees(long)

    return (lat_dgr, long_dgr)


################################################################################
## Entry

def parse_routing_option(s):
    s = s.lower()
    if s not in ["segments", "distance", "time"]:
        msg = s + ' is not a valid routing option. ' + \
                'It should be one of "segments", "distance", "time".'
        raise argparse.ArgumentTypeError(msg)
    return s

def parse_routing_algorithm(s):
    s = s.lower()
    if s not in ["bfs", "dfs", "astar"]:
        msg = s + ' is not a valid routing algorithm. ' + \
                'It should be one of "bfs", "dfs", "astar".'
        raise argparse.ArgumentTypeError(msg)
    return s

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="Assignment 1 Problem 2")
    arg_parser.add_argument("start-city", type=str, nargs=1)
    arg_parser.add_argument("end-city", type=str, nargs=1)
    arg_parser.add_argument("routing-option", type=parse_routing_option, nargs=1)
    arg_parser.add_argument("routing-algorithm", type=parse_routing_algorithm, nargs=1)
    arg_parser.add_argument("-t", "--time", action="store_true")

    args = vars(arg_parser.parse_args())
    routing_algorithm = args["routing-algorithm"][0]
    routing_option = args["routing-option"][0]
    start_city = args["start-city"][0]
    end_city = args["end-city"][0]
    timeit = args["time"]
    print args

    m = parse_map()
    m.fill_missing_gps()

    if routing_algorithm in ["bfs", "dfs"]:
        print("WARNING: BFS and DFS don't care about costs and heuristics, " + \
                "routing option is ignored.")
        if routing_algorithm == "bfs":
            print(m.bfs(start_city, end_city, timeit))
        else: # dfs
            print(m.dfs(start_city, end_city, timeit))
    else:
        if routing_option == "segments":
            cost_fun = cost_segments
            heuristic_fun = heuristic_constant
        elif routing_option == "distance":
            cost_fun = cost_distance
            heuristic_fun = heuristic_straight_line
        else: # time
            cost_fun = cost_time
            heuristic_fun = None # FIXME
        print(m.astar(start_city, end_city, heuristic_fun, cost_fun, timeit))
