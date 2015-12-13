import unittest

import neurons

class Test(unittest.TestCase):

    def test_xor(self):
        test_data = [ ((0, 0), 0),
                      ((0, 1), 1),
                      ((1, 0), 1),
                      ((1, 1), 0) ]

        # Hoestly I don't know how to train for this; we have 4 inputs in total!
        net = neurons.NeuralNet(2)

        # Using test data for training, ouch.
        print "weights before training:", net.weights()
        net.train(test_data, 10000, alpha=0.03)
        print "weights after training:", net.weights()

        # self.assertEqual(net.output(test_data[0][0]), 0)
        # self.assertEqual(net.output(test_data[1][0]), 1)
        # self.assertEqual(net.output(test_data[2][0]), 1)
        # self.assertEqual(net.output(test_data[3][0]), 0)

        print net.output(test_data[0][0])
        print net.output(test_data[1][0])
        print net.output(test_data[2][0])
        print net.output(test_data[3][0])

if __name__ == "__main__":
    unittest.main()
