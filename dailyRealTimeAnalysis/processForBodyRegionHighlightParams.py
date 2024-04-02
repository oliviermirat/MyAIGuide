from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

figWidth  = 20
figHeight = 5.1

def processForBodyRegionHighlightParams(data, region, stressor1, stressor2, stressor1_normalizationFactor, stressor2_normalizationFactor):
  
  scaler = MinMaxScaler()
  
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
    if idx <= 1:
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
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]].plot(ax=axes[2], color=["k", "r"])
  axes[2].title.set_fontsize(10)
  axes[2].title.set_text("summary strain vs pain")
  axes[2].get_legend().remove()
  axes[2].get_xaxis().set_visible(False)
  
  # First parameter highlight
  data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]])
  data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]].plot(ax=axes[3], color=["k", "r"])
  axes[3].title.set_fontsize(10)
  axes[3].title.set_text("summary " + stressor1 + " vs pain")
  axes[3].get_legend().remove()
  axes[3].get_xaxis().set_visible(False)
  
  # Second parameter highlight
  data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]])
  data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]].plot(ax=axes[4], color=["k", "r"])
  axes[4].title.set_fontsize(10)
  axes[4].title.set_text("summary " + stressor2 + " vs pain")
  axes[4].get_legend().remove()
  axes[4].get_xaxis().set_visible(False)
  
  plt.show()
  
  ### Adding comparison to computer usage
  if False:
    from correlCompare import processForBodyRegionHighlightParams_ComputerToCaloriesCorrel
    processForBodyRegionHighlightParams_ComputerToCaloriesCorrel(stressor1, data)
