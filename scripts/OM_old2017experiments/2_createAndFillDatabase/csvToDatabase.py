# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 16:26:55 2016

@author: Olivier
"""

import csv
import datetime
import time

import dataset


def toLinuxTime(s, formatTime):
    t = time.mktime(datetime.datetime.strptime(s, formatTime).timetuple())
    return t


def csvToDatabase(filename, tab):

    columns = tab.m
    timeFormat = tab.timeFormat
    timeShift = tab.timeShift
    tableName = tab.tableName
    linesToSkip = tab.linesToSkip
    maxcolumns = tab.maxcolumns

    count = 0
    times = [""] * len(columns)
    prevVals = [None] * len(columns)
    db = dataset.connect("sqlite:///olidata.db")
    valstot = ""
    cols = ", ".join(columns[:, 0])
    with open(filename, newline="") as csvfile:
        #        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            count = count + 1
            if count > linesToSkip:
                if count % 1000 == 0:
                    print(count)

                times[0] = ""
                times[1] = ""
                vals = ""
                for idx, val in enumerate(row):
                    if idx < maxcolumns:
                        if len(val) == 0:
                            if columns[idx, 1] == "1":
                                val = prevVals[idx]
                            else:
                                val = "0"
                        else:
                            prevVals[idx] = val
                        if val == None:
                            val = "0"
                        if columns[idx, 2] == "varchar":
                            vals = vals + '"' + val + '"' + ","
                        else:
                            vals = vals + val + ","
                        if columns[idx, 3] != "0":
                            ind = int(columns[idx, 3]) - 1
                            times[ind] = times[ind] + str(val) + "/"

                vals = vals[0 : len(vals) - 1]
                for idx, timeF in enumerate(timeFormat):
                    if timeF != "0":
                        time0 = times[idx]
                        time0 = time0[0 : len(time0) - 1]
                        time0 = toLinuxTime(time0, timeF)
                        times[idx] = time0
                    else:
                        if times[0] != "":
                            time0 = times[0] + timeShift
                        else:
                            time0 = timeShift
                    vals = vals + "," + str(time0)

                valstot = valstot + "(" + vals + "),"

                if count % 10000 == 0:
                    valstot = valstot[0 : len(valstot) - 1]
                    db.query(
                        "INSERT OR IGNORE INTO "
                        + tableName
                        + "("
                        + cols
                        + ") VALUES "
                        + valstot
                    )
                    valstot = ""

                "db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals+')')"

    if count % 10000 != 0:
        valstot = valstot[0 : len(valstot) - 1]
        db.query(
            "INSERT OR IGNORE INTO " + tableName + "(" + cols + ") VALUES " + valstot
        )
