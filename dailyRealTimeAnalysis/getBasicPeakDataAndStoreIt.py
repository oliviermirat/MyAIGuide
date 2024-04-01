import pandas as pd
import numpy as np
import pickle
import sys
sys.path.insert(1, '../src/MyAIGuide/data')
from storeBasisPeakCaloriesInDataFrame import storeBasisPeakCaloriesInDataFrame

# Creation of the dataframe where everything will be stored
i = pd.date_range("2015-11-19", periods=2320, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "basisPeakCalories": empty,
}
data = pd.DataFrame(data=d, index=i)

if (True):  # This step takes a long time, put to False if you want to skip it, and to True otherwise
  filename = "../data/raw/ParticipantData/Participant1/bodymetrics.csv"
  data = storeBasisPeakCaloriesInDataFrame(filename, data)

output = open("basisPeakCalories.pkl", "wb")
pickle.dump(data, output)
output.close()

