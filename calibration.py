import copy

import numpy as np
import sympy
from data import Data
from data import Expression

class Calibration:
    def __init__( self, x_m, x_r ):
        x_m = copy.deepcopy(x_m)
        x_r = copy.deepcopy(x_r)
        if isinstance( x_m, Expression ) :
            self.mes = x_m
        else :
            self.mes = Expression( x_m )
        if isinstance( x_r, Expression ) :
            self.real = x_r
        else :
            self.real = Expression( x_r )

        if isinstance( self.mes.data, np.ndarray ) :
            self.mes.uncert_sys = np.zeros(len(self.mes.data))
        else :
            self.mes.uncert_sys = 0

        self.result = self.mes < self.real

    def calibrate( self, x, x_name ) :
        x = copy.deepcopy(x)
        if isinstance( x.data, np.ndarray ) :
            x.uncert_sys = np.zeros(len(x.data))
        else :
            x.uncert_sys = 0
        m = Data('m_intern', self.result.m, uncert_sys=np.sqrt( self.result.m_err_stat**2 + self.result.m_err_sys ))
        c = Data('c_intern', self.result.c, uncert_sys=np.sqrt( self.result.c_err_stat**2 + self.result.c_err_sys ))
        res = ( m*x + c ).consume(x_name)
        res.blacklist.remove(m)
        res.blacklist.remove(c)
        return res

    def slope(self, symbol) :
        return self.result.slope( symbol )

    def axis_intercept(self, symbol) :
        return self.result.axis_intercept( symbol )

    def save_to_file(self, filen, xname, yname, font_size, legend_font_size = None,
            tex_file = None, title = None):
        return self.result.save_to_file(
                filen, xname, yname, font_size, legend_font_size, tex_file, title )
