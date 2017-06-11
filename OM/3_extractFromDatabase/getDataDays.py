# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 10:55:58 2016

@author: Olivier
"""

import utilities as ut
import math

class painByLocation(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        param=ut.returnParam(param,'location')

        result = db.query('SELECT starttime,endtime,intensity ' +
                          'FROM pain WHERE (location="' +param+'") AND '+
                          ' starttime>=' + startLin + ' AND endtime<=' + endLin)

        ut.initialiseData(data,['intensity'])

        for row in result:
            ut.fillData(data,
                        (row['starttime']+row['endtime'])/2,
                         [['intensity',row['intensity']]])


class sportDurByAct(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        param=ut.returnParam(param,'activity')

        result= db.query('SELECT starttime,endtime,activity FROM sports' +
              ' WHERE (activity="'+ param +'") AND starttime>' + startLin +
              ' AND endtime<' + endLin)

        ut.initialiseData(data,['duration'])

        for row in result:
            ut.fillData(data,
                        math.floor((row['starttime'])/86400)*86400+43200,
                        [['duration',row['endtime']-row['starttime']]])


class climbViaIntensity(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result= db.query('SELECT starttime,endtime,effortInt FROM sports' +
              ' WHERE (activity="Via Ferrata" OR activity="Climbing") '+
              'AND starttime>' + startLin + ' AND endtime<' + endLin)

        ut.initialiseData(data,['effortInt'])

        for row in result:
            ut.fillData(data,
                        math.floor(row['starttime']/86400)*86400+43200,
                        [['effortInt',row['effortInt']]])


class manicTimePerDay(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result = db.query("SELECT starttime,(starttime)/86400,"+
        "sum(endtime-starttime) FROM manicTime WHERE name='ActivitÃ©' "+
        "AND starttime>"+startLin+" AND endtime<"+endLin+
        " GROUP BY ((starttime)/86400)")

        ut.initialiseData(data,['duration'])

        for row in result:
            ut.fillData(data,
                     row['(starttime)/86400']*86400+86400/2,
                     [['duration',
                      row['sum(endtime-starttime)']]])

class whatPulsePerDay(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result = db.query("SELECT starttime,(starttime)/86400,keys,clicks "+
        "FROM whatPulse WHERE "+
        "starttime>"+startLin+" AND endtime<"+endLin+
        " AND id IN (SELECT max(id) FROM "+
        "whatPulse GROUP BY date)"
        )

        ut.initialiseData(data,['keys','clicks'])

        for row in result:
            vals=[ ['keys'  ,row['keys']] ,
                   ['clicks',row['clicks']] ]

            ut.fillData(data,
                    row['starttime']+86400/2+86400, # Should this be changed ??? #
                     vals)

class basisPerDay(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result = db.query("SELECT (insttime)/86400,"+
        "sum(steps),sum(calories) FROM basis WHERE "+
        " insttime>"+startLin+" AND insttime<"+endLin+
        " GROUP BY (insttime/86400)")

        ut.initialiseData(data,['steps','calories'])

        for row in result:
            vals=[ ['steps'  ,row['sum(steps)']] ,
                   ['calories',row['sum(calories)']] ]

            ut.fillData(data,
                     row['(insttime)/86400']*86400+86400/2,
                     vals)

class sportBasisByAct(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        param=ut.returnParam(param,'activity')

        result = db.query('SELECT starttime,endtime,activity,'+
        'sum(calories),sum(steps) '+
        'FROM sports s INNER JOIN basis b '
        'ON b.insttime>=s.starttime AND b.insttime<=s.endtime '
        'WHERE (activity="'+ param +'") AND starttime>'+startLin+
        ' AND endtime<'+endLin+' GROUP BY starttime')

        ut.initialiseData(data,['steps','calories'])

        for row in result:
            vals=[ ['steps'  ,row['sum(steps)']] ,
                   ['calories',row['sum(calories)']] ]

            ut.fillData(data,
                     math.floor((row['starttime'])/86400)*86400+43200,
                     vals)


class general(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result= db.query('SELECT stress,mood,socquant,weight,starttime FROM general' +
              ' WHERE starttime>' + startLin +' AND endtime<' + endLin)

        ut.initialiseData(data,['stress','mood','socquant','weight'])

        for row in result:

            vals=[ ['stress'   , row['stress']] ,
                   ['mood'    , row['mood']],
                   ['socquant', row['socquant']],
                   ['weight'  , row['weight']] ]

            ut.fillData(data,math.floor((row['starttime']+43200)/86400)*86400+43200,vals)

class generalAct(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result= db.query('SELECT paper,ubuntu,driving,ridingcar,store,starttime '+
          'FROM generalactivities WHERE starttime>' + startLin +
          ' AND endtime<' + endLin)

        ut.initialiseData(data,['paper','ubuntu','driving','store','ridingcar'])

        for row in result:

            vals=[ ['paper'    , row['paper']] ,
                   ['ubuntu'   , row['ubuntu']],
                   ['driving'  , row['driving']],
                   ['store'    , row['store']],
                   ['ridingcar', row['ridingcar']]]

            ut.fillData(data,math.floor((row['starttime']+43200)/86400)*86400+43200,vals)

class painStats(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        result = db.query('SELECT starttime,endtime,avg(intensity),max(intensity) ' +
                          'FROM pain WHERE '+
                          ' starttime>=' + startLin + ' AND endtime<=' + endLin+
                          ' GROUP BY starttime')

        ut.initialiseData(data,['meanIntensity','maxIntensity'])

        for row in result:
            vals=[ ['meanIntensity', row['avg(intensity)']] ,
                   ['maxIntensity' , row['max(intensity)']] ]
            ut.fillData(data, (row['starttime']+row['endtime'])/2, vals)
