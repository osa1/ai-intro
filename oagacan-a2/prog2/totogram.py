import itertools

class Node:
    def __init__(self, value, edge1=None, edge2=None, edge3=None):
        self.value = value
        self.edge1 = edge1
        self.edge2 = edge2
        self.edge3 = edge3

    def show_bfs(self):
        "Show the tree in breadth-first order."
        from collections import deque

        queue = deque([self])

        buf = []
        while len(queue) != 0:
            n = queue.popleft()
            buf.append(str(n.value))
            for edge in [n.edge1, n.edge2, n.edge3]:
                if edge:
                    queue.append(edge)

        return ' '.join(buf)

    def __str__(self):
        def aux(indent, lines):
            ls = lines.split('\n')
            spaces = '\n' + "".join(itertools.repeat('|   ', indent))
            return spaces.join(ls)

        edges = filter(None, [self.edge1, self.edge2, self.edge3])

        if len(edges) == 0:
            return str(self.value)

        strs = [ aux(1, str(edge)) for edge in edges ]

        value_str = str(self.value)
        value_space = 4 - len(value_str)
        first_indent = "".join(itertools.repeat('-', value_space))

        buf = []

        for i in xrange(len(strs)):
            edge_str = strs[i]

            if i == 0:
                buf.append(value_str + first_indent + edge_str)
            elif i == len(strs) - 1:
                buf.append("\---" + edge_str)
            else:
                buf.append("|---" + edge_str)

        return '\n'.join(buf)

if __name__ == "__main__":
    node1 = Node(1)
    node2 = Node(2)

    node_3_1_1 = Node(311)
    node_3_1_2 = Node(312)
    node3_1 = Node(31, node_3_1_1, node_3_1_2)

    node_3_2_1 = Node(321)
    node_3_2_2 = Node(322)
    node3_2 = Node(32, node_3_2_1, node_3_2_2)

    node3_3 = Node(33)
    node3 = Node(3, node3_1, node3_2, node3_3)
    node4 = Node(4, node3, node2, node1)
    print node4

    print node4.show_bfs()
