from processForBodyRegionHighlightParamsMultiple import processForBodyRegionHighlightParamsMultiple
from processForBodyRegionHighlightParams import processForBodyRegionHighlightParams
import pandas as pd

figWidth  = 20
figHeight = 5.1

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= "2023-05-15"]

# Adjusting for some of Garmin's fake active calories due to bug of recording cycling activity then removing items
data.loc['2024-04-30', 'garminKneeRelatedActiveCalories'] = data.loc['2024-04-30', 'garminKneeRelatedActiveCalories'] - 100
data.loc['2024-05-01', 'garminKneeRelatedActiveCalories'] = data.loc['2024-05-01', 'garminKneeRelatedActiveCalories'] - 100
data.loc['2024-05-03', 'garminKneeRelatedActiveCalories'] = data.loc['2024-05-03', 'garminKneeRelatedActiveCalories'] - 100
data.loc['2024-05-04', 'garminKneeRelatedActiveCalories'] = data.loc['2024-05-04', 'garminKneeRelatedActiveCalories'] - 250
data.loc['2024-05-05', 'garminKneeRelatedActiveCalories'] = data.loc['2024-05-05', 'garminKneeRelatedActiveCalories'] - 550

data["realTimeEyeInCar"] = data["realTimeEyeDrivingTime"] + data["realTimeEyeRidingTime"]

### Available useful fields: 'garminKneeRelatedActiveCalories', 'garminArmsRelatedActiveCalories', 'totalComputerPressRealTime', 'manicTimeRealTime', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeEyeDrivingTime', 'realTimeEyeRidingTime'

plotPain = False
numberOfFig = 0

# Knee pain
for exponentialWeight in [False, True]:
  numberOfFig += 1
  processForBodyRegionHighlightParams(data, 'knee', "garminKneeRelatedActiveCalories", "realTimeEyeDrivingTime", 1000, 1250, plotPain, exponentialWeight=exponentialWeight, numberOfFig=numberOfFig)
for exponentialWeight in [False, True]:
  numberOfFig += 1
  processForBodyRegionHighlightParamsMultiple(data.copy(), 'knee', ["garminKneeRelatedActiveCalories", "garminSteps", "garminCyclingActiveCalories", "realTimeEyeDrivingTime"], [500, 20000, 400, 1250], plotPain, exponentialWeight=exponentialWeight, numberOfFig=numberOfFig)

# Arm pain
for exponentialWeight in [False, True]:
  numberOfFig += 1
  processForBodyRegionHighlightParams(data, 'arm', "garminArmsRelatedActiveCalories", "whatPulseRealTime", 1000, 25000, plotPain, '2023-08-15', exponentialWeight=exponentialWeight, numberOfFig=numberOfFig)
for exponentialWeight in [False, True]:
  numberOfFig += 1
  processForBodyRegionHighlightParamsMultiple(data, 'arm', ["garminSurfSwimActiveCalories", "garminClimbingActiveCalories", "whatPulseRealTime"], [1000, 110, 25000], plotPain, '2023-08-15', exponentialWeight=exponentialWeight, numberOfFig=numberOfFig)

# Face pain
for exponentialWeight in [False, True]:
  numberOfFig += 1
  processForBodyRegionHighlightParams(data, "face", "manicTimeRealTime", "realTimeEyeInCar", 10*60, 15*60, plotPain, exponentialWeight=exponentialWeight, numberOfFig=numberOfFig)

