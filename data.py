
from util import quad_add

from sympy import *
import numpy as np

class Data:

    def __init__(self, symbol ,data, uncert_stat, uncert_sys):
        self.data = data
        self.uncert_stat = uncert_stat
        self.uncert_sys = uncert_sys
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



class Expression:

    def add_symbol(self, sym):
        if sym not in self.symbols:
            self.symbols.append(sym)

    def unite_symbols(self, lhs, rhs):
        self.symbols = lhs.symbols.copy()
        self.symbols.extend(
            [x for x in rhs.symbols if x not in lhs.symbols])

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

    def consume(self, name , tex_file = None):
        expr = self.get_sympy_expr()
        symbols = [x.symbol for x in self.symbols]
        stat_err_expr =  [diff(expr, x.symbol) for x in self.symbols]
        prop_stat_err = [lambdify(symbols, expr)(*[x.data for x in self.symbols])
            for  expr in stat_err_expr]
        prop_stat_err = [a * b for (a,b) in zip(prop_stat_err, [x.uncert_stat for x in self.symbols])]

        lambda_expr = lambdify(symbols, expr)
        ndata = lambda_expr(*[x.data for x in self.symbols])
        prop_sys_err = [
            0.5 * np.abs(
                lambda_expr(*[self.symbols[m].data if m != i else
                    self.symbols[m].data - self.symbols[m].uncert_sys for m in range(len(self.symbols))]) -
                lambda_expr(*[self.symbols[m].data if m != i else
                    self.symbols[m].data + self.symbols[m].uncert_sys for m in range(len(self.symbols))])
            ) for i in range(len(self.symbols))]
        if tex_file is not None:
            tex_file.write_table({"Paramter": [latex(sym) for sym in symbols],
                "Fortpflanzungsterm": [latex(expr) for expr in stat_err_expr],
                "Durchschnittlicher stat. Fehler": [ np.average(stat) for stat in prop_stat_err],
                "Druchschnittlicher sys. Fehler": [np.average(sys) for sys in prop_sys_err]},
                caption = "Fehler fortpflanzung auf ${}$".format(latex(expr)))
        return Data(name, ndata, quad_add(prop_stat_err), quad_add(prop_sys_err))



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
        self.symbols = expr.symbols

    def get_sympy_expr(self):
        return log(self.expr.get_sympy_expr())

def GPSin(arg):
    return ExpressionSin(arg)

class ExpressionSin(Expression):

    def __init__(self, expr):
        self.expr = expr
        self.symbols = expr.symbols

    def get_sympy_expr(self):
        return sin(self.expr.get_sympy_expr())
