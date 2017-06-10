import pickle
import findOptimalShift as optShift
import numpy as np
import matplotlib.pyplot as plt

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

# for i in range(1,60):
[shift,maxx]=optShift.testCorrel(1,[[0,1/3600],[34,1/60],[33,1/60]],symptoms,environment,xaxis,1)
print(shift,maxx)

# head=symptoms[:,1]
# manictime=environment[:,0]/(60*60)
# ubuntu=environment[:,34]/60
# paper=environment[:,33]/60
# driving=environment[:,35]/60
# simuPlot([head,manictime+ubuntu+paper],['head','computer'],xaxis)
