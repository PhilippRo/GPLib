import numpy as np
import sympy
from data import Data
from data import Expression
from scipy.optimize import curve_fit as scipy_curve_fit

class CurveFitResult:

    def __init__(self, xs, ys,
            x_err_stat, y_err_stat,
            x_err_sys, y_err_sys,
            func, paras, p_cov,
            chi_q, blacklist ) :
        self.xs = xs
        self.ys = ys
        self.x_err_stat = x_err_stat
        self.y_err_stat = y_err_stat
        self.x_err_sys = x_err_sys
        self.x_err_sys = x_err_sys
        self.func = func
        self.paras = paras
        self.p_cov = p_cov
        self.chi_q = chi_q
        self.blacklist = blacklist

    def __str__(self):
        out = "CurveFitResult(\n"
        out += "\tFunction: {}\n".format(self.func[0])
        out += "\tParas:\n"
        for i in range(len(self.paras)) :
            out += "\t\t{} = {}\n".format( self.func[1][i+1], self.paras[i] )
        out += "\tCovariance:\n{}\n".format(self.p_cov)
        out += "\tChi^2 = {}".format(self.chi_q)
        return out

# func is tuple of sympy expression and array of corresponding sympy symbols. First symbol should be x
def curve_fit( xs, ys, func, p0 = None ):
    if isinstance( xs, Data ) :
        xs = Expression(xs)
    x_data = xs.consume('x')
    if isinstance( ys, Data ) :
        ys = Expression(ys)
    y_data = ys.consume('y')

    if not (x_data.uncert_stat == 0).all :
        raise ValueError("x_data cannot have stat. uncertainty")
    if not (x_data.uncert_sys == 0).all :
        raise ValueError("x_data cannot have sys. uncertainty")

    func_expr = func[0]
    func_symbols = func[1]
    func_lam = sympy.lambdify( func_symbols, func_expr )

    x_sym = func_symbols[0]
    par_sym = func_symbols[1:]

    jac_expr = sympy.Matrix([func_expr]).jacobian(par_sym)
    jac_func = sympy.lambdify( [x_sym, *par_sym], jac_expr )

    sigma = np.diag( y_data.uncert_stat**2 )
    s = []
    for si in y_data.uncert_sys :
        s.append([])
        for sj in y_data.uncert_sys :
            s[-1].append(si*sj)
    sigma += np.asarray(s)

    paras, p_cov = scipy_curve_fit( func_lam, x_data.data, y_data.data, p0=p0, sigma=sigma  )

    r = y_data.data - func_lam( x_data.data, *paras )
    chi_q = r.T @ np.linalg.inv(sigma) @ r

    return CurveFitResult( x_data.data, y_data.data,
            x_data.uncert_stat, y_data.uncert_stat,
            x_data.uncert_sys, y_data.uncert_sys,
            func, paras, p_cov,
            chi_q, x_data.blacklist + y_data.blacklist )
