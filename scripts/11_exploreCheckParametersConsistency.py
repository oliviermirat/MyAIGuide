import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 1000)

d1 = pd.read_pickle("participant1DifferentParameters.pkl")
d2 = pd.read_pickle("participant2DifferentParameters.pkl")
d8 = pd.read_pickle("participant8DifferentParameters.pkl")

s1 = d1["score"].tolist()
s2 = d2["score"].tolist()
s8 = d8["score"].tolist()

nb_s1above1  = np.sum(np.array(s1) > 1)
nb_s2above1  = np.sum(np.array(s2) > 1)
nb_s8above1  = np.sum(np.array(s8) > 1)

print(nb_s1above1, len(s1), " : ", nb_s1above1 / len(s1))
print(nb_s2above1, len(s2), " : ", nb_s2above1 / len(s2))
print(nb_s8above1, len(s8), " : ", nb_s8above1 / len(s8))

d8[d8["score"] <= 1]

