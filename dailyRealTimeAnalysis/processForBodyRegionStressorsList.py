from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

figWidth  = 20
figHeight = 5.1

def processForBodyRegionStressorsList(data, region, stressorsList, stressorNormalizationFactorList, expWeightedAvg=False, halfLife=0):
  
  scaler = MinMaxScaler()
  
  bodyRegionCap = region.capitalize()
  # Getting stressors
  for stressor in stressorsList:
    if expWeightedAvg:
      if halfLife:
        data[stressor + "_RollingMean"] = data[stressor].ewm(adjust=False, halflife=halfLife).mean()
      else:
        data[stressor + "_RollingMean"] = data[stressor].ewm(span=14, adjust=False).mean()
    else:
      data[stressor + "_RollingMean"] = data[stressor].rolling(14).mean()
  # Building strain variable
  data[region + 'RelatedStrain'] = 0
  for i in range(len(stressorsList)):
    data[region + 'RelatedStrain'] += data[stressorsList[i]] / stressorNormalizationFactorList[i]
  if expWeightedAvg:
    if halfLife:
      data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].ewm(adjust=False, halflife=halfLife).mean()
    else:
      data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].ewm(span=14, adjust=False).mean()
  else:
    data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].rolling(14).mean()
  # Pain variable
  if expWeightedAvg:
    if halfLife:
      data["realTime" + bodyRegionCap + "Pain_RollingMean"] = data["realTime" + bodyRegionCap + "Pain"].ewm(adjust=False, halflife=halfLife).mean()
    else:
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