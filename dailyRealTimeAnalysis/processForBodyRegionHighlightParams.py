from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

figWidth  = 20
figHeight = 5.1
expSpan   = 21

def processForBodyRegionHighlightParams(data, region, stressor1, stressor2, stressor1_normalizationFactor, stressor2_normalizationFactor, plotPain, lowerLimitDate='', compareBeforeAfterJan2024=False, exponentialWeight=False, numberOfFig=0):
  
  plotTitleForEachSubplot = not(compareBeforeAfterJan2024)
  
  scaler = MinMaxScaler()
  
  bodyRegionCap = region.capitalize()
  # Getting stressors
  data[stressor1 + "_RollingMean"] = data[stressor1].ewm(span=expSpan).mean() if exponentialWeight else data[stressor1].rolling(14).mean()
  data[stressor2 + "_RollingMean"] = data[stressor2].ewm(span=expSpan).mean() if exponentialWeight else data[stressor2].rolling(14).mean()
  # Building strain variable if exponentialWeight else data[stressor2].rolling(14).mean()
  # Building strain variable
  data[region + 'RelatedStrain'] = data[stressor1] / stressor1_normalizationFactor + data[stressor2] / stressor2_normalizationFactor
  data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].ewm(span=expSpan).mean() if exponentialWeight else data[region + "RelatedStrain"].rolling(14).mean()
  # Pain variable
  data["realTime" + bodyRegionCap + "Pain_RollingMean"] = data["realTime" + bodyRegionCap + "Pain"].ewm(span=expSpan).mean() if exponentialWeight else data["realTime" + bodyRegionCap + "Pain"].rolling(14).mean()
  
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
  
  # Filtering by date
  if len(lowerLimitDate):
    print("setting lower limit date to:", lowerLimitDate)
    data = data.loc[data.index >= lowerLimitDate]
  
  # Plot
  if plotTitleForEachSubplot:
    hspace   = 0.4
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=5, ncols=1)
    fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    hspace   = 1
    fig, axes = plt.subplots(nrows=5, ncols=1)
    fig.subplots_adjust(hspace=hspace)
  for idx, dataField in enumerate([stressor1, stressor2, region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']):
    color1 = (0.12156863, 0.46666667, 0.70588235) # blue
    color2 = (1.0, 0.49803922, 0.05490196) # orange
    if idx == 0:
      color1 = "b"
    if idx == 1:
      color1 = "g"    
    if idx == 2:
      color2 = "k"
    if idx == 3:
      color2 = "r"
    if idx <= 1:
      # data[[dataField, dataField + '_RollingMean']].plot(ax=axes[idx], color=[color1, color2])
      data[[dataField]].plot(ax=axes[idx], color=[color1])
      axes[idx].title.set_fontsize(10)
      stressorTitle = dataField
      if idx == 0:
        stressorTitle += '; Normalization factor: ' + str(stressor1_normalizationFactor)
      elif idx == 1:
        stressorTitle += '; Normalization factor: ' + str(stressor2_normalizationFactor)
      if plotTitleForEachSubplot:
        axes[idx].title.set_text(stressorTitle)
      axes[idx].get_legend().remove()
      axes[idx].get_xaxis().set_visible(False)
  
  if plotPain:
    
    # First parameter highlight
    data[["realTime" + bodyRegionCap + "Pain", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[["realTime" + bodyRegionCap + "Pain", region + "PainMeanAndNormalize"]])
    data[["realTime" + bodyRegionCap + "Pain", region + "PainMeanAndNormalize"]].plot(ax=axes[3], color=["k", "r"])
    axes[3].title.set_fontsize(10)
    if plotTitleForEachSubplot:
      axes[3].title.set_text("summary " + stressor1 + " vs pain")
    axes[3].get_legend().remove()
    axes[3].get_xaxis().set_visible(False)
    
  else:
    
    # First parameter highlight
    data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]])
    data[[stressor1 + "_RollingMean", region + "PainMeanAndNormalize"]].plot(ax=axes[2], color=["b", "r"])
    axes[2].title.set_fontsize(10)
    if plotTitleForEachSubplot:
      axes[2].title.set_text("summary " + stressor1 + " vs pain")
    axes[2].get_legend().remove()
    axes[2].get_xaxis().set_visible(False)
    
    # Second parameter highlight
    data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]])
    data[[stressor2 + "_RollingMean", region + "PainMeanAndNormalize"]].plot(ax=axes[3], color=["g", "r"])
    axes[3].title.set_fontsize(10)
    if plotTitleForEachSubplot:
      axes[3].title.set_text("summary " + stressor2 + " vs pain")
    axes[3].get_legend().remove()
    axes[3].get_xaxis().set_visible(False)
  
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]] = scaler.fit_transform(data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]])
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]].plot(ax=axes[4], color=["k", "r"])
  if plotTitleForEachSubplot:
    axes[4].title.set_fontsize(10)
    axes[4].title.set_text("summary strain vs pain")
  axes[4].get_legend().remove()
  # axes[4].get_xaxis().set_visible(False)
  
  if not(numberOfFig):
    plt.show()
  else:
    figsFormat = 'png'
    plt.savefig(str(numberOfFig) + '_' + str(region) + '_' + str('exponential' if exponentialWeight else 'mean') + '.' + figsFormat, format=figsFormat)    
  
  ### Adding comparison to computer usage
  if False:
    from correlCompare import processForBodyRegionHighlightParams_ComputerToCaloriesCorrel
    processForBodyRegionHighlightParams_ComputerToCaloriesCorrel(stressor1, data)
  
  if compareBeforeAfterJan2024:
  
    from scipy import stats
    import numpy as np
    
    dataBefore = data.loc[data.index <  '2024-01-01'].copy()
    dataAfter  = data.loc[data.index >= '2024-01-01'].copy()

    allDataBefore = np.array(dataBefore[[region + "StrainMeanAndNormalize"]].values.tolist()).T[0].tolist()
    allDataAfter  = np.array(dataAfter[[region + "StrainMeanAndNormalize"]].values.tolist()).T[0].tolist()
    
    print(np.std(allDataBefore), np.std(allDataAfter))
    t_stat, p_value = stats.ttest_ind(allDataBefore, allDataAfter, equal_var=False)
    print("Welch's t-statistic:", t_stat)
    print("p-value:", p_value)
    
    fig, axes = plt.subplots(nrows=3, ncols=1)
    
    # data[[region + "StrainMeanAndNormalize", region + 'RelatedStrain']].plot(ax=axes[0], color=["k", "b"])
    data[[region + "StrainMeanAndNormalize"]].plot(ax=axes[0], color=["k"])
    axes[0].get_legend().remove()
    
    axes[1].boxplot([allDataBefore, allDataAfter], labels=["before january 1st 2024", "after january 1st 2024"])
    
    if True:
      allDataBefore = (np.array(allDataBefore[15:])-np.array(allDataBefore[:-15])).tolist()
      allDataAfter  = (np.array(allDataAfter[15:])-np.array(allDataAfter[:-15])).tolist()
      print(np.std(allDataBefore), np.std(allDataAfter))
      t_stat, p_value = stats.ttest_ind(allDataBefore, allDataAfter, equal_var=False)
      print("Welch's t-statistic:", t_stat)
      print("p-value:", p_value)
      axes[2].boxplot([allDataBefore, allDataAfter], labels=["before january 1st 2024", "after january 1st 2024"])
    
    plt.show()
