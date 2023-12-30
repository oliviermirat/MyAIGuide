from processForBodyRegionStressorsList import processForBodyRegionStressorsList
from processForBodyRegion import processForBodyRegion
import pandas as pd

halfLife = 20

figWidth  = 20
figHeight = 5.1

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= "2023-05-15"]

### Available useful fields: 'garminKneeRelatedActiveCalories', 'garminArmsRelatedActiveCalories', 'totalComputerPressRealTime', 'manicTimeRealTime', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeEyeDrivingTime', 'realTimeEyeRidingTime'

# Knee pain
processForBodyRegionStressorsList(data, 'knee', ["garminSteps", "garminCyclingActiveCalories", "realTimeEyeDrivingTime"], [15000, 700, 10*60], True, halfLife)
processForBodyRegionStressorsList(data, 'knee', ["garminKneeRelatedActiveCalories", "realTimeEyeDrivingTime"], [1000, 10*60], True, halfLife)

# Arm pain
processForBodyRegionStressorsList(data, 'arm', ["garminArmsRelatedActiveCalories", "whatPulseRealTime"], [1000, 15000], True, halfLife)
processForBodyRegionStressorsList(data, 'arm', ["garminArmsRelatedActiveCalories", "whatPulseRealTime", "phoneTime"], [1000, 15000, 600], True, halfLife)

# Face pain
data["realTimeEyeInCar"] = data["realTimeEyeDrivingTime"] + data["realTimeEyeRidingTime"]
processForBodyRegionStressorsList(data, 'face', ["manicTimeRealTime", "realTimeEyeInCar"], [10*60, 15*60], True, halfLife)
