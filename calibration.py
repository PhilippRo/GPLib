import copy

import numpy as np
import sympy
from data import Data
from data import Expression
from data import ExpressionSub
from praktikum import analyse

class Calibration:
    def __init__( self, x_m, x_r, m_symbol ):
        self.mes = copy.deepcopy(x_m)
        self.real = copy.deepcopy(x_r)
        if isinstance( self.mes.data, np.ndarray ) :
            self.mes.uncert_sys = np.zeros(len(self.mes.data))
        else :
            self.mes.uncert_sys = 0

        self.result = self.mes < self.real
        self.m, self.c = self.result.params( m_symbol )

    def calibrate( self, x, x_name ) :
        x = copy.deepcopy(x)
        if isinstance( x.data, np.ndarray ) :
            x.uncert_sys = np.zeros(len(x.data))
        else :
            x.uncert_sys = 0
        m = Data('m_intern', self.m.data, uncert_sys=np.sqrt( self.m.uncert_stat**2 + self.m.uncert_sys**2 ))
        c = self.c.consume()
        c = Data('c_intern', c.data, uncert_sys=np.sqrt( c.uncert_stat**2 + c.uncert_sys**2 ))
        res = ( m*x + c ).consume(x_name)
        res.blacklist.remove(m)
        res.blacklist.remove(c)
        return res

    def slope(self) :
        return self.m

    def axis_intercept(self) :
        return self.c

    def ndf( self ):
        return len(self.xs) - 2

    def chi_q_over_ndf( self ) :
        return self.chi_q / self.ndf()

    def save_to_file(self, filen, xname, yname, font_size, legend_font_size = None,
            tex_file = None, title = None):
        return self.result.save_to_file(
                filen, xname, yname, font_size, legend_font_size, tex_file, title )
