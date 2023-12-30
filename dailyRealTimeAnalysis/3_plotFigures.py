from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

figWidth  = 20
figHeight = 5.1

scaler = MinMaxScaler()

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= "2023-05-15"]

### Available useful fields: 'garminKneeRelatedActiveCalories', 'garminArmsRelatedActiveCalories', 'totalComputerPressRealTime', 'manicTimeRealTime', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeEyeDrivingTime', 'realTimeEyeRidingTime'

def processForBodyRegion(region, stressor1, stressor2, stressor1_normalizationFactor, stressor2_normalizationFactor):
  bodyRegionCap = region.capitalize()
  # Getting stressors
  data[stressor1 + "_RollingMean"] = data[stressor1].rolling(14).mean()
  data[stressor2 + "_RollingMean"] = data[stressor2].rolling(14).mean()
  # Building strain variable
  data[region + 'RelatedStrain'] = data[stressor1] / stressor1_normalizationFactor + data[stressor2] / stressor2_normalizationFactor
  data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].rolling(14).mean()
  # Pain variable
  data["realTime" + bodyRegionCap + "Pain_RollingMean"] = data["realTime" + bodyRegionCap + "Pain"].rolling(14).mean()
  # Normalization
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[region + "RelatedStrain_RollingMean", "realTime" + bodyRegionCap + "Pain_RollingMean"]])
  # Dealing with outliers
  if True:
    for dataField in [stressor1, stressor2, region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']:
      data[dataField].fillna(data[dataField].mean(), inplace=True)
      data[dataField + '_RollingMean'].fillna(data[dataField + '_RollingMean'].mean(), inplace=True)
    for dataField in [region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]:
      data[dataField].fillna(data[dataField].mean(), inplace=True)
  else:
    data.fillna(0, inplace=True)
  # Plot
  hspace   = 0.4
  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=5, ncols=1)
  fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
  for idx, dataField in enumerate([stressor1, stressor2, region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']):
    color1 = (0.12156863, 0.46666667, 0.70588235) # blue
    color2 = (1.0, 0.49803922, 0.05490196) # orange
    if idx == 2:
      color2 = "k"
    if idx == 3:
      color2 = "r"
    data[[dataField, dataField + '_RollingMean']].plot(ax=axes[idx], color=[color1, color2])
    axes[idx].title.set_fontsize(10)
    stressorTitle = dataField
    if idx == 0:
      stressorTitle += '; Normalization factor: ' + str(stressor1_normalizationFactor)
    elif idx == 1:
      stressorTitle += '; Normalization factor: ' + str(stressor2_normalizationFactor)
    axes[idx].title.set_text(stressorTitle)
    axes[idx].get_legend().remove()
    axes[idx].get_xaxis().set_visible(False)
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]].plot(ax=axes[4], color=["k", "r"])
  axes[4].title.set_fontsize(10)
  axes[4].title.set_text("summary strain vs pain")
  axes[4].get_legend().remove()
  axes[4].get_xaxis().set_visible(False)
  plt.show()


def processForBodyRegionStressorsList(data, region, stressorsList, stressorNormalizationFactorList, expWeightedAvg=False):
  bodyRegionCap = region.capitalize()
  # Getting stressors
  for stressor in stressorsList:
    if expWeightedAvg:
      data[stressor + "_RollingMean"] = data[stressor].ewm(span=14, adjust=False).mean()
    else:
      data[stressor + "_RollingMean"] = data[stressor].rolling(14).mean()
  # Building strain variable
  data[region + 'RelatedStrain'] = 0
  for i in range(len(stressorsList)):
    data[region + 'RelatedStrain'] += data[stressorsList[i]] / stressorNormalizationFactorList[i]
  if expWeightedAvg:
    data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].ewm(span=14, adjust=False).mean()
  else:
    data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].rolling(14).mean()
  # Pain variable
  if expWeightedAvg:
    data["realTime" + bodyRegionCap + "Pain_RollingMean"] = data["realTime" + bodyRegionCap + "Pain"].ewm(span=14, adjust=False).mean()
  else:
    data["realTime" + bodyRegionCap + "Pain_RollingMean"] = data["realTime" + bodyRegionCap + "Pain"].rolling(14).mean()
  # Normalization
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[region + "RelatedStrain_RollingMean", "realTime" + bodyRegionCap + "Pain_RollingMean"]])
  # Dealing with outliers
  if True:
    for dataField in stressorsList + [region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']:
      data[dataField].fillna(data[dataField].mean(), inplace=True)
      data[dataField + '_RollingMean'].fillna(data[dataField + '_RollingMean'].mean(), inplace=True)
    for dataField in [region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]:
      data[dataField].fillna(data[dataField].mean(), inplace=True)
  else:
    data.fillna(0, inplace=True)
  # Plot
  hspace   = 0.4
  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=len(stressorsList)+3, ncols=1)
  fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
  for idx, dataField in enumerate(stressorsList + [region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']):
    color1 = (0.12156863, 0.46666667, 0.70588235) # blue
    color2 = (1.0, 0.49803922, 0.05490196) # orange
    if idx == len(stressorsList):
      color2 = "k"
    if idx == len(stressorsList) + 1:
      color2 = "r"
    data[[dataField, dataField + '_RollingMean']].plot(ax=axes[idx], color=[color1, color2])
    axes[idx].title.set_fontsize(10)
    stressorTitle = dataField
    if idx < len(stressorsList):
      stressorTitle += '; Normalization factor: ' + str(stressorNormalizationFactorList[idx])
    axes[idx].title.set_text(stressorTitle)
    axes[idx].get_legend().remove()
    axes[idx].get_xaxis().set_visible(False)
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]].plot(ax=axes[len(stressorsList) + 2], color=["k", "r"])
  axes[len(stressorsList)+2].title.set_fontsize(10)
  axes[len(stressorsList)+2].title.set_text("summary strain vs pain")
  axes[len(stressorsList)+2].get_legend().remove()
  axes[len(stressorsList)+2].get_xaxis().set_visible(False)
  plt.show()


# expWeightedAvg = True

# Knee pain
processForBodyRegionStressorsList(data, 'knee', ["garminSteps", "garminCyclingActiveCalories", "realTimeEyeDrivingTime"], [15000, 700, 10*60])
processForBodyRegion('knee', "garminKneeRelatedActiveCalories", "realTimeEyeDrivingTime", 1000, 10*60)

# Arm pain
processForBodyRegion('arm', "garminArmsRelatedActiveCalories", "whatPulseRealTime", 1000, 15000)
processForBodyRegionStressorsList(data, 'arm', ["garminArmsRelatedActiveCalories", "whatPulseRealTime", "phoneTime"], [1000, 15000, 600])

# Face pain
data["realTimeEyeInCar"] = data["realTimeEyeDrivingTime"] + data["realTimeEyeRidingTime"]
processForBodyRegion("face", "manicTimeRealTime", "realTimeEyeInCar", 10*60, 15*60)
