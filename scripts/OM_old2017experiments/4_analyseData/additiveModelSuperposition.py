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
    averagingwindow2,
    averagingwindowBig,
    sympThres,
    showw=1,
    relativeScaler=0,
):

    thresh = 0.25
    # sympThres=3.6

    plt.subplot(4, 1, 1)
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
        envir += coeff * curEnv
    putLegend()

    accumulEnvir = np.zeros(len(envir))
    for i in range(0, averagingwindow):
        accumulEnvir[i] = np.average(envir[0 : averagingwindow - 1])  # envir[i]
    for i in range(averagingwindow, len(envir)):
        accumulEnvir[i] = np.average(
            envir[i - averagingwindow : i]
        )  # + 0.1*envir[i]+0.03*envir[i-1]

    accumulEnvir2 = np.zeros(len(envir))
    for i in range(0, averagingwindow2):
        accumulEnvir2[i] = np.average(envir[0 : averagingwindow2 - 1])  # envir[i]
    for i in range(averagingwindow2, len(envir)):
        accumulEnvir2[i] = np.average(
            envir[i - averagingwindow2 : i]
        )  # + 0.1*envir[i]+0.03*envir[i-1]

    accumulEnvirBig = np.zeros(len(envir))
    for i in range(0, averagingwindowBig):
        accumulEnvirBig[i] = np.average(
            envir[0 : averagingwindowBig - 1]
        )  # - (averagingwindowBig-i)*(0.06/averagingwindowBig) # envir[i]
    for i in range(averagingwindowBig, len(envir)):
        accumulEnvirBig[i] = np.average(envir[i - averagingwindowBig : i])

    moySympt = np.zeros(len(envir))
    for i in range(0, averagingwindowBig):
        moySympt[i] = np.average(
            symptoms[0 : averagingwindowBig - 1, sympNum]
        )  # - (averagingwindowBig-i)*(0.06/averagingwindowBig) # envir[i]
    for i in range(averagingwindowBig, len(envir)):
        moySympt[i] = np.average(symptoms[i - averagingwindowBig : i, sympNum])

    plt.subplot(4, 1, 2)
    difference = accumulEnvir - accumulEnvirBig
    for i in range(0, len(difference)):
        if difference[i] < 0:
            difference[i] = 0
        else:
            difference[i] = (difference[i]) / (
                accumulEnvirBig[i] / moySympt[i]
            )  # np.exp(0.00001*accumulEnvirBig[i])

    difference2 = accumulEnvir2 - accumulEnvirBig
    for i in range(0, len(difference2)):
        if difference2[i] < 0:
            difference2[i] = 0
        else:
            difference2[i] = (difference2[i]) / (
                accumulEnvirBig[i] / moySympt[i]
            )  # np.exp(0.00001*accumulEnvirBig[i])
    difference2 = difference2

    difference2[0] = difference2[1]
    max1 = np.max(difference)
    max2 = np.max(difference2)
    if max2 > max1:
        difference2 = difference2 * (max1 / max2)
    else:
        difference = difference * (max2 / max1)

    # Acumulated activity compared to average activity

    plt.plot(xaxis, difference, label="For last 20 days")
    plt.plot(xaxis, difference2, label="For previous day")

    maxDiff = np.zeros(len(difference))
    for i in range(0, len(difference)):
        maxDiff[i] = max(difference[i], difference2[i])
    plt.plot(xaxis, maxDiff, label="Max of 2 previous")

    putLegend()

    # plt.subplot(4,1,2)
    # plt.plot(xaxis,symptoms[:,sympNum],label='symptom')
    symptomsAverage = pandas.rolling_mean(symptoms[:, sympNum], 3)
    # plt.plot(xaxis,symptomsAverage,label='symptomAverage')
    # flat = np.zeros(len(symptoms[:,sympNum]))
    # for i in range(0,len(flat)):
    # flat[i] = sympThres
    # plt.plot(xaxis,flat,label='flat')
    # putLegend()

    plt.subplot(4, 1, 3)
    symptomsAverage[0] = symptomsAverage[2]
    symptomsAverage[1] = symptomsAverage[2]
    plt.plot(xaxis, minMaxScaler(maxDiff), label="Activity")
    plt.plot(xaxis, minMaxScaler(symptoms[:, sympNum]), label="Symptom")
    putLegend()

    plt.subplot(4, 1, 4)
    symptomsAverage[0] = symptomsAverage[2]
    symptomsAverage[1] = symptomsAverage[2]
    plt.plot(
        xaxis, pandas.rolling_mean(minMaxScaler(maxDiff), 7), label="Activity Averaged"
    )
    plt.plot(
        xaxis,
        pandas.rolling_mean(minMaxScaler(symptomsAverage), 7),
        label="Symptom Averaged",
    )
    putLegend()

    if showw == 1:
        plt.show()

    symptReturn = symptoms[:, sympNum]
    enviReturn = accumulEnvir

    return [symptReturn, enviReturn]
