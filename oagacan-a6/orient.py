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
