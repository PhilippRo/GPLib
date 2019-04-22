from data import *
from tex import *
import unittest
import numpy as np

class DataTestCase(unittest.TestCase):

    def test_consume(self):
        d = np.array([1,2,3,4,5])
        x = Data("x", np.array([1, 2, 3, 4, 5]),
            np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        y = Data("y", np.array([1, 2, 3, 4, 5]),
            np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        tex_file = TexFile("test.tex")
        res = (x + y*y).consume("res", tex_file)
        self.assertTrue(np.array_equal(res.data , d + d ** 2))


unittest.main()
