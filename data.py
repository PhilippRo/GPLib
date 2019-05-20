
from util import quad_add
from tex import TexFile
from deprecated import deprecated as depr
from sympy import *
import matplotlib.pyplot as plt
import numpy as np
import numbers

from praktikum.analyse import mittelwert_stdabw, lineare_regression, lineare_regression_xy

tex_file = TexFile("tex_file.tex")

class LinRegResult:

    def __init__( self, xs, ys, remove_cov=True ):
        if not isinstance( xs, Data ) :
            xs = xs.consume("xs", tex_file)
        if not isinstance( ys, Data ) :
            ys = ys.consume("ys", tex_file)

        self.xs = xs.data
        self.ys = ys.data
        self.x_err_stat = xs.uncert_stat
        self.x_err_sys = xs.uncert_sys
        self.y_err_stat = ys.uncert_stat
        self.y_err_sys = ys.uncert_sys

        self.remove_cov = remove_cov
        if remove_cov :
            self.xs_mittel = mittelwert_stdabw( xs.data )[0]
            xs = (xs - self.xs_mittel).consume('x')
            self.ys_mittel = mittelwert_stdabw( ys.data )[0]
            ys = (ys - self.ys_mittel).consume('y')
        else :
            self.xs_mittel = 0
            self.ys_mittel = 0

        if (xs.uncert_stat == np.zeros(len(xs.uncert_stat))).all():
            m, m_stat, c, c_stat, chi_q, _ = lineare_regression(xs.data, ys.data, ys.uncert_stat)
            m1, _, c1, _, _, _ = lineare_regression(xs.data, ys.data + ys.uncert_sys, ys.uncert_stat)
            m2, _, c2, _, _, _ = lineare_regression(xs.data, ys.data - ys.uncert_sys, ys.uncert_stat)

            self.chi_q = chi_q
            self.m = m
            self.m_err_sys = (np.abs(m2 - m) + np.abs(m - m1)) * 0.5
            self.m_err_stat = m_stat
            self.c = c
            self.c_err_sys = (np.abs(c2 - c) + np.abs(c - c1)) * 0.5
            self.c_err_stat = c_stat
            self.blacklist = xs.blacklist + ys.blacklist

        else:
            m, m_stat, c, c_stat, chi_q, _ = lineare_regression_xy(xs.data, ys.data, xs.uncert_stat, ys.uncert_stat)
            m1, _, c1, _, _, _ = lineare_regression_xy(xs.data + xs.uncert_sys, ys.data, xs.uncert_stat, ys.uncert_stat)
            m2, _, c2, _, _, _ = lineare_regression_xy(xs.data - xs.uncert_sys, ys.data, xs.uncert_stat, ys.uncert_stat)
            m3, _, c3, _, _, _ = lineare_regression_xy(xs.data, ys.data + ys.uncert_sys, xs.uncert_stat, ys.uncert_stat)
            m4, _, c4, _, _, _ = lineare_regression_xy(xs.data, ys.data - ys.uncert_sys, xs.uncert_stat, ys.uncert_stat)

            self.chi_q = chi_q
            self.m = m
            self.m_err_sys = quad_add([np.abs(m2 - m) + np.abs(m - m1), np.abs(m4 - m) + np.abs(m - m3)]) * 0.5
            self.m_err_stat = m_stat
            self.c = c
            self.c_err_sys = quad_add([np.abs(c2 - c) + np.abs(c - c1), np.abs(c4 - c) + np.abs(c - c3)]) * 0.5
            self.c_err_stat = c_stat
            self.blacklist = xs.blacklist + ys.blacklist

    @depr("slope is deprecated, use params instead")
    def slope(self, symbol) :
        return Data(symbol, self.m, uncert_stat=self.m_err_stat, uncert_sys=self.m_err_sys, blacklist=self.blacklist)

    @depr("axis_intercept is deprecated, use params instead")
    def axis_intercept(self, symbol) :
        return Data(symbol, self.c, uncert_stat=self.c_err_stat, uncert_sys=self.c_err_sys, blacklist=self.blacklist)

    def params(self, m_symbol, c_symbol=None) :
        m = Data(m_symbol, self.m, uncert_stat=self.m_err_stat, uncert_sys=self.m_err_sys, blacklist=self.blacklist)
        if self.remove_cov :
            c = ExpressionSub( self.ys_mittel, self.m * self.xs_mittel )
        else :
            c = Data(c_symbol, self.c, uncert_stat=self.c_err_stat, uncert_sys=self.c_err_sys, blacklist=self.blacklist)
        return m, c

    def model(self, y_symbol, x) :
        m, c = self.params('m_intern', 'c_intern')
        m = Data('m_intern', m.data, uncert_sys=np.sqrt( m.uncert_stat**2 + m.uncert_sys**2 ))
        if not isinstance( c, Data ):
            c = c.consume('c_intern')
        c = Data('c_intern', c.data, uncert_sys=np.sqrt( c.uncert_stat**2 + c.uncert_sys**2 ))
        res = ( m*x + c ).consume(y_symbol)
        res.blacklist.remove(m)
        res.blacklist.remove(c)
        return res

    def y_model(self, name) :
        x = Data('x_intern', self.xs, self.x_err_stat, self.x_err_sys)
        m = Data('m_intern', self.m)
        if self.remove_cov :
            c = ExpressionSub( self.ys_mittel, self.m * self.xs_mittel )
        else :
            c = Data('c_intern', self.c)
        res = ( m*x + c ).consume(name)
        res.blacklist.remove(x)
        res.blacklist.remove(m)
        if not self.remove_cov :
            res.blacklist.remove(c)
        return res

    def ndf( self ):
        return len(self.xs) - 2

    def chi_q_over_ndf( self ) :
        return self.chi_q / self.ndf()

    def save_to_file(self, filen, xname, yname, font_size, legend_font_size = None,
            tex_file = None, title = None, Description = None):
        plt.rcParams.update({'font.size': font_size})
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        fig = plt.figure(figsize=(20,16))
        grid = plt.GridSpec(8,8)

        res_plot = fig.add_subplot(grid[-2:, :])
        data_plot = fig.add_subplot(grid[:-3:, :], sharex = res_plot)

        data_plot.plot(self.xs, self.y_model('y_intern').data, label=r'Fit', color='g', marker='', linewidth=4)
        data_plot.errorbar(self.xs, self.ys, yerr=self.y_err_stat, xerr=self.x_err_stat,
                ecolor='r', capsize =  2, elinewidth=2, linewidth=0, label=r"Daten")


        res_plot.plot(self.xs, np.zeros(len(self.xs)))
        res_plot.errorbar(self.xs, self.ys - self.y_model('y_intern').data, ecolor="r",
            yerr = self.y_err_stat + self.m * self.x_err_stat,
            capsize=3, elinewidth=1, label = r"Residuengraph $f(x) - y$",
                fmt='', linewidth=0)

        if legend_font_size is None:
            legend_font_size = font_size

        data_plot.legend(fontsize=legend_font_size)
        res_plot.legend(fontsize=legend_font_size)

        if title is None:
            title = "Lineare Regression + Residuenplot"

        plt.title(title, fontsize=1.3*font_size)
        plt.xlabel(xname, fontsize=font_size)
        plt.ylabel(yname, fontsize=font_size)

        plt.savefig(filen+'.eps', bbox_inches = "tight")

        plt.close()

        if tex_file is not None:
            tex_file.write_section({'Parameter': ['m', 'c', '$\\frac{\chi^2}{ndf}$'],
                'Wert': [self.m, self.c, self.chi_q_over_ndf()],
                'Stat. Fehler': [self.m_err_stat, self.c_err_stat, "-"],
                'Sys. Fehler': [self.m_err_sys, self.c_err_sys, "-"]},
                Description = "Ergebnisse Lineare Regression",
                caption= title if title is not None else filen)


