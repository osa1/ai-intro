################################################################################
# Assignment 6 - Omer Sinan Agacan (oagacan)
#
# I made three attempts at implementing neural nets from scratch, unfortunately
# none of them work(by which I mean they produce bad results). I must be missing
# some very basic thing, but I couldn't figure out why. The main problem is:
#
# - My nets are always generating output in range [0, 1], I have no ideas why.
#
# Funny thing is, I found some code online and tried them using XOR function.
# They never worked well. It seems like most implementations are either broken
# or just suck. One example was able to learn XOR, but that one failed to learn
# when I change it's weird activation functions from tanh() to sigmoid().
#
# knn is also not working great - the problem is I couldn't come up with a
# useful distance function. Other than the distance, the code should be correct.
# (unlike neural net code, which probably has a small but very important bug)
#
# (Do I need to extract some features? Maybe, but I don't understand how am I
# supposed to know this, given that the book or slides are not giving any hints
# about features for rotations etc.)
#
# The bug in my neural net implementation should be a theoretical one, rather
# than an implementation bug. Because I was able to reproduce same
# problem(outputs always in range [0, 1]) with 3 different implementations, all
# done by me.
#
# alpha(the step, or learning rate) is by default 0.9. Maybe the problem is just
# that I need to implement in efficiently(using matrices and numpy) and then
# in learning step iterate hundreds of time. Currently I'm only iterating 5
# times.
#
# The problem though is that I learned that operations on neural nets can be
# done using matrix operations at a very late stage. I simply followed the
# definition given in the book and it's not implemented using matrix operations.
#
# When I learned about this it was already too late - as I have finals.
#
################################################################################

# Parsing images etc.
from img import *

# K-nearest neighbor implementation
import knn

# Second implementation, similarly not working
import neurons

################################################################################
# Entry

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="assignment 6")
    parser.add_argument("training_file")
    parser.add_argument("test_file")
    parser.add_argument("mode", choices=["knn", "nnet", "best"])
    parser.add_argument("knn/nnet/best_param", type=int)

    args = vars(parser.parse_args())

    param = args["knn/nnet/best_param"]

    if args["mode"] == "knn":
        train_data = parse_img_file(args["training_file"])
        test_data = parse_img_file(args["test_file"])
        knn.run_knn(train_data, test_data, param)
    elif args["mode"] == "nnet":
        train_data = parse_img_file(args["training_file"])
        test_data = parse_img_file(args["test_file"])
        neurons.run_nnet(train_data, test_data, param)
    elif args["mode"] == "best":
        print "Best is not implemented"
        sys.exit(1)
