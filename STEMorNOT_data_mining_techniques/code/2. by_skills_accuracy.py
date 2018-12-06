import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
path = os.getcwd() + '/anonymized_dataset_for_ADM2017/'
print(path)
log1 = pd.read_csv(path + 'student_log_{}.csv'.format(1))
initial_col_order = [col.lower() for col in list(log1.columns)]

data = pd.DataFrame()
for i in range(1, 10):
    student_log = pd.read_csv(path + 'student_log_{}.csv'.format(i))
    student_log.columns = [col.lower() for col in student_log]
    data = pd.concat([data, student_log], ignore_index=True)

# reorder everything with the original order, where student id is in the first column
data = data[initial_col_order]
data.shape
data.head()
z = []
for i in set(data['ln-1']):
    print(i)
    if type(i) == type(''):
        print(float(i))


def to_float(x):
    try:
        if x.isdigit():
            return float(x)
    except:
        if x == '.':
            return 0
        return x

def series_types(series):
    types = []
    for i in set(series):
        if not type(i) in types:
            types.append(type(i))
    return(types)


data['sy assistments usage'] = data['sy assistments usage'].astype('category')
data['skill'] = data['skill'].astype('category')
data['problemtype'] = data['problemtype'].astype('category')
data['ln-1'] = data['ln-1'].apply(lambda x: to_float(x))
data['ln'] = data['ln'].apply(lambda x: to_float(x))
# data.memory_usage(deep=True)
# data.info(memory_usage='deep')

training = pd.read_csv(path + 'training_label.csv').drop(['AveCorrect'], axis=1)
training.columns = [col.lower() for col in training.columns]
training.shape

# merged data set with isSTEM
df = data.merge(training, on='itest_id', how="left")
df.info()

actions = df[df.isstem.notnull()]
print("training set size: ", training.shape[0], "actions for # of students: ", len(actions.itest_id.unique()))
print("sample size useless for training: ", training.shape[0] - len(actions.itest_id.unique()))

# merged training data set
stem = actions[actions.isstem == 1]
nonstem = actions[actions.isstem == 0]

# all, stem, nonstem
actions.shape, stem.shape, nonstem.shape

all_skill = actions.groupby('skill')

actions.head()

series_types(actions.correct)
series_types(actions.skill)
actions = df[df.isstem.notnull()]
actions['skill'] = actions.skill.astype('category')
actions.info()

tmp = actions[['isstem', 'correct', 'itest_id']]
tmp.head()
#actions[actions.skill.cat.codes==50]['skill'] #<< no skill
tmp1 = actions[['isstem', 'correct', 'itest_id']]
tmp1['skill'] = actions.skill
tmp1['skill'].head()
tmp[tmp['skill']==0].head()
tmp1[tmp1.index==189006]
tmp['skill'] = actions.skill.cat.codes

tmp.head()

#tmp = tmp.merge(training, on='itest_id', how="left")
tmp.head()
stem = tmp[tmp.isstem == 1]
stem_g = stem.groupby(['itest_id', 'skill']).sum()
stem_group = stem_g.groupby(level=1).mean()
stem_group['accuracy'] = stem_group.correct / stem_group.isstem
stem_group.head()
# validation that the logic was correct`
# x = stem[stem.skill==0].groupby('itest_id').sum()['correct']
# x.mean()
nonstem = tmp[tmp.isstem == 0]
nonstem.isstem += 1
nonstem_g = nonstem.groupby(['itest_id', 'skill']).sum()
nonstem_group = nonstem_g.groupby(level=1).mean()
nonstem_group['accuracy'] = nonstem_group.correct / nonstem_group.isstem

nonstem_group.head()
threshold = 10
stem_group1 = stem_group[stem_group.isstem>threshold]
nonstem_group1 = nonstem_group[nonstem_group.isstem>threshold]

plt.plot(stem_group1.index, stem_group1.correct, color='g')
plt.plot(nonstem_group1.index, nonstem_group1.correct, color='r')
plt.show()

