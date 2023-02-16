# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 09:49:48 2016

@author: Olivier
"""

import sys

import getDataMinutes as gm
import matplotlib.pyplot as plt
import utilities as ut

sys.path.insert(0, "../3_extractFromDatabase")


start = "2016/01/01 00:00"
end = "2016/12/29 23:59"
# start = '2016/07/15 00:00'
# end = '2016/09/05 23:59'


def keepMax(data, maxtofind):
    datetime = data["datetime"]
    val = data[maxtofind]
    n = len(datetime) - 1
    toRemove = []
    for idx, p in enumerate(datetime):
        if idx != n:
            if datetime[idx] == datetime[idx + 1]:
                if val[idx] > val[idx + 1]:
                    toRemove.append(idx + 1)
                else:
                    toRemove.append(idx)
    m = len(toRemove)
    for i in range(1, m + 1):
        rem = toRemove[m - i]
        for j in data:
            del data[j][rem]


def plotExpected(data, y, num=111, show=1):
    plt.subplot(num)
    plt.plot(data["datetime"], data[y])
    if show:
        plt.show()


def plotBarExpected(data, y, num=111, show=1):
    ax = plt.subplot(num)
    ax.bar(data["datetime"], data[y], width=1)
    ax.xaxis_date()
    if show:
        plt.show()


info = ut.getDbStartEnd(start, end)

basisByMinutes = gm.basisByMinutes()
data7 = basisByMinutes.getData(info)

sportsTimeIntervalles = gm.sportsTimeIntervalles()
data8 = sportsTimeIntervalles.getData(info, -5)

manicTimeIntervalles = gm.manicTimeIntervalles()
data9 = manicTimeIntervalles.getData(info, -5)


plotExpected(data7, "steps", 111, 0)
plotExpected(data7, "calories", 111, 0)
plotExpected(data8, "active", 111, 0)
plotExpected(data9, "active")