class Data:

    def __init__(self, symbol ,data, uncert_stat=0, uncert_sys=0, blacklist = []):
        if isinstance( data, np.ndarray ) :
            if isinstance( uncert_stat, numbers.Number ) and uncert_stat == 0 :
                uncert_stat = np.zeros(len(data))
            if isinstance( uncert_sys, numbers.Number ) and uncert_sys == 0 :
                uncert_sys = np.zeros(len(data))
            if (not data.shape == uncert_stat.shape) or (not data.shape == uncert_sys.shape) :
                raise ValueError("data, uncert_stat and uncert_sys must be of equal shape")
        elif (not isinstance( data, numbers.Number )) or (not isinstance( uncert_stat, numbers.Number )) or (not isinstance( uncert_sys, numbers.Number )) :
            raise ValueError("data, uncert_stat and uncert_sys must be Number or np.array")
        self.data = data
        self.uncert_stat = uncert_stat
        self.uncert_sys = uncert_sys
        self.blacklist = blacklist
        if len(symbol.split(" ")) == 1:
            self.symbol = symbols(symbol)
            self.symbols = [self]
        else:
            raise ValueError("Symbol string may not contain spaces")

    def get_sympy_expr(self):
        return self.symbol

    def __eq__(self, rhs):
        return self.symbol == rhs.symbol

    def __add__(self, rhs):
        expr = ExpressionAdd(self, rhs)
        return expr

    def __sub__(self, rhs):
        expr = ExpressionSub(self, rhs)
        return expr

    def __mul__(self, rhs):
        expr = ExpressionMul(self, rhs)
        return expr

    def __truediv__(self, rhs):
        expr = ExpressionDiv(self, rhs)
        return expr

    def __pow__(self, rhs):
        expr = ExpressionPow(self, rhs)
        return expr

    def __lt__(self, rhs):
        return LinRegResult( self, rhs  )

    def __str__(self):
        if isinstance( self.data, np.ndarray ):
            out = "{} = [\n".format(self.symbol)
            data = [self.data, self.uncert_stat, self.uncert_sys]
            data = list(map( list, zip(*data)))
            for d in data:
                out += "\t({} +- {} +- {})\n".format(d[0], d[1], d[2])
            return out + "]\n"
        else :
            out = "{} = ".format(self.symbol)
            out += "({} +- {} +- {})".format(self.data, self.uncert_stat, self.uncert_sys)
            return out



