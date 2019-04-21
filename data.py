
from sympy import *

class Data:

    def __init__(self, symbol ,data, uncert_stat, uncert_sys):
        self.data = data
        self.uncert_stat = uncert_stat
        self.uncert_sys = uncert_sys
        if len(symbol.split(" ")) == 1:
            self.symbol = symbols(symbol)
        else:
            raise ValueError("Symbol string may not contain spaces")

    def get_sympy_expr():
        return self.symbol

    def __add__(self, lhs):
        expr = ExpressionAdd(self, lhs)
        expr.add_symbol(self.symbol)

    def __sub__(self, lhs):
        expr = ExpressionSub(self, lhs)
        expr.add_symbol(self.symbol)

    def __mul__(self, lhs):
        expr = ExpressionMul(self, lhs)
        expr.add_symbol(self.symbol)

    def __div___(self, lhs):
        expr = ExpressionDiv(self, lhs)
        expr.add_symbol(self.symbol)

    def __pow__(self, lhs):
        expr = ExpressionPow(self, lhs)
        expr.add_symbol(self.symbol)



class Expression:

    def add_symbol(self, sym):
        if sym not in self.symbols:
            self.symbols.append(sym)

    def unite_symbols(self, rhs):
        self.symbols = lhs.append(
            [x for x in lhs.symbols if x not in rhs.symbols])

    def __add__(self, rhs):
        ExpressionAdd(self, rhs)

    def __mul__(self, rhs):
        ExpressionSub(self, rhs)

    def __sub__(self, ths):
        ExpressionSub(self, ths)

    def __truediv__(self, rhs):
        ExpressionDiv(self, rhs)

    def __pow__(self, rhs):
        ExpressionPow(self, rhs)



class ExpressionAdd(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols()

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr + self.rhs.get_sympy_expr



class ExpressionSub(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols()

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr - self.rhs.get_sympy_expr



class ExpressionMul(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols()

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr * self.rhs.get_sympy_expr


class ExpressionDiv(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols()

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr / self.rhs.get_sympy_expr


class ExpressionPow(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.unite_symbols()

    def get_sympy_expr(self):
        return self.lhs.get_sympy_expr ** self.rhs.get_sympy_expr

def GPLog(arg):
    return ExpressionLog(arg)

class ExpressionLog(Expression):

    def __init__(self, expr):
        self.expr = expr
        if type(expr) == Data:
            self.symbols = [expr.symbol]
        else:
            self.symbols = symbols

    def get_sympy_expr(self):
        return log(self.expr.get_sympy_expr())

def GPSin(arg):
    return ExpressionSin(arg)

class ExpressionSin(Expression):

    def __init__(self, expr):
        self.expr = expr
        if type(expr) == Data:
            self.symbols = [expr.symbol]
        else:
            self.symbols = symbols

    def get_sympy_expr(self):
        return sin(self.expression)
