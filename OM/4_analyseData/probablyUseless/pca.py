from sklearn.decomposition import PCA
import pickle
import moysAndGroups as mam
import matplotlib.pyplot as plt
import numpy as np

input = open('localData2.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]
past=mam.createPastMoy(environment,[0.1,0.2,0.5,1],[-3,-2,-1,0])

pca = PCA(n_components=2)
past2=pca.fit_transform(past)
print(pca.explained_variance_ratio_)
print(sum(pca.explained_variance_ratio_))

# plt.plot(past2[:,0],past2[:,1],'.')
# plt.show()

head=symptoms[:,0]
cond1=head<3.5
cond2=head>=3.5

cond1=np.array([cond1,]*2).transpose()
cond2=np.array([cond2,]*2).transpose()

small=np.extract(cond1,past2)
small=small.reshape((int(len(small)/2), 2))

big=np.extract(cond2,past2)
big=big.reshape((int(len(big)/2), 2))

plt.plot(small[:,0],small[:,1],'.')
plt.plot(big[:,0],big[:,1],'.')
plt.show()
