# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 17:12:33 2016

@author: Olivier
"""

import datetime
import time

import dataset


class getData:
    def sql(self, db, data, startLin, endLin, param):
        pass

    def getData(self, info, param=[]):
        [db, startLin, endLin] = info
        data = {}
        self.sql(db, data, startLin, endLin, param)
        return data


def returnParam(param, column):
    if not (type(param) is str):
        param2 = ""
        n = len(param) - 1
        for idx, p in enumerate(param):
            if idx == 0:
                param2 = p + '" OR ' + column + '="'
            if (idx != 0) & (idx != n):
                param2 = param2 + p + '" OR ' + column + '="'
            if idx == n:
                param2 = param2 + p
        return param2
    else:
        return param


def toLinuxTime(s, formatTime):
    t = time.mktime(datetime.datetime.strptime(s, formatTime).timetuple())
    return t


def toDatetime(s):
    ye = int(datetime.datetime.fromtimestamp(s).strftime("%Y"))
    mo = int(datetime.datetime.fromtimestamp(s).strftime("%m"))
    da = int(datetime.datetime.fromtimestamp(s).strftime("%d"))
    ho = int(datetime.datetime.fromtimestamp(s).strftime("%H"))
    mi = int(datetime.datetime.fromtimestamp(s).strftime("%M"))
    se = int(datetime.datetime.fromtimestamp(s).strftime("%S"))
    t = datetime.datetime(ye, mo, da, ho, mi, se)
    return t


def getDbStartEnd(start, end):
    db = dataset.connect("sqlite:///../2_createAndFillDatabase/olidata.db")

    startLin = str(toLinuxTime(start, "%Y/%m/%d %H:%M"))
    endLin = str(toLinuxTime(end, "%Y/%m/%d %H:%M"))

    return [db, startLin, endLin]


def initialiseData(data, entries):
    data["unixtime"] = []
    data["datetime"] = []
    for idx, val in enumerate(entries):
        data[val] = []


def fillData(m, x, y):
    m["unixtime"].append(x)
    m["datetime"].append(toDatetime((x)))
    for idx, entry in enumerate(y):
        m[entry[0]].append(entry[1])
