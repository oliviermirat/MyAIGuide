import csv
import datetime
import pickle

import additiveModelSuperposition as addMod
import numpy as np

environment = np.zeros((273, 20))
symptoms = np.zeros((273, 1))

j = 0
for i in range(1, 10):
    filename = (
        "../1_initialRawData/dailyFitBitPerMonth/fitbit_export_2017_0" + str(i) + ".csv"
    )
    with open(filename, newline="") as csvfile:
        spamreader = csv.reader(csvfile)
        count = 0
        for row in spamreader:
            count = count + 1
            if count > 2 and len(row):
                # print(row[2])
                environment[j, 12] = int(row[2].replace(",", ""))
                environment[j, 19] = int(row[4])
                j += 1

j = 0
filename = "../1_initialRawData/pain2017.csv"
with open(filename, newline="") as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
        count = count + 1
        if count > 2 and len(row):
            if row[3] == "Knees":
                symptoms[j, 0] = float(row[5])
                j += 1

input = open("localData.txt", "rb")
localData = pickle.load(input)
input.close()
# symptoms=localData[0]
xaxis = localData[2]
xaxis = np.append([datetime.datetime(2016, 1, 5, 12, 0)], xaxis)
xaxis = np.append([datetime.datetime(2016, 1, 4, 12, 0)], xaxis)
xaxis = np.append([datetime.datetime(2016, 1, 3, 12, 0)], xaxis)
xaxis = np.append([datetime.datetime(2016, 1, 2, 12, 0)], xaxis)
xaxis = np.append([datetime.datetime(2016, 1, 1, 12, 0)], xaxis)
xaxis = np.delete(xaxis, 59)
for idx, x in enumerate(xaxis):
    xaxis[idx] = x.replace(year=x.year + 1)
xaxis = xaxis[0:273]

averagingwindow = 20
averagingwindow2 = 1  # 4
averagingwindowBig = 60

coeff = 0.4
select = [[12, 1], [19, coeff]]
labels = ["Knee Symptom", "Steps Taken", "Stairs Climbed"]

# for i in range(3,len(environment[:,11])):
# cal = environment[i,11]
# if cal < 1700:
# environment[i,11] = np.mean(environment[i-3:i,11])
# environment[i,12] = np.mean(environment[i-3:i,12])

addMod.additiveModel(
    0,
    select,
    labels,
    symptoms,
    environment,
    xaxis,
    averagingwindow,
    averagingwindow2,
    averagingwindowBig,
    3.3,
)

# Knee Symptoms, Steps Taken and Stairs Climbed
# Average Activity on previous day, last 20 days, and max of the 2, compared to the last 60 days + min put at 0
# Accumulated activity (calculated above) and knee symptoms
# Accumulated activity (calculated above) and knee symptoms, averaged on 7 days
