import pickle
import numpy as np
import csv
import datetime
import pandas as pd
import os, os.path
import re

# Creation of the dataframe where everything will be stored
i = pd.date_range('2015-11-19', periods=1550, freq='1D')
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {'basisPeakSteps': empty, 'steps': empty, 'denivelation': empty, 'kneePain': empty, 'handsAndFingerPain': empty, 'foreheadAndEyesPain': empty, 'forearmElbowPain': empty, 'aroundEyesPain': empty, 'shoulderNeckPain': empty, 'painthreshold': np.full((sLength),3.4), 'whatPulseKeysC1': empty, 'whatPulseClicksC1': empty, 'manicTimeC1': empty, 'whatPulseKeysC2': empty, 'whatPulseClicksC2': empty, 'manicTimeC2': empty, 'whatPulseKeysC3': empty, 'whatPulseClicksC3': empty, 'manicTimeC3': empty, 'whatPulseKeysT': empty, 'whatPulseClicksT': empty, 'whatPulseT': empty, 'manicTimeT': empty, 'walk': empty, 'roadBike': empty, 'mountainBike': empty, 'swimming': empty, 'surfing': empty, 'climbing': empty, 'viaFerrata': empty, 'alpiSki': empty, 'downSki': empty, 'eyeRelatedActivities': empty, }
data = pd.DataFrame(data=d, index=i)

