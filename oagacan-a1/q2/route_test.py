import route

import unittest

test_configs = \
    [ ("Ada,_Oklahoma", "Albany,_California"), \
      ("Bloomington,_Indiana", "New_York,_New_York") ]

class TestMoveMethods(unittest.TestCase):
    def setUp(self):
        self.m = route.parse_map()

    def test_bfs_runs(self):
        for (c1, c2) in test_configs:
            self.assertIsNotNone(self.m.bfs(c1, c2))

    def test_dfs_runs(self):
        for (c1, c2) in test_configs:
            self.assertIsNotNone(self.m.dfs(c1, c2))

    def test_astar_constant(self):
        test = ("Yankton,_South_Dakota", "Bigfork,_Montana")
        astar_result = self.m.astar(test[0], test[1], route.heuristic_constant)
        self.assertIsNotNone(astar_result)
        bfs_result = self.m.bfs(test[0], test[1])
        self.assertIsNotNone(bfs_result)
        self.assertEqual(len(bfs_result.path), len(astar_result.path))

if __name__ == "__main__":
    unittest.main()
