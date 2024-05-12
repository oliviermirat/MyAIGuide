from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

figWidth  = 20
figHeight = 5.1

def functionToOptimize(data, region, stressorsList, stressorsNormalizationFactor, bodyRegionCap):
  scaler = MinMaxScaler()
  for stressor in stressorsList:
    data[stressor + "_RollingMean"] = data[stressor].rolling(14).mean()
  data[region + 'RelatedStrain'] = 0
  for idx, stressor in enumerate(stressorsList): 
    data[region + 'RelatedStrain'] += data[stressor] / stressorsNormalizationFactor[idx]
  strain = data[region + "RelatedStrain"].rolling(14).mean().values.tolist()
  pain = data["realTime" + bodyRegionCap + "Pain"].rolling(14).mean().values.tolist()
  correlationCoeff = np.corrcoef(np.array(strain[13:]), np.array(pain[13:]))[0, 1]
  return correlationCoeff

def optimizeNormalizationFactor(data, region, stressorsList, stressorsNormalizationFactor, bodyRegionCap):
  
  def function(x1, x2, x3, x4):
    return -functionToOptimize(data, region, stressorsList, [x1, x2, x3, x4], bodyRegionCap)
  
  x1, x2, x3, x4 = stressorsNormalizationFactor[0], stressorsNormalizationFactor[1], stressorsNormalizationFactor[2], stressorsNormalizationFactor[3]  # Initial values
  learning_rate = 10000
  eps = 10
  iterations = 1000

  for i in range(iterations):
    
    print(i)
    
    # Approximate gradients using finite difference
    f_x1 = (function(x1 + eps, x2, x3, x4) - function(x1 - eps, x2, x3, x4)) / (2 * eps)
    f_x2 = (function(x1, x2 + eps, x3, x4) - function(x1, x2 - eps, x3, x4)) / (2 * eps)
    f_x3 = (function(x1, x2, x3 + eps, x4) - function(x1, x2, x3 - eps, x4)) / (2 * eps)
    f_x4 = (function(x1, x2, x3, x4 + eps) - function(x1, x2, x3, x4 - eps)) / (2 * eps)
    
    print(x1, x2, x3, x4)

    # Update the variables
    x1 = max(10, x1 - learning_rate * f_x1)
    x2 = max(10, x2 - learning_rate * f_x2)
    x3 = max(10, x3 - learning_rate * f_x3)
    x4 = max(10, x4 - learning_rate * f_x4)
  
  optimized_variables = [x1, x2, x3, x4]
  
  print("Original values:", stressorsNormalizationFactor, "; val:", -function(stressorsNormalizationFactor[0], stressorsNormalizationFactor[1], stressorsNormalizationFactor[2], stressorsNormalizationFactor[3]))
  print("Optimized values:", optimized_variables, "; val:", -function(optimized_variables[0], optimized_variables[1], optimized_variables[2], optimized_variables[3]))
  
  return optimized_variables