# Storing BasisPeak data in dataframe
if False: # This step takes a long time, put to False if you want to skip it, and to True otherwise
  filename = '../MonsterMizerOpenData/Participant1PublicOM/bodymetrics.csv'
  with open(filename, newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
      count=count+1
      if (count>2 and len(row)):
        date  = row[0][0:10]
        data.loc[date,'basisPeakSteps'] = data.loc[date,'basisPeakSteps'] + int(row[5])
        if count % 10000 == 0:
          print(count,'lines done out of the 532 330 needed for the basis peak')

# Storing fitbit data in dataframe
directory = os.fsencode('../MonsterMizerOpenData/Participant1PublicOM/dailyFitBitPerMonth/')
for file in os.listdir(directory):
  name = os.fsdecode(file)
  if name.endswith(".csv"): 
    filename = '../MonsterMizerOpenData/Participant1PublicOM/dailyFitBitPerMonth/'+name
    with open(filename, newline='') as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
        count=count+1
        if (count>2 and len(row)):
          day   = row[0][0:2]
          month = row[0][3:5]
          year  = row[0][6:10]
          date  = year+'-'+month+'-'+day
          data.loc[date,'steps']        = int(row[2].replace(',',''))
          data.loc[date,'denivelation'] = int(row[4])

# Storing pain intensities in dataframe
filename = '../MonsterMizerOpenData/Participant1PublicOM/pain.csv'
curYear  = ''
curMonth = ''
curDay   = ''
with open(filename, newline='') as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count=count+1
    if (count>2 and len(row)):
      if len(row[0]):
        curYear  = row[0]
      if len(row[1]):
        curMonth = row[1]
        if len(curMonth) == 1:
          curMonth = '0'+curMonth
      if len(row[2]):
        curDay   = row[2]
        if len(curDay) == 1:
          curDay = '0'+curDay
      date = curYear+'-'+curMonth+'-'+curDay
      dict = {'Knees' : 'kneePain',
              'Hands And Fingers' : 'handsAndFingerPain',
              'Forehead and Eyes' : 'foreheadAndEyesPain',
              'Forearm close to elbow' : 'forearmElbowPain',
              'Eyes (or around them)' : 'aroundEyesPain',
              'Shoulder Neck' : 'shoulderNeckPain'}
      if (row[3] in dict):
        data.loc[date,dict[row[3]]] = float(row[5])
        
# Storing whatPulse data in dataFrame
for num in ['1','2','3']:
  nbFiles = len([name for name in os.listdir('../MonsterMizerOpenData/Participant1PublicOM/computerUsage/computer'+num+'/whatPulse/') if os.path.isfile(os.path.join('data/computerUsage/computer'+num+'/whatPulse/', name))])
  for i in range(1,nbFiles+1):
    filename = '../MonsterMizerOpenData/Participant1PublicOM/computerUsage/computer'+num+'/whatPulse/whatpulse-input-history'+str(i)+'.csv'
    with open(filename, newline='') as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
        count=count+1
        if (count>1 and len(row)):
          date  = row[0][0:10]
          data.loc[date,'whatPulseKeysC'+num] = int(row[1])
          data.loc[date,'whatPulseClicksC'+num] = int(row[2])
data['whatPulseKeysT'] = data['whatPulseKeysC1'] + data['whatPulseKeysC2'] + data['whatPulseKeysC3']
data['whatPulseClicksT'] = data['whatPulseClicksC1'] + data['whatPulseClicksC2'] + data['whatPulseClicksC3']
data['whatPulseT'] = data['whatPulseKeysT'] + data['whatPulseClicksT']

# Storing Manic Time data in dataFrame
for num in ['1','2','3']:
  filename = '../MonsterMizerOpenData/Participant1PublicOM/computerUsage/computer'+num+'/manicTime/manicTime.csv'
  with open(filename, newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
      count=count+1
      if (count>1 and len(row)):
        if row[0][0:4] == "Acti":
          if num == '1':
            day   = row[1][0:2]
            month = row[1][3:5]
            year  = row[1][6:10]
          else:
            delimit = [m.start() for m in re.finditer('/', row[1])]
            month = row[1][0:delimit[0]]
            day   = row[1][delimit[0]+1:delimit[1]]
            if len(month)==1:
              month = '0' + month
            if len(day)==1:
              day = '0' + day
            year  = row[1][delimit[1]+1:delimit[1]+5]
          date  = year+'-'+month+'-'+day
          hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
          data.loc[date,'manicTimeC'+num] = data.loc[date,'manicTimeC'+num] + hours
data['manicTimeT'] = data['manicTimeC1'] + data['manicTimeC2'] + data['manicTimeC3']

# Storing Sport data in dataframe
filename = '../MonsterMizerOpenData/Participant1PublicOM/sport.csv'
curYear  = ''
curMonth = ''
curDay   = ''
with open(filename, newline='') as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count=count+1
    if (count>1 and len(row)):
      if len(row[0]):
        curYear  = row[0]
      if len(row[1]):
        curMonth = row[1]
        if len(curMonth) == 1:
          curMonth = '0'+curMonth
      if len(row[2]):
        curDay   = row[2]
        if len(curDay) == 1:
          curDay = '0'+curDay
      date = curYear+'-'+curMonth+'-'+curDay
      dict = {'Walk' : 'walk',
              'Road Bike' : 'roadBike',
              'Mt Bike' : 'mountainBike',
              'Swimming' : 'swimming',
              'Surfing' : 'surfing',
              'Climbing' : 'climbing',
              'Via Ferrata' : 'viaFerrata',
              'Alpi Ski' : 'alpiSki',
              'Down Ski' : 'downSki'}
      if (row[3] in dict):
        data.loc[date,dict[row[3]]] = 1

# Storing Eye related activity hours in dataframe
filename = '../MonsterMizerOpenData/Participant1PublicOM/eyeRelatedActivities.csv'
curYear  = ''
curMonth = ''
curDay   = ''
with open(filename, newline='') as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count=count+1
    if (count>2 and len(row)):
      if len(row[0]):
        curYear  = row[0]
      if len(row[1]):
        curMonth = row[1]
        if len(curMonth) == 1:
          curMonth = '0'+curMonth
      if len(row[2]):
        curDay   = row[2]
        if len(curDay) == 1:
          curDay = '0'+curDay
      date = curYear+'-'+curMonth+'-'+curDay
      tot = 0
      if len(row[3]):
        tot = tot + int(row[3])
      if len(row[4]):
        tot = tot + int(row[4])
      if len(row[5]):
        tot = tot + int(row[5])
      if len(row[6]):
        tot = tot + int(row[6])
      data.loc[date,'eyeRelatedActivities'] = tot

# Saving the dataframe in a txt
output = open('data.txt', 'wb')
pickle.dump(data, output)
output.close()
