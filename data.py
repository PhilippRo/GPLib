
from util import quad_add
from tex import TexFile
from sympy import *
import matplotlib.pyplot as plt
import numpy as np
import numbers

from praktikum.analyse import lineare_regression, lineare_regression_xy

tex_file = TexFile("tex_file.tex")

class LinRegResult:

    def __init__(self, xs, ys, x_err_stat, y_err_stat,
            x_err_sys, y_err_sys, chi_q, m, m_err_stat,
            m_err_sys, c, c_err_stat, c_err_sys,
            blacklist ):
        self.xs = xs
        self.ys = ys
        self.x_err_stat = x_err_stat
        self.x_err_sys = x_err_sys
        self.y_err_stat = y_err_stat
        self.y_err_sys = y_err_sys
        self.chi_q = chi_q
        self.m = m
        self.m_err_sys = m_err_sys
        self.m_err_stat = m_err_stat
        self.c = c
        self.c_err_sys = c_err_sys
        self.c_err_stat = c_err_stat
        self.blacklist = blacklist

    def slope(self, symbol) :
        return Data(symbol, self.m, uncert_stat=self.m_err_stat, uncert_sys=self.m_err_sys, blacklist=self.blacklist)

    def axis_intercept(self, symbol) :
        return Data(symbol, self.c, uncert_stat=self.c_err_stat, uncert_sys=self.c_err_sys, blacklist=self.blacklist)

    def model(self, y_symbol, x) :
        # TODO fix error propragation!
        m = Data('m_intern', self.m, uncert_sys=self.m_err_stat)
        c = Data('c_intern', self.c, uncert_sys=self.c_err_stat)
        res = ( m*x + c ).consume(y_symbol)
        res.blacklist.remove(m)
        res.blacklist.remove(c)
        return res

    def y_model(self, name) :
        x = Data('x_intern', self.xs, self.x_err_stat, self.x_err_sys)
        m = Data('m_intern', self.m)
        c = Data('c_intern', self.c)
        res = ( m*x + c ).consume(name)
        res.blacklist.remove(x)
        res.blacklist.remove(m)
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

        data_plot.plot(self.xs, self.m * self.xs + self.c, label=r'Fit', color='g', marker='', linewidth=4)
        data_plot.errorbar(self.xs, self.ys, yerr=self.y_err_stat, xerr=self.x_err_stat,
                ecolor='r', capsize =  2, elinewidth=2, linewidth=0, label=r"Daten")


        res_plot.plot(self.xs, np.zeros(len(self.xs)))
        res_plot.errorbar(self.xs, self.ys - self.m * self.xs - self.c, ecolor="r",
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

        if tex_file is not None:
            tex_file.write_section({'Paramter': ['m', 'c', '$\\frac{\chi^2}{ndf}$'],
                'Wert': [self.m, self.c, self.chi_q],
                'Stat. Fehler': [self.m_err_stat, self.c_err_stat, "-"],
                'Sys. Fehler': [self.m_err_sys, self.c_err_sys, "-"]},
                Description = Description,
                caption="Ergebnisse der Linearen Regression")


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

    def __eq__(self, lhs):
        return self.symbol == lhs.symbol

    def __add__(self, lhs):
        expr = ExpressionAdd(self, lhs)
        return expr

    def __sub__(self, lhs):
        expr = ExpressionSub(self, lhs)
        return expr

    def __mul__(self, lhs):
        expr = ExpressionMul(self, lhs)
        return expr

    def __truediv___(self, lhs):
        expr = ExpressionDiv(self, lhs)
        return expr

    def __pow__(self, lhs):
        expr = ExpressionPow(self, lhs)
        return expr

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
        self.symbols = lhs.symbols.copy()
        self.symbols.extend(
            [x for x in rhs.symbols if x not in lhs.symbols])

        self.unite_blacklist(lhs, rhs)
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
        xs = self.consume("xs", tex_file)
        ys = rhs.consume("ys", tex_file)
        if (xs.uncert_stat == np.zeros(len(xs.uncert_stat))).all():
            m, m_stat, c, c_stat, chi_q, _ = lineare_regression(xs.data, ys.data, ys.uncert_stat)
            m1, _, c1, _, _, _ = lineare_regression(xs.data, ys.data + ys.uncert_sys, ys.uncert_stat)
            m2, _, c2, _, _, _ = lineare_regression(xs.data, ys.data - ys.uncert_sys, ys.uncert_stat)
            return LinRegResult(xs.data, ys.data, xs.uncert_stat,
                ys.uncert_stat, xs.uncert_sys, ys.uncert_sys,
                chi_q,
                m, m_stat, (np.abs(m2 - m) + np.abs(m - m1)) * 0.5,
                c, c_stat, (np.abs(c2 - c) + np.abs(c - c1)) * 0.5,
                blacklist=xs.blacklist + ys.blacklist )
        else:
            m, m_stat, c, c_stat, chi_q, _ = lineare_regression_xy(xs.data, ys.data, xs.uncert_stat, ys.uncert_stat)
            m1, _, c1, _, _, _ = lineare_regression_xy(xs.data + xs.uncert_sys, ys.data, xs.uncert_stat, ys.uncert_stat)
            m2, _, c2, _, _, _ = lineare_regression_xy(xs.data - xs.uncert_sys, ys.data, xs.uncert_stat, ys.uncert_stat)
            m3, _, c3, _, _, _ = lineare_regression_xy(xs.data, ys.data + ys.uncert_sys, xs.uncert_stat, ys.uncert_stat)
            m4, _, c4, _, _, _ = lineare_regression_xy(xs.data, ys.data - ys.uncert_sys, xs.uncert_stat, ys.uncert_stat)
            return LinRegResult(xs.data, ys.data, xs.uncert_stat,
                ys.uncert_stat, xs.uncert_sys, ys.uncert_sys,
                chi_q,
                m, m_stat, quad_add([np.abs(m2 - m) + np.abs(m - m1), np.abs(m4 - m) + np.abs(m - m3)]) * 0.5,
                c, c_stat, quad_add([np.abs(c2 - c) + np.abs(c - c1), np.abs(c4 - c) + np.abs(c - c3)]) * 0.5,
                blacklist=xs.blacklist + ys.blacklist )

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
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr() + self.rhs.get_sympy_expr()



class ExpressionSub(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr() - self.rhs.get_sympy_expr()



class ExpressionMul(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr() * self.rhs.get_sympy_expr()


class ExpressionDiv(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr() / self.rhs.get_sympy_expr()


class ExpressionPow(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols( lhs, rhs )

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr() ** self.rhs.get_sympy_expr()

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