def processForBodyRegionHighlightParamsMultiple(data, region, stressorsList, stressorsNormalizationFactor, plotPain, lowerLimitDate=''):
  
  if False:
    stressorsNormalizationFactor = optimizeNormalizationFactor(data, region, stressorsList, stressorsNormalizationFactor, region.capitalize())
  
  scaler = MinMaxScaler()
  
  bodyRegionCap = region.capitalize()
  # Getting stressors
  for stressor in stressorsList:
    data[stressor + "_RollingMean"] = data[stressor].rolling(14).mean()
  # Building strain variable
  data[region + 'RelatedStrain'] = 0
  for idx, stressor in enumerate(stressorsList): 
    data[region + 'RelatedStrain'] += data[stressor] / stressorsNormalizationFactor[idx]
  data[region + "RelatedStrain_RollingMean"] = data[region + "RelatedStrain"].rolling(14).mean()
  # Pain variable
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
  
  # Filtering by date
  if len(lowerLimitDate):
    print("setting lower limit date to:", lowerLimitDate)
    data = data.loc[data.index >= lowerLimitDate]
  
  # Plot
  hspace   = 0.4
  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=len(stressorsList)+1, ncols=1) #nrows=2*len(stressorsList)+1, ncols=1)
  fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
  if False:
    for idx, dataField in enumerate(stressorsList + [region + 'RelatedStrain', 'realTime' + bodyRegionCap + 'Pain']):
      color1 = (0.12156863, 0.46666667, 0.70588235) # blue
      color2 = (1.0, 0.49803922, 0.05490196) # orange
      # if idx == 2:
        # color2 = "k"
      # if idx == 3:
        # color2 = "r"
      if idx < len(stressorsList):
        data[[dataField, dataField + '_RollingMean']].plot(ax=axes[idx], color=[color1, color2])
        axes[idx].title.set_fontsize(10)
        stressorTitle = dataField
        stressorTitle += '; Normalization factor: ' + str(stressorsNormalizationFactor[idx])
        axes[idx].title.set_text(stressorTitle)
        axes[idx].get_legend().remove()
        axes[idx].get_xaxis().set_visible(False)
  data[[region + "StrainMeanAndNormalize", region + "PainMeanAndNormalize"]].plot(ax=axes[len(stressorsList)], color=["k", "r"])
  axes[len(stressorsList)].title.set_fontsize(10)
  axes[len(stressorsList)].title.set_text("summary strain vs pain")
  axes[len(stressorsList)].get_legend().remove()
  axes[len(stressorsList)].get_xaxis().set_visible(False)
    
  # Parameter highlight
  for idx, stressor in enumerate(stressorsList):
    rounding = 100
    maxVal           = int(( np.max(data[stressor].values.tolist()) )*rounding)/rounding
    maxValDivNorm    = int(( np.max(data[stressor].values.tolist()) / stressorsNormalizationFactor[idx] )*rounding)/rounding
    meanVal          = int(( np.mean(data[stressor].values.tolist()) )*rounding)/rounding
    meanValDivNorm   = int(( np.mean(data[stressor].values.tolist()) / stressorsNormalizationFactor[idx] )*rounding)/rounding
    medianVal        = int(( np.median(data[stressor].values.tolist()) )*rounding)/rounding
    medianValDivNorm = int(( np.median(data[stressor].values.tolist()) / stressorsNormalizationFactor[idx] )*rounding)/rounding
    contribution = stressor + ": normalization factor:" + str(stressorsNormalizationFactor[idx]) + " ;;; contribution:: max:" + str(maxVal) + " , " + str(maxValDivNorm) + " ;;; mean:" + str(meanVal) + " , " + str(meanValDivNorm) + " ;;; median:" + str(medianVal) + " , " + str(medianValDivNorm)
    data[[stressor + "_RollingMean", region + "PainMeanAndNormalize", stressor]] = scaler.fit_transform(data[[stressor + "_RollingMean", region + "PainMeanAndNormalize", stressor]])
    data[[stressor + "_RollingMean", region + "PainMeanAndNormalize", stressor]].plot(ax=axes[idx], color=["k", "r", "g"])
    axes[idx].title.set_fontsize(10)
    axes[idx].title.set_text(contribution)
    axes[idx].get_legend().remove()
    axes[idx].get_xaxis().set_visible(False)
  
  plt.show()
  
  ### Adding comparison to computer usage
  if False:
    from correlCompare import processForBodyRegionHighlightParams_ComputerToCaloriesCorrel
    processForBodyRegionHighlightParams_ComputerToCaloriesCorrel(stressor1, data)
  
  if False:
    
    dataBefore = data.loc[data.index <  '2024-01-01'].copy()
    dataAfter  = data.loc[data.index >= '2024-01-01'].copy()

    allDataBefore = np.array(dataBefore[[region + "StrainMeanAndNormalize"]].values.tolist()).T[0].tolist()
    allDataAfter  = np.array(dataAfter[[region + "StrainMeanAndNormalize"]].values.tolist()).T[0].tolist()
    
    if True:
      allDataBefore = (np.array(allDataBefore[15:])-np.array(allDataBefore[:-15])).tolist()
      allDataAfter  = (np.array(allDataAfter[15:])-np.array(allDataAfter[:-15])).tolist()
    
    print(np.std(allDataBefore), np.std(allDataAfter))
    t_stat, p_value = stats.ttest_ind(allDataBefore, allDataAfter, equal_var=False)
    print("Welch's t-statistic:", t_stat)
    print("p-value:", p_value)
    
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(6, 6), sharey=True)
    axs.boxplot([allDataBefore, allDataAfter], labels=["before january 1st 2024", "after january 1st 2024"])
    
    plt.show()
