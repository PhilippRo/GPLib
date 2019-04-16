from sympy import *
import numpy as np

#class Symbol:
    
# symbol ist das sympy symbol for Data
# data ist entweder eine list<Data> oder ein Wert (einschließlich unbesetzt)
# uncert ist die unsicherheit auf data als dict von sympy-symbol nach Wert oder list von uncerts

class Uncert:
    def __init__(self):
        self.dict = dict()

    #def __add__ (self, rhs):

        

class Data:

    def __add__(self, rhs) :
        if isinstance(self.data, list) :
            if isinstance(rhs.data, list) :
                result = []
                result_uncert = []
                for d in range(len(self.data)):
                    result.append( self.data[d] + rhs.data[d] )
                    result_uncert.append( self.uncert[d] + rhs.uncert[d] )
                return Expr( self.symbol + rhs.symbol, result,  result_uncert)
            else :
                raise ValueError("Error LHS and RHS dont have same depth")
        elif isinstance(rhs.data, list) :
            raise ValueError("Error LHS and RHS dont have same depth")
        else :
            new_data = []
            return Expr( self.symbol + rhs.symbol, self.data + rhs.data, self.uncert + self.uncert )

    def __index__(self, i) :
        if isinstance(self.data, list):
            return Expr( self.symbol, self.data[i], self.uncert[i].extend( self.data[i].uncert) )
        else :
            raise ValueError("Data doesnt contain substructure!")

    def get(self):
        return ( self.data, self.uncert )
            
class Raw(Data):
    def __init__(self, symbol, data, uncert):
        self.data = data
        self.uncert = uncert
        if len(symbol.split(" ")) == 1:
            self.symbol = symbols(symbol)
        else:
            raise ValueError("Symbol string may not contain spaces")

class Expr(Data):
    def __init__(self, symbol, data, uncert):
        self.data = data
        self.uncert = uncert
        self.symbol = symbol


d = Raw('d', [Raw('d', 1, 0.5), Raw('d', 2, 0.5), Raw('d', 3, 0.5)], [0.2,0.2,0.2])
print(type(d))
print(type(d.data))
print(type(d.data[0].data))

f = Raw('f', [Raw('f', 3, 1), Raw('d', 4, 0.5), Raw('d', 6, 0.5)], [0.2,0.2,0.2])
for e in (d + f).data:
    print("{}".format(e.data))