class Expression:

    def __init__(self, data):
        self.data = data
        self.symbols = [data]
        self.blacklist = data.blacklist

    def add_symbol(self, sym):
        if sym not in self.symbols:
            if sym in self.blacklist :
                raise ValueError("symbol in blacklist!")

            self.symbols.append(sym)

    def unite_blacklist(self, lhs, rhs):
        self.blacklist = lhs.blacklist.copy()
        self.blacklist.extend(
            [x for x in rhs.blacklist if x not in lhs.blacklist])

    def unite_symbols(self, lhs, rhs):
        if isinstance( lhs, Data ) or isinstance( lhs, Expression ) :
            self.symbols = lhs.symbols.copy()
            if isinstance( rhs, Data ) or isinstance( rhs, Expression ) :
                self.symbols.extend(
                    [x for x in rhs.symbols if x not in lhs.symbols])
                self.unite_blacklist(lhs, rhs)
            else :
                self.blacklist = lhs.blacklist.copy()
        else :
            if isinstance( rhs, Data ) or isinstance( rhs, Expression ) :
                self.symbols = rhs.symbols.copy()
                self.blacklist = rhs.blacklist.copy()
            else :
                self.symbols = []
                self.blacklist = []
        for s in self.symbols:
            if s in self.blacklist :
                raise ValueError("One or more symbols in blacklist: {}".format(s.symbol))

    def __add__(self, rhs):
        return ExpressionAdd(self, rhs)

    def __mul__(self, rhs):
        return ExpressionMul(self, rhs)

    def __sub__(self, ths):
        return ExpressionSub(self, ths)

    def __truediv__(self, rhs):
        return ExpressionDiv(self, rhs)

    def __pow__(self, rhs):
        return ExpressionPow(self, rhs)

    #lineare regression
    def __lt__(self, rhs):
        return LinRegResult( self, rhs  )

    def consume(self, name , tex_file = None):
        expr = self.get_sympy_expr()
        symbols = [x.symbol for x in self.symbols]
        err_expr =  [diff(expr, x.symbol) for x in self.symbols]
        prop_err = [lambdify(symbols, expr)(*[x.data for x in self.symbols])
            for  expr in err_expr]
        prop_stat_err = [a * b for (a,b) in zip(prop_err, [x.uncert_stat for x in self.symbols])]
        prop_sys_err = [a * b for (a,b) in zip(prop_err, [x.uncert_sys for x in self.symbols])]

        lambda_expr = lambdify(symbols, expr)
        ndata = lambda_expr(*[x.data for x in self.symbols])
        if tex_file is not None:
            tex_file.write_table({"Parameter": [latex(sym) for sym in symbols],
                "Fortpflanzungsterm": [latex(expr) for expr in err_expr],
                "Durchschnittlicher stat. Fehler": [ np.average(stat) for stat in prop_stat_err],
                "Druchschnittlicher sys. Fehler": [np.average(sys) for sys in prop_sys_err]},
                caption = "Fehlerfortpflanzung auf ${}$".format(latex(expr)))
        return Data(name, ndata, uncert_stat=quad_add(prop_stat_err), uncert_sys=quad_add(prop_sys_err), blacklist=self.symbols.copy() )

    def get_sympy_expr(self):
        return self.data.get_sympy_expr()

    def __str__(self):
        return self.get_sympy_expr().__str__() + self.consume( "temp" ).__str__()[4:]


