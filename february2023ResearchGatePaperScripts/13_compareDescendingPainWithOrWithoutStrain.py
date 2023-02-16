import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pkl
import pandas as pd
import numpy as np
import shutil
import os
from statsmodels.stats import rates

# Participant 1

pklFile1 = 'descendingPeriodsMaxDerivative_Knee.pkl'
pklFile2 = 'descendingPeriodsMaxDerivative_Eyes.pkl'

with open(pklFile1, 'rb') as f:
  derivatives1 = pkl.load(f)

with open(pklFile2, 'rb') as f:
  derivatives2 = pkl.load(f)

noStrainIn   = np.concatenate((np.array(derivatives1[0]), np.array(derivatives2[0])))
withStrainIn = np.concatenate((np.array(derivatives1[1]), np.array(derivatives2[1])))

totNoStrain   = len(noStrainIn)
print("noStrain:",   (np.sum(noStrainIn < 0.0000001) / totNoStrain) * 100, (np.sum(noStrainIn >= 0.0000001) / totNoStrain) * 100, " Out of:", totNoStrain, " graphs.")
totWithStrain = len(withStrainIn)
print("withStrain:", (np.sum(withStrainIn < 0.0000001) / totWithStrain) * 100, (np.sum(withStrainIn >= 0.0000001) / totWithStrain) * 100, " Out of:", totWithStrain, " graphs.")

###

noStrainIn2   = noStrainIn.copy()
withStrainIn2 = withStrainIn.copy()

print("Poisson test:", rates.test_poisson_2indep(len(noStrainIn2[noStrainIn2 >= 0.0000001]), len(noStrainIn2), len(withStrainIn2[withStrainIn2 >= 0.0000001]), len(withStrainIn2))[1])


# totNoStrain   = len(noStrainIn)
# print("noStrain:",   (np.sum(noStrainIn == 0) / totNoStrain) * 100, (np.sum(noStrainIn > 0) / totNoStrain) * 100)
# totWithStrain = len(withStrainIn)
# print("withStrain:", (np.sum(withStrainIn == 0) / totWithStrain) * 100, (np.sum(withStrainIn > 0) / totWithStrain) * 100)

# fig7, ax7 = plt.subplots()
# ax7.set_title('Multiple Samples with Different sizes')
# ax7.boxplot([noStrainIn, withStrainIn])
# plt.show()

saveFigs = False

sns.set_theme(style="ticks")
if saveFigs:
  f, ax = plt.subplots(figsize=(3, 2.2), dpi=300)
else:
  f, ax = plt.subplots()

d = {'strainPresence': ["noStrainIn" for val in noStrainIn] + ["withStrainIn" for val in withStrainIn], 'maxDifferential': [val for val in noStrainIn] + [val for val in withStrainIn]}
data = pd.DataFrame(data=d)

sns.boxplot(x="strainPresence", y="maxDifferential", data=data)
sns.stripplot(x="strainPresence", y="maxDifferential", data=data, size=4, color=".3", linewidth=0)

if saveFigs:
  plt.savefig('descendingPainWithVsWithoutStrainPresent.svg')
  plt.close()
else:
  plt.show()


# Participant 2

pklFile1 = 'descendingPeriodsMaxDerivative_Participant2.pkl'

with open(pklFile1, 'rb') as f:
  derivatives1 = pkl.load(f)

noStrainIn   = np.array(derivatives1[0])
withStrainIn = np.array(derivatives1[1])

totNoStrain   = len(noStrainIn)
print("noStrain:",   (np.sum(noStrainIn < 0.0000001) / totNoStrain) * 100, (np.sum(noStrainIn >= 0.0000001) / totNoStrain) * 100, " Out of:", totNoStrain, " graphs.")
totWithStrain = len(withStrainIn)
print("withStrain:", (np.sum(withStrainIn < 0.0000001) / totWithStrain) * 100, (np.sum(withStrainIn >= 0.0000001) / totWithStrain) * 100, " Out of:", totWithStrain, " graphs.")

sns.set_theme(style="ticks")
f, ax = plt.subplots()

d = {'strainPresence': ["noStrainIn" for val in noStrainIn] + ["withStrainIn" for val in withStrainIn], 'maxDifferential': [val for val in noStrainIn] + [val for val in withStrainIn]}
data = pd.DataFrame(data=d)

sns.boxplot(x="strainPresence", y="maxDifferential", data=data)
sns.stripplot(x="strainPresence", y="maxDifferential", data=data, size=4, color=".3", linewidth=0)

plt.show()


# Participant 8

pklFile1 = 'descendingPeriodsMaxDerivative_Participant8.pkl'

with open(pklFile1, 'rb') as f:
  derivatives1 = pkl.load(f)

noStrainIn   = np.array(derivatives1[0])
withStrainIn = np.array(derivatives1[1])

totNoStrain   = len(noStrainIn)
print("noStrain:",   (np.sum(noStrainIn < 0.0000001) / totNoStrain) * 100, (np.sum(noStrainIn >= 0.0000001) / totNoStrain) * 100, " Out of:", totNoStrain, " graphs.")
totWithStrain = len(withStrainIn)
print("withStrain:", (np.sum(withStrainIn < 0.0000001) / totWithStrain) * 100, (np.sum(withStrainIn >= 0.0000001) / totWithStrain) * 100, " Out of:", totWithStrain, " graphs.")

sns.set_theme(style="ticks")
f, ax = plt.subplots()

d = {'strainPresence': ["noStrainIn" for val in noStrainIn] + ["withStrainIn" for val in withStrainIn], 'maxDifferential': [val for val in noStrainIn] + [val for val in withStrainIn]}
data = pd.DataFrame(data=d)

sns.boxplot(x="strainPresence", y="maxDifferential", data=data)
sns.stripplot(x="strainPresence", y="maxDifferential", data=data, size=4, color=".3", linewidth=0)

plt.show()
