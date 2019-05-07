import numpy as np
import sympy
from data import Data
from data import Expression
from praktikum import analyse

class Calibration:
    def __init__( self, x_m, x_r ):
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

    def calibrate( self, x, x_name ) :
        m = Data('m_intern', self.result.m, uncert_sys=self.result.m_err_stat)
        c = Data('c_intern', self.result.c, uncert_sys=self.result.c_err_stat)
        res = ( m*(x-self.mes_mittel) + c + self.real_mittel ).consume(x_name)
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
        c = self.result.axis_intercept( 'c_intern' )
        m = self.result.slope( 'm_intern' )
        ret = ( c - m * self.mes_mittel + self.real_mittel).consume( symbol )
        ret.blacklist.remove( c )
        ret.blacklist.remove( m )
        return ret

    def save_to_file(self, filen, xname, yname, font_size, legend_font_size = None,
            tex_file = None, title = None):
        return self.result.save_to_file(
                filen, xname, yname, font_size, legend_font_size, tex_file, title )