class ExpressionAdd(Expression):

    def __init__(self, lhs, rhs):
        if not (isinstance( lhs, Data ) or isinstance( lhs, Expression ) or isinstance( lhs, numbers.Number )) :
            raise TypeError("LHS must be either Data, Expression or Number")
        if not (isinstance( rhs, Data ) or isinstance( rhs, Expression ) or isinstance( rhs, numbers.Number )) :
            raise TypeError("RHS must be either Data, Expression or Number")
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        if isinstance( self.lhs, Data ) or isinstance( self.lhs, Expression ) :
            lhs = self.lhs.get_sympy_expr()
        else :
            lhs = self.lhs
        if isinstance( self.rhs, Data ) or isinstance( self.rhs, Expression ) :
            rhs = self.rhs.get_sympy_expr()
        else :
            rhs = self.rhs
        return lhs + rhs



class ExpressionSub(Expression):

    def __init__(self, lhs, rhs):
        if not (isinstance( lhs, Data ) or isinstance( lhs, Expression ) or isinstance( lhs, numbers.Number )) :
            raise TypeError("LHS must be either Data, Expression or Number")
        if not (isinstance( rhs, Data ) or isinstance( rhs, Expression ) or isinstance( rhs, numbers.Number )) :
            raise TypeError("RHS must be either Data, Expression or Number")
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        if isinstance( self.lhs, Data ) or isinstance( self.lhs, Expression ) :
            lhs = self.lhs.get_sympy_expr()
        else :
            lhs = self.lhs
        if isinstance( self.rhs, Data ) or isinstance( self.rhs, Expression ) :
            rhs = self.rhs.get_sympy_expr()
        else :
            rhs = self.rhs
        return lhs - rhs



class ExpressionMul(Expression):

    def __init__(self, lhs, rhs):
        if not (isinstance( lhs, Data ) or isinstance( lhs, Expression ) or isinstance( lhs, numbers.Number )) :
            raise TypeError("LHS must be either Data, Expression or Number")
        if not (isinstance( rhs, Data ) or isinstance( rhs, Expression ) or isinstance( rhs, numbers.Number )) :
            raise TypeError("RHS must be either Data, Expression or Number")
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        if isinstance( self.lhs, Data ) or isinstance( self.lhs, Expression ) :
            lhs = self.lhs.get_sympy_expr()
        else :
            lhs = self.lhs
        if isinstance( self.rhs, Data ) or isinstance( self.rhs, Expression ) :
            rhs = self.rhs.get_sympy_expr()
        else :
            rhs = self.rhs
        return lhs * rhs


