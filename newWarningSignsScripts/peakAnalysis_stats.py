from scipy import stats
from statsmodels.stats import rates
import numpy as np

def computePoissonPValue(testName, countDescending, descendingRef, countAscending, ascendingRef):
  print("")
  print(testName)
  print("countDescending:", countDescending, "; countAscending:", countAscending)
  print("nbDescendingDays:", descendingRef, "; nbAscendingDays:", ascendingRef)
  print("poisson p-value:", rates.test_poisson_2indep(countDescending, descendingRef, countAscending, ascendingRef)[1])
  return [countDescending + countAscending, descendingRef + ascendingRef, rates.test_poisson_2indep(countDescending, descendingRef, countAscending, ascendingRef)[1], (countAscending / ascendingRef) / (countDescending / descendingRef)]


def computeStatisticalSignificanceTests(maxstrainScores, nbDescendingDays, nbAscendingDays):
  
  testName = "Testing -1 to 0 against 0 to 1"
  countDescending = len(maxstrainScores[np.logical_and(maxstrainScores >= -1, maxstrainScores < 0)])
  countAscending  = len(maxstrainScores[np.logical_and(maxstrainScores >= 0, maxstrainScores <= 1)])
  descendingRef   = nbDescendingDays
  ascendingRef    = nbAscendingDays
  [totCount1, totRef1, poissonPValue1, ratio1] = computePoissonPValue(testName, countDescending, descendingRef, countAscending, ascendingRef)
  
  testName = "Testing -0.8 to 0 against 0 to 1 and -1 to -0.8"
  countDescending = len(maxstrainScores[np.logical_and(maxstrainScores >= -0.8, maxstrainScores < 0)])
  countAscending  = len(maxstrainScores[np.logical_or(maxstrainScores < -0.8, maxstrainScores >= 0)])
  descendingRef   = 0.8 * nbDescendingDays
  ascendingRef    = nbAscendingDays + 0.2 * nbDescendingDays
  [totCount2, totRef2, poissonPValue2, ratio2] = computePoissonPValue(testName, countDescending, descendingRef, countAscending, ascendingRef)
  
  testName = "Testing -1 to 0.2 against 0.2 to 1"
  countDescending = len(maxstrainScores[np.logical_and(maxstrainScores >= -1, maxstrainScores < 0.2)])
  countAscending  = len(maxstrainScores[np.logical_and(maxstrainScores >= 0.2, maxstrainScores <= 1)])
  descendingRef   = nbDescendingDays+nbAscendingDays*0.2
  ascendingRef    = nbAscendingDays*0.8
  [totCount3, totRef3, poissonPValue3, ratio3] = computePoissonPValue(testName, countDescending, descendingRef, countAscending, ascendingRef)
  
  print("")
  print("totCount1, totRef1:", totCount1, totRef1)
  print("totCount2, totRef2:", totCount2, totRef2)
  print("totCount3, totRef3:", totCount3, totRef3)
  if totCount1 == totCount2 and totCount2 == totCount3:
    print("Ok: All tot counts are equal!")
  else:
    print("PROBLEM: some tot counts are different!")
  if totRef1 == totRef2 and totRef2 == totRef3:
    print("Ok: All tot ref are equal!")
  else:
    print("PROBLEM: some tot ref are different!")  
  
  return {"range1" : "Testing -1 to 0 against 0 to 1",
          "poissonPValue1": poissonPValue1,
          "ratio1": ratio1,
          "totCount1": totCount1, 
          "totRef1": totRef1,
          "range2" : "Testing -0.8 to 0 against 0 to 1 and -1 to -0.8",
          "poissonPValue2": poissonPValue2,
          "ratio2": ratio2,
          "totCount2": totCount2, 
          "totRef2": totRef2,
          "range3" : "Testing -1 to 0.2 against 0.2 to 1",
          "poissonPValue3": poissonPValue3,
          "ratio3": ratio3,
          "totCount3": totCount3, 
          "totRef3": totRef3
          }