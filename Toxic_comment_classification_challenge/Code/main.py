import pandas as pd 
import matplotlib
import numpy as np
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import CountVectorizer
import sklearn.model_selection
from sklearn.feature_extraction.text import TfidfTransformer

path ='../Datasets/rawData/'
dataset=pd.read_csv(path + 'train.csv'.format(1))
dataset.head()
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(dataset.comment_text)
tfidf_transformer = TfidfTransformer()
train = tfidf_transformer.fit_transform(X_train_counts)

a = np.array(dataset.toxic)
b = np.array(dataset.severe_toxic)
c = np.array(dataset.obscene)
d = np.array(dataset.threat)
e = np.array(dataset.insult)
f = np.array(dataset.identity_hate)
targetTrain=np.column_stack((a,b,c,d,e,f))
target_pd = pd.DataFrame(targetTrain)

print('I"m ready to fit')
classifier = BinaryRelevance(GaussianNB())
classifier.fit(train,targetTrain)
print('I"ve finished')