import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
df1=pd.DataFrame(np.random.random(630).reshape(70,9))
df2=pd.DataFrame(np.zeros(35).reshape(35,1))
df3=pd.DataFrame(np.ones(35).reshape(35,1))
df4=pd.concat([df2,df3],axis=0,ignore_index=True)
df=pd.concat([df1,df4],axis=1,ignore_index=True)
print(df)
data_columns=df1.columns
length=len(data_columns)

X=df.iloc[:,0:-2]
X1=X_train.values
y=df.iloc[:,-1]
y1=y_train.values
X_train,X_test,y_train,y_test=train_test_split(X1,y1,random_state=4)
log=LogisticRegression()
log.fit(X_train,y_train)
scores=cross_val_score(log,X,y,cv,scoring='accuracy')
print(scores)
print(scores.mean())

def logistic(df,c):
    X=df.iloc[:,0:-2]
    X1=X.values
    y=df.iloc[:,-1]
    y1=y.values
    X_train,X_test,y_train,y_test=train_test_split(X1,y1,random_state=4)
    log=LogisticRegression()
    log.fit(X_train,y_train)
    scores=cross_val_score(log,X,y,cv=c,scoring='accuracy')
    means=scores.mean()
    return means

logistic(df,10)
