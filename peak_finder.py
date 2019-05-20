
import sys
sys.path.append("../../GPLib")

from data import Data
from fitting import curve_fit

import numpy as np
from sympy import *
import matplotlib.pyplot as plt

from praktikum import analyse

def find_peaks(xs, ys, threshold=10, step_size=0.01):

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
        # fit parabels onto peaks to get errors on position and hight
        for (s, p, e) in peak_pos:
            if e - p < p-s:
                s = p - (e - p )
            elif s-p < e-p:
                e = p + (p - s)
            while e - s <= 7:
                s = s - 1
                e = e + 1

            sample_x = list()
            try:
                for i in [s + n for n in range(e - s)]:
                    u_c = ys.data[i]
                    while u_c < ys.data[i + 1] if i < p else ys.data[i] < u_c:
                        u_c = u_c + step_size
                        sample_x.append(xs.data[i])
            except IndexError:
                pass
            x_pos, x_pos_err = analyse.mittelwert_stdabw(sample_x)
            # xdata
            xr.append(x_pos)
            x_stat_err.append(x_pos_err / np.sqrt(e-s))
            x_sys_err.append(xs.uncert_sys[p])

        return (Data("x_pos", np.array(xr), np.array(x_stat_err), np.array(x_sys_err)))
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

def peak_height(xs, ys, x_peak, y_name ):
    data = list( zip( xs.data, xs.uncert_stat, xs.uncert_sys, ys.data, ys.uncert_stat, ys.uncert_sys ) )
    key = lambda x: abs(x[0] - x_peak.data)
    peak = min( *data, key=key )
    y_peak = Data( y_name, peak[3], peak[4], peak[5] )
    return (x_peak, y_peak)
