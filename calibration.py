import numpy as np
import sympy
from data import Data
from data import Expression

class Calibration:
    def __init__( self, x_m, x_r ):
        if isinstance( x_m, Expression ) :
            self.mes = x_m
        else :
            self.mes = Expression( x_m )
        if isinstance( x_r, Expression ) :
            self.real = x_r
        else :
            self.real = Expression( x_r )
        self.result = self.mes < self.real

    def calibrate( self, x, x_name ) :
        m = Data('m_intern', self.result.m, uncert_sys=self.result.m_err_stat)
        c = Data('c_intern', self.result.c, uncert_sys=self.result.c_err_stat)
        res = ( m*x + c ).consume(x_name)
        if isinstance( res.data, np.ndarray ) :
            res.uncert_sys = np.zeros(len(res.data))
        else :
            res.uncert_sys = 0
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
