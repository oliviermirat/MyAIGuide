from processForBodyRegionHighlightParams import processForBodyRegionHighlightParams
import pandas as pd

figWidth  = 20
figHeight = 5.1

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= "2023-05-15"]

### Available useful fields: 'garminKneeRelatedActiveCalories', 'garminArmsRelatedActiveCalories', 'totalComputerPressRealTime', 'manicTimeRealTime', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeEyeDrivingTime', 'realTimeEyeRidingTime'

# Knee pain
processForBodyRegionHighlightParams(data, 'knee', "garminKneeRelatedActiveCalories", "realTimeEyeDrivingTime", 1000, 10*60)

# Arm pain
processForBodyRegionHighlightParams(data, 'arm', "garminArmsRelatedActiveCalories", "whatPulseRealTime", 1000, 25000)

# Face pain
data["realTimeEyeInCar"] = data["realTimeEyeDrivingTime"] + data["realTimeEyeRidingTime"]
processForBodyRegionHighlightParams(data, "face", "manicTimeRealTime", "realTimeEyeInCar", 10*60, 15*60)
