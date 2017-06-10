import matplotlib.pyplot as plt

# Standardize the data attributes for the Iris dataset.
from sklearn.datasets import load_iris
from sklearn import preprocessing
# load the Iris dataset
iris = load_iris()
print(iris.data.shape)
# separate the data and target attributes
X = iris.data
y = iris.target
normalized_X = preprocessing.normalize(X)
# standardize the data attributes
standardized_X = preprocessing.scale(X)

plt.subplot(221)
plt.plot(X)
plt.subplot(223)
plt.plot(normalized_X)
plt.subplot(222)
plt.plot(X)
plt.subplot(224)
plt.plot(standardized_X)
plt.show()