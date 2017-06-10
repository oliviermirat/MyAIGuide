# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 17:13:15 2016

@author: Olivier
"""

def printAllPains(info):
    db=info[0]
    startLin=info[1]
    endLin=info[2]

    print('')
    print('Pain:')
    result = db.query('SELECT year,month,day,location,intensity ' +
                      'FROM pain WHERE' +
                      ' starttime>=' + startLin + ' AND endtime<=' + endLin)
    for row in result:
        print(row['year'], row['month'], row['day'],
              row['location'], row['intensity'])

def printWhatPulse(info):
    db=info[0]
    startLin=info[1]
    endLin=info[2]

    print('')
    print('WhatPulse:')
    result4 = db.query('SELECT date,keys,clicks ' +
                       'FROM whatPulse WHERE' +
                       ' starttime>=' + startLin + ' AND endtime<=' + endLin)
    for row in result4:
        print(row['date'], row['keys'], row['clicks'])