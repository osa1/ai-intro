from confusion_matrix import print_confusion_matrix

import itertools

def minkowski_dist(p, ds1, ds2):
    """Minkowski distance of given p for two ImageData."""
    for ((r1, g1, b1), (r2, g2, b2)) in itertools.izip(ds1.rgbs, ds2.rgbs):
        s = ( abs(r1 - r2) ** p ) + \
            ( abs(g1 - g2) ** p ) + \
            ( abs(b1 - b2) ** p )

    return s ** (1.0 / float(p))

def knn(k, train_data, img):
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

    return max([(votes_0, 0), (votes_90, 90), (votes_180, 180), (votes_270, 270)],
            key=lambda x: x[0])[1]

def run_knn(train_data, test_data, k):
    classified_0   = []
    classified_90  = []
    classified_180 = []
    classified_270 = []

    for test in test_data:
        ret = knn(k, train_data, test)

        ret_str = "(" + str(ret == test.orientation) + ")"
        print test.name, "classified as", ret, ret_str

        if ret == 0:
            classified_0.append(test)
        elif ret == 90:
            classified_90.append(test)
        elif ret == 180:
            classified_180.append(test)
        elif ret == 270:
            classified_270.append(test)
        else:
            raise RuntimeError("Bug: knn returned %s" % str(ret))

    f = open("knn_output.txt", "w")
    print_confusion_matrix(f, classified_0, classified_90, classified_180, classified_270)
    f.close()
