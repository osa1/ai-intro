import unittest

from totogram import *

class Test(unittest.TestCase):
    def testInvariants(self):
        node1 = Node(1)
        node2 = Node(2)

        node1.connect(node2)
        check_invariants(node1, True)
        check_invariants(node2, True)

        node3 = Node(3)
        node4 = Node(4)
        node3.connect(node1)
        node4.connect(node1)
        check_invariants(node1, True)

        node2_1 = Node(21)
        node2_2 = Node(22)
        node2.connect(node2_1)
        node2.connect(node2_2)

        for node in [node1, node2, node3, node4, node2_1, node2_2]:
            check_invariants(node, True)

if __name__ == "__main__":
    unittest.main()
