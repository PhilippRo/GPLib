from data import *
from fitting import *
from tex import *
import unittest
import numpy as np
import sympy


class DataTestCase(unittest.TestCase):

    def test_consume(self):
        d = np.array([1,2,3,4,5])
        x = Data("x", np.array([1, 2, 3, 4, 5]),
            uncert_stat = np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            uncert_sys = np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        y = Data("y", np.array([1, 2, 3, 4, 5]),
            uncert_stat = np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            uncert_sys = np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        tex_file = TexFile("test.tex")
        res = (x + y*y).consume("res", tex_file)
        self.assertTrue(np.array_equal(res.data , d + d ** 2))

        with self.assertRaises(ValueError) :
            res + x

    def test_sin(self):
        d = np.array([np.pi, np.pi/2])
        x = Data("x", np.array([np.pi, np.pi/2]),
            uncert_stat = np.array([0.1, 0.12]),
            uncert_sys = np.array([0.1, 0.12]))
        res = ExpressionSin(x).consume("res")
        self.assertTrue(np.array_equal(res.data , np.sin(d)))

    def test_lin_reg(self):
        x = Data("x", np.array([1, 2, 3, 4, 5]),
            uncert_stat = np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            uncert_sys = np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        y = Data("y", np.array([1, 2, 3, 4, 5]),
            uncert_stat = np.array([0.1, 0.12, 0.11, 0.1, 0.1]),
            uncert_sys = np.array([0.1, 0.12, 0.11, 0.1, 0.1]))
        lr = Expression(x) < Expression(y)
        m = lr.slope('m')
        c = lr.axis_intercept('c')
        y_m = lr.model('y_m', x)
        lr.save_to_file("test", "x", "y", 20, tex_file = tex_file, legend_font_size = 10)

    def test_error_prop(self):
        d = np.array([0,np.pi/2, np.pi])
        x = Data("x", d,
            uncert_stat = np.array([0.1,0.2,0.1]),
            uncert_sys = np.array([0.2,0.4,0.4]))
        d2 = np.array([1,2,2])
        c = Data("c", d2,
            uncert_stat = np.array([0,0,0]),
            uncert_sys = np.array([0,0,0]))
        res = (c * ExpressionSin(x)).consume("res")
        data_equal = True
        uncert_stat_equal = True
        uncert_sys_equal = True
        for i in range(len(res.data)) :
            if np.abs( res.data - d2 * np.sin( d ) )[i] > 0.00001:
                data_equal = False
                break
            if np.abs( res.uncert_stat - np.abs(np.asarray( [0.1,0.2,0.1] ) * d2 * np.cos(d)) )[i] > 0.00001:
                uncert_stat_equal = False
                break
            if np.abs( res.uncert_sys- np.abs(np.asarray( [0.2,0,0.4] ) * d2 * np.cos(d)) )[i] > 0.00001:
                uncert_sys_equal = False
                break
        self.assertTrue( data_equal )
        self.assertTrue( uncert_stat_equal )
        self.assertTrue( uncert_sys_equal )

    def test_curve_fit( self ):
        x_d = np.asarray([-1,1,2,3])
        y_d = np.asarray([2.2,1.9,5,12])

        x = Data("x", x_d)
        y = Data("y", y_d, uncert_stat=np.asarray([0.5,0.2,0.2, 0.2]), uncert_sys=np.asarray([0.5,0.5,1,3]))

        p1, p2, p3 = sympy.symbols("p1 p2 p3")
        f = p1* x.symbol**2 + p2*x.symbol + p3

        curve_fit_result = curve_fit( x, y, (f, (x.symbol, p1, p2, p3)) )

unittest.main()
