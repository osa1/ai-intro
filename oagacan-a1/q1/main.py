import copy
import itertools

##
## We define names as constants to 1) minimize typos 2) faster comparsions.
##

IRENE = "Irene"
FRANK = "Frank"
GEORGE = "George"
HEATHER = "Heather"
JERRY = "Jerry"

KIRKWOOD = "Kirkwood St."
LAKE = "Lake Ave."
ORANGE = "Orange Dr."
NORTH = "North Ave."
MAXWELL = "Maxwell St."

CANDELABRUM = "Candelabrum"
BANISTER = "Banister"
DOORKNOB = "Doorknob"
ELEPHANT = "Elephant"
AMPLIFIER = "Amplifier"

PERSONS     = (IRENE, FRANK, GEORGE, HEATHER, JERRY)
LOCATIONS   = (KIRKWOOD, LAKE, ORANGE, NORTH, MAXWELL)
ITEMS       = (CANDELABRUM, BANISTER, DOORKNOB, ELEPHANT, AMPLIFIER)

##
## State
##

class State:

    # We have 5 items each, so no big deal. (two lists with 120 elements)
    location_permutations = list(itertools.permutations(LOCATIONS))
    items_permutations = list(itertools.permutations(ITEMS))

    def __init__(self, locations_idx = 0, ordered_idx = 0, received_idx = 0):
        self.locations_idx = locations_idx
        self.ordered_idx = ordered_idx
        self.received_idx = received_idx

    @property
    def persons(self):
        return PERSONS

    @property
    def locations(self):
        return State.location_permutations[self.locations_idx]

    @property
    def ordered(self):
        return State.items_permutations[self.ordered_idx]

    @property
    def received(self):
        return State.items_permutations[self.received_idx]

    def person_at(self, i):
        return PERSONS[i]

    def location_at(self, i):
        return self.location_permutations[self.locations_idx][i]

    def ordered_at(self, i):
        return self.items_permutations[self.ordered_idx][i]

    def received_at(self, i):
        return self.items_permutations[self.received_idx][i]

    def next_state(self):
        # NOTE: A quick benchmark showed that iterating through all the
        # permutations takes about 2 seconds. (it's actually 2.21s, but that
        # includes Python startup, generating initial permutation lists etc.)

        if self.received_idx < len(State.items_permutations) - 1:
            return State(self.locations_idx,
                         self.ordered_idx,
                         self.received_idx + 1)

        if self.ordered_idx < len(State.items_permutations) - 1:
            return State(self.locations_idx,
                         self.ordered_idx + 1,
                         0)

        if self.locations_idx < len(State.location_permutations) - 1:
            return State(self.locations_idx + 1,
                         0,
                         0)

        # This means we iterated through all the possible permutations.
        return None

    def __repr__(self):
        return "State(locations_idx=" + str(self.locations_idx) \
                  + ",ordered_idx=" + str(self.ordered_idx) \
                  + ",received_idx=" + str(self.received_idx) \
                  + ")"

    def show(self):
        print "Person  | Location     | Ordered      | Received"
        print "===================================================="

        for i in range(0, 5):
            print add_spaces(self.person_at(i), 7)    + " | " + \
                  add_spaces(self.location_at(i), 12) + " | " + \
                  add_spaces(self.ordered_at(i), 12)  + " | " + \
                  add_spaces(self.received_at(i), 12)

##
## A constraint is a function from a State to a bool.
##

# TODO: One possible optimization here is to remove search_fails for persons,
# because index for each person is fixed.

def constraint_1(state):
    """The person who ordered the candelabrum received the banister."""
    candelabrum_order_idx = search_fail(CANDELABRUM, state.ordered)
    banister_recv_idx = search_fail(BANISTER, state.received)
    return candelabrum_order_idx == banister_recv_idx

def constraint_2(state):
    """The customer who ordered banister received the package that Irene had
    ordered."""
    banister_order_idx = search_fail(BANISTER, state.ordered)
    banister_received = state.received_at(banister_order_idx)
    irene_idx = search_fail(IRENE, state.persons)
    irene_order = state.ordered_at(irene_idx)
    return banister_received == irene_order

def constraint_3(state):
    """Frank received the doorknob."""
    frank_idx = search_fail(FRANK, state.persons)
    frank_received = state.received_at(frank_idx)
    return frank_received == DOORKNOB

def constraint_4(state):
    """George's package went to Kirkwood St."""
    george_idx = search_fail(GEORGE, state.persons)
    george_ordered = state.ordered_at(george_idx)
    kirkwood_idx = search_fail(KIRKWOOD, state.locations)
    kirkwood_received = state.received_at(kirkwood_idx)
    return george_ordered == kirkwood_received

def constraint_5(state):
    """The delivery that should have gone to Kirkwood St. was sent to Lake Ave.
    """
    kirkwood_idx = search_fail(KIRKWOOD, state.locations)
    kirkwood_ordered = state.ordered_at(kirkwood_idx)
    lake_idx = search_fail(LAKE, state.locations)
    lake_received = state.received_at(lake_idx)
    return kirkwood_ordered == lake_received

def constraint_6(state):
    """Heather received the package that was to go to Orange Drive."""
    heather_idx = search_fail(HEATHER, state.persons)
    heather_received = state.received_at(heather_idx)
    orange_idx = search_fail(ORANGE, state.locations)
    orange_ordered = state.ordered_at(orange_idx)
    return heather_received == orange_ordered

def constraint_7(state):
    """Jerry received Heather's order."""
    jerry_idx = search_fail(JERRY, state.persons)
    jerry_received = state.received_at(jerry_idx)
    heather_idx = search_fail(HEATHER, state.persons)
    heather_ordered = state.ordered_at(heather_idx)
    return jerry_received == heather_ordered

def constraint_8(state):
    """The Elephant arrived in North Avenue."""
    elephant_idx = search_fail(ELEPHANT, state.received)
    elephant_location = state.location_at(elephant_idx)
    return elephant_location == NORTH

def constraint_9(state):
    """The person who had ordered the elephant received the package that should
    have gone to Maxwell Street."""
    elephant_ordered_idx = search_fail(ELEPHANT, state.ordered)
    elephant_ordered_received = state.received_at(elephant_ordered_idx)
    maxwell_idx = search_fail(MAXWELL, state.locations)
    maxwell_ordered = state.ordered_at(maxwell_idx)
    return elephant_ordered_received == maxwell_ordered

def constraint_10(state):
    """The customer on Maxwell Street received the Amplifier."""
    maxwell_idx = search_fail(MAXWELL, state.locations)
    maxwell_received = state.received_at(maxwell_idx)
    return maxwell_received == AMPLIFIER

CONSTRAINTS = (constraint_1, constraint_2, constraint_3, constraint_4,
               constraint_5, constraint_6, constraint_7, constraint_8,
               constraint_9, constraint_10)

##
## Utilities
##

def search_fail(string, iterable):
    """Search given string in given iterable, fail with a RuntimeException if
    not found."""

    idx = 0

    for s in iterable:
        if s == string:
            return idx
        idx += 1

    raise RuntimeError('String "' + string + '" not found in iterable.')

def add_spaces(s, l):
    if len(s) < l:
        return s + ' ' * (l - len(s))
    return s

##
## Entry
##

def main():
    current_state = State()

    while current_state:
        found = True
        for constraint in CONSTRAINTS:
            if not constraint(current_state):
                current_state = current_state.next_state()
                found = False
                break

        if found:
            print "SOLUTION FOUND:"
            current_state.show()
            return

if __name__ == "__main__":
    main()
