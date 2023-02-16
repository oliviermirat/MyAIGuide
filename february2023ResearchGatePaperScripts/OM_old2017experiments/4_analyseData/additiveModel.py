import matplotlib.pyplot as plt
import numpy as np
import pandas
from sklearn import preprocessing


def putLegend():
    leg = plt.legend(loc="upper center", fontsize=9)
    if leg:
        leg.draggable()


def minMaxScaler(tab):
    minn = min(tab)
    maxx = max(tab)
    if maxx - minn > 0:
        return (tab - minn) / (maxx - minn)
    else:
        return tab


def addLowLevel(data, low):
    data = data + low
    data = data / (1 + low)
    return data


def minMaxScalerRelative(tab, wind):
    minn = pandas.rolling_min(tab, wind)
    maxx = pandas.rolling_max(tab, wind)
    minn[0 : wind - 1] = minn[wind]
    maxx[0 : wind - 1] = maxx[wind]
    norm = maxx - minn
    return (tab - minn) / norm


def rotate(tab, num):
    n = len(tab)
    tab2 = tab[:]
    tab2[num:n] = tab[0 : n - num]
    tab2[0:num] = tab[n - num : n]
    return tab2


def additiveModel(
    sympNum,
    enviInfo,
    labels,
    symptoms,
    environment,
    xaxis,
    averagingwindow,
    show=0,
    relativeScaler=0,
):
    plt.subplot(3, 1, 1)
    if relativeScaler:
        sympt = minMaxScalerRelative(symptoms[:, sympNum], relativeScaler)
    else:
        sympt = minMaxScaler(symptoms[:, sympNum])
        sympt = addLowLevel(sympt, 0.1)
    plt.plot(xaxis, sympt, label=labels[0])
    zeros = np.zeros((len(symptoms), 5))
    envir = zeros[:, 0]
    for idx, info in enumerate(enviInfo):
        numCol = info[0]
        coeff = info[1]
        curEnv = minMaxScaler(environment[:, numCol])
        curEnv = addLowLevel(curEnv, 0.1)
        plt.plot(xaxis, curEnv, label=labels[1 + idx])
        print(
            labels[1 + idx], "max: ", max(environment[:, numCol]), " ; coeff: ", coeff
        )
        envir += coeff * curEnv
    putLegend()

    plt.subplot(3, 1, 2)
    symptsave = sympt[0 : averagingwindow - 1]
    envirsave = envir[0 : averagingwindow - 1]
    sympt = pandas.rolling_mean(sympt, averagingwindow)
    envir = pandas.rolling_mean(envir, averagingwindow)
    sympt[0 : averagingwindow - 1] = symptsave
    envir[0 : averagingwindow - 1] = envirsave
    sympt = minMaxScaler(sympt)
    envir = minMaxScaler(envir)
    plt.plot(xaxis, sympt, label="symptom")
    plt.plot(xaxis, envir, label="environment")
    putLegend()

    plt.subplot(3, 1, 3)
    # x=sympt[averagingwindow-1:len(sympt)]
    # y=envir[averagingwindow-1:len(envir)]
    x = sympt
    y = envir
    corr = np.correlate(x, np.hstack((y[1:], y)), mode="valid")
    # corr=np.correlate(x,y,"full")
    # shift=int(np.argmax(corr[0:100]))
    shift = int(np.argmax(corr[0:15]))
    plt.plot(corr)
    print(shift, corr[shift])
    print(np.corrcoef(x, y))
    print(np.corrcoef(x, rotate(y, shift)))
    # print(np.corrcoef(preprocessing.scale(x),preprocessing.scale(rotate(y,shift))))
    plt.show()

    return [shift, corr[shift]]
