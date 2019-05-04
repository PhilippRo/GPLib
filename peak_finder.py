
import sys
sys.path.append("../../GPLib")

from data import Data
from fitting import curve_fit

import numpy as np
from sympy import *
import matplotlib.pyplot as plt

def find_peaks(xs, ys, threshold=10):

    def find_peak_location(xs, ys):
        res =list()
        max_idx = len(xs.data) - 1
        c_i = 0
        # in case a first edge exsists falling edge
        while max_idx > c_i and ys[c_i + 1] < ys[c_i]:
            c_i = c_i + 1
        while c_i < max_idx:
            # rising edge
            start_idx = c_i
            while max_idx > c_i and ys[c_i + 1] >= ys[c_i]:
                c_i = c_i +1
            pos_idx = c_i
            #falling edge
            while max_idx > c_i and ys[c_i + 1] < ys[c_i]:
                c_i = c_i + 1
            end_idx = c_i
            res.append((start_idx, pos_idx, end_idx))
        return res

    def get_error(peak_pos):
        xr, x_stat_err, x_sys_err, yr, y_stat_err, y_sys_err = (list(), list(),
            list(), list(), list(), list())
        x, width, xpos, height = symbols("x a d c")
        y_of_x = width * (x - xpos)**2 + height
        # fit parabels onto peaks to get errors on position and hight
        for (s, p, e) in peak_pos:
            if e - p < p-s:
                s = p - (e - p )
            elif s-p < e-p:
                e = p + (p - s)
            while e - s <= 5:
                s = s - 1
                e = e + 1

            lxs = Data("x", xs.data[s:e])
            lys = Data("y", ys.data[s:e], ys.uncert_stat[s:e], xs.uncert_sys[s:e])
            print(ys.uncert_stat[s:e])
            fit_res = curve_fit(lxs, lys, (y_of_x, [x, width, xpos, height]),
                [(ys.data[p + 1] - ys.data[p])/(xs.data[p+1] - xs.data[p])**2,
                    xs.data[p], ys.data[p]])
            # xdata
            xr.append(fit_res.paras[1])
            x_stat_err.append(fit_res.p_cov[1][1])
            x_sys_err.append(xs.uncert_sys[p])

            # ydata
            yr.append(fit_res.paras[2])
            y_stat_err.append(fit_res.p_cov[2][2])
            y_sys_err.append(ys.uncert_sys[p])

        return (Data("x_pos", np.array(xr), np.array(x_stat_err), np.array(x_sys_err)),
                Data("peak_hight", np.array(yr), np.array(y_stat_err), np.array(y_sys_err)))
        return xr
    if type(xs) != Data or type(ys) != Data:
        raise ValueError("xs and ys need to be Data objects")
    if len(xs.data) != len(ys.data):
        raise ValueError("xs and ys need to have same length")

    #filter peaks
    npeaks = list()
    peaks = find_peak_location(xs.data, ys.data)
    while len([  1    for (_, p1, _) in peaks
                for (_, p2, _) in peaks
                if abs(p1 - p2) < threshold and p1 != p2])!= 0:
        (a, pos, b) = max(peaks, key = lambda x: ys.data[x[1]])
        peaks = [p for p in peaks if abs(p[1] - pos) > threshold]
        weed_out = [p for p in peaks if abs(p[1] -pos) < threshold]
        weed_out.append((a, pos, b))
        npeaks.append((min(weed_out, key=lambda x:x[0])[0],
                pos,
                max(weed_out, key = lambda x: x[2])[2] ))

    return get_error(npeaks)
