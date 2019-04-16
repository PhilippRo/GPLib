
from sympy import *

class Data:

    def __init__(self, symbol ,data, uncert_stat, uncert_sys):
        self.data = data
        self.uncert_stat = uncert_stat
        self.uncert_sys = uncert_sys
        if len(self.symbol.split(" ")) == 1:
            self.symbol = symbols(symbol)
        else:
            raise ValueError("Symbol string may not contain spaces")

    def __add__

class Expression():

    def unite_symbols(self, lhs, rhs):
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
        ExpressionPow(self, rhs):



class ExpressionAdd(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs



class ExpressionSub(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs



class ExpressionMul(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs



class ExpressionDiv(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs



class ExpressionPow(Expression):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs




