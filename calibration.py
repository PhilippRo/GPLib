import numpy as np
import sympy
from data import Data
from data import Expression
from praktikum import analyse

class Calibration:
    def __init__( self, x_m, x_r, m_symbol, c_symbol ):
        if isinstance( x_m, Expression ) :
            self.mes_mittel = analyse.mittelwert_stdabw( x_m.consume().data )[0]
            self.mes = x_m - self.mes_mittel
        else :
            self.mes_mittel = analyse.mittelwert_stdabw( x_m.data )[0]
            self.mes = Expression( x_m ) - self.mes_mittel
        if isinstance( x_r, Expression ) :
            self.real_mittel = analyse.mittelwert_stdabw( x_r.consume().data )[0]
            self.real = x_r - self.real_mittel
        else :
            self.real_mittel = analyse.mittelwert_stdabw( x_r.data )[0]
            self.real = Expression( x_r ) - self.real_mittel
        self.result = self.mes < self.real
        self.m = result.slope( c_symbol )
        self.c = ExpressionSub( self.real_mittel, self.m * self.mes_mittel )

    def calibrate( self, x, x_name ) :
        m = Data('m_intern', self.result.m, uncert_sys=np.sqrt( self.result.m_err_stat**2 + self.result.m_err_sys**2 ))
        c = Data('c_intern', self.result.c, uncert_sys=np.sqrt( self.result.c_err_stat**2 + self.result.c_err_sys**2 ))
        res = ( m*(x-self.mes_mittel) + c + self.real_mittel ).consume(x_name)
        res.blacklist.remove(m)
        res.blacklist.remove(c)
        return res

    def slope(self) :
        return self.m

    def axis_intercept(self) :
        return self.c

    def save_to_file(self, filen, xname, yname, font_size, legend_font_size = None,
            tex_file = None, title = None):
        return self.result.save_to_file(
                filen, xname, yname, font_size, legend_font_size, tex_file, title )
