import itertools

class ImageData:
    def __init__(self, name, orientation, rgbs):
        self.name = name
        self.orientation = orientation
        self.rgbs = rgbs

    def __str__(self):
        return "ImageData<name: " + self.name + "\n" + \
               "          orientation: " + str(self.orientation) + "\n" + \
               "          rgbs: " + str(self.rgbs) + ">"

    def __repr__(self):
        return self.__str__()


def minkowski_dist(p, ds1, ds2):
    """Minkowski distance of given p for two ImageData."""
    for ((r1, g1, b1), (r2, g2, b2)) in itertools.izip(ds1.rgbs, ds2.rgbs):
        s = ( abs(r1 - r2) ** p ) + \
            ( abs(g1 - g2) ** p ) + \
            ( abs(b1 - b2) ** p )

    return s ** (1.0 / float(p))

def parse_img_file(file):
    f = open(file, 'r')

    ret = []

    for line in f.readlines():
        parts = line.split()
        name = parts[0]
        orient = int(parts[1])

        assert ((len(parts) - 2) % 3 == 0)

        rgbs = []

        for i in xrange(2, len(parts), 3):
            r = int(parts[i  ])
            g = int(parts[i+1])
            b = int(parts[i+2])

            rgbs.append((r, g, b))

        ret.append(ImageData(name, orient, rgbs))

    return ret

def nn(k, train_data, img):
    """K-nearest-neighbors."""
    nns = []

    worst_idx = None
    worst_dist = None

    for train_img in train_data:
        # TODO: I think this distance function is basically useless for this
        # purpose. Do I need to do some pre-processing and generate features
        # etc?
        dist = minkowski_dist(1, train_img, img)

        if len(nns) < k:
            nns.append((train_img, dist))
            worst_idx = None
            worst_dist = None
        else:
            # Find neighbor with worst distance if necessary.
            if worst_idx == None:
                for (idx, (n, n_dist)) in enumerate(nns):
                    if n_dist > worst_dist:
                        worst_idx = idx
                        worst_dist = n_dist

            if worst_dist > dist:
                nns[worst_idx] = (train_img, dist)
                worst_idx = None
                worst_dist = None

    assert len(nns) == k

    votes_0 = 0
    votes_90 = 0
    votes_180 = 0
    votes_270 = 0

    for (n, _) in nns:
        if n.orientation == 0:
            votes_0 += 1
        elif n.orientation == 90:
            votes_90 += 1
        elif n.orientation == 180:
            votes_180 += 1
        elif n.orientation == 270:
            votes_270 += 1
        else:
            raise RuntimeError("Invalid orientation: " + str(n.orientation))

    # print "votes_0:", votes_0
    # print "votes_90:", votes_90
    # print "votes_180:", votes_180
    # print "votes_270:", votes_270

    return max([(votes_0, 0), (votes_90, 90), (votes_180, 180), (votes_270, 270)], key=lambda x: x[0])[1]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="assignment 6")
    parser.add_argument("training_file")
    parser.add_argument("test_file")
    parser.add_argument("mode", choices=["knn", "nnet"])
    parser.add_argument("knn/nnet_param", type=int)

    args = vars(parser.parse_args())

    train_data = parse_img_file(args["training_file"])
    print "example distance:", minkowski_dist(1, train_data[0], train_data[1])

    test_data = parse_img_file(args["test_file"])

    for test in test_data:
        ret = nn(10, train_data, test)
        result = "(True)" if ret == test.orientation else "(False)"
        print "nn:", ret, result
