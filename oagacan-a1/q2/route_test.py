import route

import unittest

test_configs = \
    [ ("Ada,_Oklahoma", "Albany,_California"), \
      ("Bloomington,_Indiana", "New_York,_New_York") ]

class TestMoveMethods(unittest.TestCase):
    def setUp(self):
        self.m = route.parse_map()
        self.m.fill_missing_gps()

    def test_bfs_runs(self):
        for (c1, c2) in test_configs:
            self.assertIsNotNone(self.m.bfs(c1, c2))

    def test_dfs_runs(self):
        for (c1, c2) in test_configs:
            self.assertIsNotNone(self.m.dfs(c1, c2))

    def test_astar_constant(self):
        test = ("Yankton,_South_Dakota", "Bigfork,_Montana")
        astar_result = self.m.astar(test[0], test[1], route.heuristic_constant, route.cost_segments)
        self.assertIsNotNone(astar_result)
        bfs_result = self.m.bfs(test[0], test[1])
        self.assertIsNotNone(bfs_result)
        self.assertEqual(len(bfs_result.path), len(astar_result.path))

    def astar_distance(self, start, end):
        test = ("Bloomington,_Indiana", "Indianapolis,_Indiana")
        astar_result = self.m.astar(
                start, end, route.heuristic_straight_line, route.cost_distance)
        self.assertIsNotNone(astar_result)

        uniform_result = self.m.uniform_cost(start, end, route.cost_distance)
        self.assertIsNotNone(uniform_result)

        if astar_result.cost != uniform_result.cost:
            print "A* result:"
            print astar_result
            print "Dijkstra result:"
            print uniform_result
        self.assertEqual(astar_result.cost, uniform_result.cost)

    def test_astar_distance(self):
        self.astar_distance("Bloomington,_Indiana",  "Indianapolis,_Indiana")

    def test_astar_distance_2(self):
        self.astar_distance("Bloomington,_Indiana",  "Chicago,_Illinois")

if __name__ == "__main__":
    unittest.main()