plt.plot(stem_group1.index, stem_group1.accuracy, color='g', alpha=0.5)
plt.plot(nonstem_group1.index, nonstem_group1.accuracy, color='r', alpha=0.5)
plt.show()
nonstem_group1.columns = ['nonstem_total', 'nonstem_correct', 'nonstem_accuracy']
stem_group1.columns = ['stem_total', 'stem_correct', 'stem_accuracy']
nonstem_group1.head()
x = stem_group1.merge(nonstem_group1, left_index=True,right_index=True)
x.shape
threshold=10
x_above10 = x[(x.nonstem_total>threshold) | (x.stem_total>threshold)]
x_above10.shape
x.head()
x_above10['diff'] = x_above10.stem_accuracy - x_above10.nonstem_accuracy

plt.plot(x_above10['diff']), plt.show()

accuracy_diff = x_above10['diff']
accuracy_diff[accuracy_diff > 0.1]



list(set(actions.skill))[1]
list(set(actions.skill))[18]
list(set(actions.skill))[35]
list(set(actions.skill))[80]


stem_group_var = stem_g.groupby(level=1).var()
stem_group_var['accuracy'] = stem_group.correct / stem_group.isstem
stem_group


top_advantages  =  [1, 18, 35, 80]
t = 18
for t in top_advantages:
    stem18 = stem[stem.skill==t]
    stem_g2 = stem18.groupby(['itest_id', 'skill']).sum()
    stem_g2['accuracy'] = stem_g2.correct / stem_g2.isstem
    stem_acc_over_10_attempts = stem_g2[stem_g2.isstem>10]


    top_advantages  =  [1, 18, 35, 80]
    nonstem18 = nonstem[nonstem.skill==t]
    nonstem_g2 = nonstem18.groupby(['itest_id', 'skill']).sum()
    nonstem_g2['accuracy'] = nonstem_g2.correct / nonstem_g2.isstem
    nonstem_acc_over_10_attempts = nonstem_g2[nonstem_g2.isstem>10]
    print('Skill #: ', t)
    plt.subplot(211)
    plt.xlim((0, 1))
    sns.boxplot(list(stem_acc_over_10_attempts['accuracy'])), plt.title('STEM'), plt.show()
    plt.subplot(212)
    plt.xlim((0, 1))
    sns.boxplot(list(nonstem_acc_over_10_attempts['accuracy'])), plt.title('NONSTEM'), plt.show()


stem_tmp = tmp[tmp.isstem == 1]
nonstem_tmp = tmp[tmp.isstem == 0]

stem_correct = stem_tmp.groupby('skill').sum()
stem_correct.head()
stem_correct.columns = ['stem_correct', 'total_stem']
nonstem_correct = nonstem_tmp.groupby('skill').sum()
nonstem_correct['isstem'] = nonstem_tmp.groupby('skill').count()['isstem']

nonstem_correct.columns = ['nonstem_correct', 'total_nonstem']
stem_correct.stem_correct.shape

ax = plt.subplot(111)
ax.plot(stem_correct.index, stem_correct.stem_correct, color='g')
ax.plot(nonstem_correct.index, nonstem_correct.nonstem_correct, color='r')
plt.show()



stem_skill = stem.groupby('skill')
stem_skill['correct'].mean()

nonstem_skill = nonstem.groupby('skill')
nonstem_skill['correct'].mean()

cat_comp = pd.DataFrame([list(stem_skill['correct'].mean()), list(nonstem_skill['correct'].mean())]).transpose()
cat_comp['skill'] = pd.DataFrame(list(nonstem_skill['correct'].mean().index))
cat_comp['diff'] = abs(cat_comp[0] / cat_comp[1] - 1)
sorted_ = cat_comp.sort_values(by="diff")
sorted_[sorted_.index == 18]
sorted_[sorted_.index == 35]

sorted_.index = range(cat_comp.shape[0])
sorted_['diff'] += 1
plt.plot(sorted_['diff']), plt.show()
