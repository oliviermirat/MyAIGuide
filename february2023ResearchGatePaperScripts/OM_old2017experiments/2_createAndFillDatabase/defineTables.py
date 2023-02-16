# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 18:05:41 2016

@author: Olivier
"""

import numpy as np


class basisTab:
    m = np.array(
        [
            ["date", 0, "varchar", 1],
            ["calories", 0, "int", 0],
            ["gsr", 0, "int", 0],
            ["hearrate", 0, "int", 0],
            ["skintemp", 0, "int", 0],
            ["steps", 0, "int", 0],
            ["insttime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y-%m-%d %H:%MZ"]
    timeShift = 0
    tableName = "basis"
    linesToSkip = 1
    maxcolumns = 6


class painTab:
    m = np.array(
        [
            ["year", 1, "int", 1],
            ["month", 1, "int", 1],
            ["day", 1, "int", 1],
            ["location", 0, "varchar", 0],
            ["side", 0, "varchar", 0],
            ["intensity", 0, "int", 0],
            ["comment", 0, "varchar", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y/%m/%d", "0"]
    timeShift = 86400
    tableName = "pain"
    linesToSkip = 2
    maxcolumns = 7


class sportTab:
    m = np.array(
        [
            ["year", 1, "int", 1],
            ["month", 1, "int", 1],
            ["day", 1, "int", 1],
            ["activity", 0, "varchar", 0],
            ["start", 0, "varchar", 0],
            ["duration", 0, "varchar", 0],
            ["km", 0, "varchar", 0],
            ["denivelation", 0, "int", 0],
            ["appdur", 0, "int", 0],
            ["appden", 0, "int", 0],
            ["painafter", 0, "int", 0],
            ["inreg", 0, "varchar", 0],
            ["side", 0, "varchar", 0],
            ["effortInt", 0, "int", 0],
            #                ['other',0,'varchar',0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y/%m/%d", "0"]
    timeShift = 86400
    tableName = "sports"
    linesToSkip = 1
    maxcolumns = 14


class manicTimeTab:
    m = np.array(
        [
            ["name", 0, "varchar", 0],
            ["start", 0, "varchar", 1],
            ["end", 0, "varchar", 2],
            ["duration", 0, "varchar", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
    timeShift = 0
    tableName = "manicTime"
    linesToSkip = 1
    maxcolumns = 4


class screenSaverTab:
    m = np.array(
        [
            ["name", 0, "varchar", 0],
            ["start", 0, "varchar", 1],
            ["end", 0, "varchar", 2],
            ["duration", 0, "varchar", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
    timeShift = 0
    tableName = "screenSaver"
    linesToSkip = 1
    maxcolumns = 4


class whatPulseTab:
    m = np.array(
        [
            ["date", 0, "varchar", 1],
            ["keys", 0, "int", 0],
            ["clicks", 0, "int", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y-%m-%d", "0"]
    timeShift = 86400
    tableName = "whatPulse"
    linesToSkip = 1
    maxcolumns = 3


class taplogTab:
    m = np.array(
        [
            ["ms", 0, "int", 0],
            ["timezoneoffset", 0, "int", 0],
            ["timestamp", 0, "varchar", 0],
            ["dayofyear", 0, "int", 0],
            ["dayofmonth", 0, "int", 0],
            ["dayofweek", 0, "varchar", 0],
            ["timeofday", 0, "int", 0],
            ["idd", 0, "int", 0],
            ["cat1", 0, "varchar", 0],
            ["cat2", 0, "varchar", 0],
            ["insttime", 0, "int", 0],
        ]
    )
    timeFormat = ["0"]
    timeShift = 0
    tableName = "taplog"
    linesToSkip = 1
    maxcolumns = 10


class general:
    m = np.array(
        [
            ["year", 1, "int", 1],
            ["month", 1, "int", 1],
            ["day", 1, "int", 1],
            ["stress", 1, "int", 0],
            ["mood", 1, "int", 0],
            ["socquant", 1, "varchar", 0],
            ["socqual", 1, "varchar", 0],
            ["weight", 1, "int", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y/%m/%d", "0"]
    timeShift = 86400
    tableName = "general"
    linesToSkip = 2
    maxcolumns = 8


class generalActivities:
    m = np.array(
        [
            ["year", 1, "int", 1],
            ["month", 1, "int", 1],
            ["day", 1, "int", 1],
            ["paper", 0, "int", 0],
            ["ubuntu", 0, "int", 0],
            ["driving", 0, "int", 0],
            ["store", 0, "int", 0],
            ["ridingcar", 0, "int", 0],
            ["starttime", 0, "int", 0],
            ["endtime", 0, "int", 0],
        ]
    )
    timeFormat = ["%Y/%m/%d", "0"]
    timeShift = 86400
    tableName = "generalactivities"
    linesToSkip = 2
    maxcolumns = 8
