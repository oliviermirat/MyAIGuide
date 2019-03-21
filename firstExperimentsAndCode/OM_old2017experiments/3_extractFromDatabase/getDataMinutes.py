# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 10:55:58 2016

@author: Olivier
"""

import utilities as ut

class basisByMinutes(ut.getData):
    def sql(self,db,data,startLin,endLin,param):
        
        result = db.query('SELECT steps,calories,insttime FROM basis WHERE' +
                          ' insttime>' + startLin + ' AND insttime<' + endLin)

        ut.initialiseData(data,['steps','calories'])
        
        for row in result:
            vals=[ ['steps'  ,row['steps']] ,
                   ['calories',row['calories']] ]
                       
            ut.fillData(data,
                     row['insttime'],
                     vals)


class sportsTimeIntervalles(ut.getData):
    def sql(self,db,data,startLin,endLin,param):

        print('\nSports:')
        
        result= db.query('SELECT starttime,endtime,activity FROM sports' +
              ' WHERE starttime>' + startLin + ' AND endtime<' + endLin)
              
        ut.initialiseData(data,['active'])
              
        for row in result:
            ut.fillData(data,row['starttime']-1, [['active',0]] )
            ut.fillData(data,row['starttime']  , [['active',param]] )
            ut.fillData(data,row['endtime']    , [['active',param]] )
            ut.fillData(data,row['endtime']+1  , [['active',0]] )
            print(row['activity'])


class manicTimeIntervalles(ut.getData):
    def sql(self,db,data,startLin,endLin,param):
        
        result = db.query("SELECT starttime,endtime FROM manicTime WHERE" +
                   " name='ActivitÃ©' AND" +
                   " starttime>" + startLin + " AND endtime<" + endLin)
              
        ut.initialiseData(data,['active'])
              
        for row in result:
            ut.fillData(data,row['starttime']-1, [['active',0]] )
            ut.fillData(data,row['starttime']  , [['active',param]] )
            ut.fillData(data,row['endtime']    , [['active',param]] )
            ut.fillData(data,row['endtime']+1  , [['active',0]] )
