
# coding: utf-8

# In[7]:


import os, sys
import pandas as pd
import numpy as np

path = os.getcwd() + '/anonymized_dataset_for_ADM2017/'
print(path)


# In[22]:





# In[21]:


log1 = pd.read_csv(path + 'student_log_{}.csv'.format(1))
initial_col_order = [col.lower() for col in list(log1.columns)]


# In[26]:


data = pd.DataFrame()
for i in range(1, 10):
    student_log = pd.read_csv(path + 'student_log_{}.csv'.format(i), low_memory=False)
    student_log.columns = [col.lower() for col in student_log]
    data = pd.concat([data, student_log], ignore_index=True)

data = data[initial_col_order]
print(data.shape)
data.head()

training = pd.read_csv(path + 'training_label.csv').drop(['AveCorrect'], axis=1)
training.columns = [col.lower() for col in training.columns]
training.shape


# In[30]:


# testing on a little dataset
df = data
df1 = df.merge(training, on='itest_id', how="left")


actions = df1[df1.isstem.notnull()]

print("training set size: ", training.shape[0], "actions for # of students: ", len(actions.itest_id.unique()))
print("sample size useless for training: ", training.shape[0] - len(actions.itest_id.unique()))

print(df1.shape)
print(actions.shape)

# merged training data set
stem = actions[actions.isstem == 1]
nonstem = actions[actions.isstem == 0]

stem.shape, nonstem.shape


# In[31]:


actions.columns


# In[32]:


actions.info()