class ExpressionDiv(Expression):

    def __init__(self, lhs, rhs):
        if not (isinstance( lhs, Data ) or isinstance( lhs, Expression ) or isinstance( lhs, numbers.Number )) :
            raise TypeError("LHS must be either Data, Expression or Number")
        if not (isinstance( rhs, Data ) or isinstance( rhs, Expression ) or isinstance( rhs, numbers.Number )) :
            raise TypeError("RHS must be either Data, Expression or Number")
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        if isinstance( self.lhs, Data ) or isinstance( self.lhs, Expression ) :
            lhs = self.lhs.get_sympy_expr()
        else :
            lhs = self.lhs
        if isinstance( self.rhs, Data ) or isinstance( self.rhs, Expression ) :
            rhs = self.rhs.get_sympy_expr()
        else :
            rhs = self.rhs
        return lhs / rhs


class ExpressionPow(Expression):

    def __init__(self, lhs, rhs):
        if not (isinstance( lhs, Data ) or isinstance( lhs, Expression ) or isinstance( lhs, numbers.Number )) :
            raise TypeError("LHS must be either Data, Expression or Number")
        if not (isinstance( rhs, Data ) or isinstance( rhs, Expression ) or isinstance( rhs, numbers.Number )) :
            raise TypeError("RHS must be either Data, Expression or Number")
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        if isinstance( self.lhs, Data ) or isinstance( self.lhs, Expression ) :
            lhs = self.lhs.get_sympy_expr()
        else :
            lhs = self.lhs
        if isinstance( self.rhs, Data ) or isinstance( self.rhs, Expression ) :
            rhs = self.rhs.get_sympy_expr()
        else :
            rhs = self.rhs
        return lhs ** rhs


def GPLog(arg):
    return ExpressionLog(arg)

class ExpressionLog(Expression):

    def __init__(self, expr):
        self.expr = expr
        self.blacklist = expr.blacklist
        self.symbols = expr.symbols

    def get_sympy_expr(self):
        return log(self.expr.get_sympy_expr())

def GPSin(arg):
    return ExpressionSin(arg)

class ExpressionSin(Expression):

    def __init__(self, expr):
        self.expr = expr
        self.blacklist = expr.blacklist
        self.symbols = expr.symbols

    def get_sympy_expr(self):
        return sin(self.expr.get_sympy_expr())

class ExpressionCos(Expression):

    def __init__(self, expr):
        self.expr = expr
        self.blacklist = expr.blacklist
        self.symbols = expr.symbols

    def get_sympy_expr(self):
        return cos(self.expr.get_sympy_expr())

def scatter( x, y, filen, xname, yname, font_size, legend_font_size = None,
        title = None, Description = None, xlines=None, ylines=None, connect=False):
    plt.rcParams.update({'font.size': font_size})
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    fig = plt.figure(figsize=(20,16))
    grid = plt.GridSpec(8,8)

    plt.errorbar(x.data, y.data, yerr=y.uncert_stat, xerr=x.uncert_stat,
            ecolor='r', capsize =  2, elinewidth=2, linewidth=0, label=r"Daten")
    if connect :
        plt.plot( x.data, y.data, color='r' )


    if legend_font_size is None:
        legend_font_size = font_size

    plt.legend(fontsize=legend_font_size)

    if title is None:
        title = "{} against {}".format( yname, xname)

    plt.title(title, fontsize=1.3*font_size)
    plt.xlabel(xname, fontsize=font_size)
    plt.ylabel(yname, fontsize=font_size)

    if not xlines is None :
        for x in xlines :
            plt.axvline(x)

    if not ylines is None :
        for y in ylines :
            plt.axhline(y)

    plt.savefig(filen+'.eps', bbox_inches = "tight")
