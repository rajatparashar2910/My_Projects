from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn import preprocessing


app = Flask(__name__)

MONGO_URL = 'mongodb://data_diggers:data_diggers@cluster0-shard-00-00-07rsk.mongodb.net:27017,cluster0-shard-00-01-07rsk.mongodb.net:27017,cluster0-shard-00-02-07rsk.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin'
client = MongoClient(MONGO_URL)
db = client.data_diggers

# calculate rank from the survey
def calculate_survey_rank(weights, pearson, df):
    multiplier = pearson.copy()
    for key in multiplier.keys():
        if key == 'number_of_universities_per_person':
            multiplier[key] = multiplier[key] * float(weights['Quality of higher education'])
        elif key == 'pubs_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Entertainment'])
        elif key == 'total_jobs_per_person':
            multiplier[key] = multiplier[key] * float(weights['Total Jobs available'])
        elif key == 'school_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Number of schools'])
        elif key == 'stations_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Connectivity to other cities'])
        elif key == 'hospitals_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Number of hospitals'])
        elif (key == 'frostday_peryear') or (key == 'rainfall_permon') or (key == 'summerday_ave_temperature') or (key == 'summernight_ave_temperature') or (key == 'sunshine_permon') or (key == 'winterday_ave_temperature') or (key == 'winternight_ave_temperature'):
            multiplier[key] = multiplier[key] * float(weights['Weather'])
        elif key == 'gva':
            multiplier[key] = multiplier[key] * float(weights['GVA per worker'])
        elif key == 'house_price':
            multiplier[key] = multiplier[key] * float(weights['Flat/House prices'])
        elif key == 'population':
            multiplier[key] = multiplier[key] * float(weights['Population'])
        elif (key == 'road_traffic_2015') or (key == 'road_traffic_2016'):
            multiplier[key] = multiplier[key] * float(weights['Road Traffic'])
        elif key == 'traffic_noise':
            multiplier[key] = multiplier[key] * float(weights['Noise level at night'])
        elif key == 'unemployment':
            multiplier[key] = multiplier[key] * float(weights['Unemployment rate'])

    # calculate the ranking - with for loop
    df['result'] = 0
    for key in multiplier.keys():
        # to numbers
        df[key] = pd.to_numeric(df[key])
        multiplier[key] = float(multiplier[key])

        # calculate
        df['result'] = df['result'] + df[key] * multiplier[key]

    # sort result
    df = df.sort_values(['result'], ascending=False)

    return df['result']

# calculate rank according to user input
def calculate_user_rank(weights, pearson, df):
    multiplier = pearson.copy()
    for key in multiplier.keys():
        if key == 'number_of_universities_per_person':
            multiplier[key] = multiplier[key] * float(weights['Education'])
        elif key == 'pubs_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Entertainment'])
        elif key == 'total_jobs_per_person':
            multiplier[key] = multiplier[key] * float(weights['Jobs'])
        elif key == 'school_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Schools'])
        elif key == 'stations_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Connectivity'])
        elif key == 'hospitals_number_per_person':
            multiplier[key] = multiplier[key] * float(weights['Hospitals'])
        elif (key == 'frostday_peryear') or (key == 'rainfall_permon') or (key == 'summerday_ave_temperature') or (key == 'summernight_ave_temperature') or (key == 'sunshine_permon') or (key == 'winterday_ave_temperature') or (key == 'winternight_ave_temperature'):
            multiplier[key] = multiplier[key] * float(weights['Weather'])
        elif key == 'gva':
            multiplier[key] = multiplier[key] * float(weights['GVA'])
        elif key == 'house_price':
            multiplier[key] = multiplier[key] * float(weights['HousePrice'])
        elif key == 'population':
            multiplier[key] = multiplier[key] * float(weights['Population'])
        elif (key == 'road_traffic_2015') or (key == 'road_traffic_2016'):
            multiplier[key] = multiplier[key] * float(weights['RoadTraffic'])
        elif key == 'traffic_noise':
            multiplier[key] = multiplier[key] * float(weights['Noise'])
        elif key == 'unemployment':
            multiplier[key] = multiplier[key] * float(weights['Unemployment'])

    # calculate the ranking - with for loop
    df['result'] = 0
    for key in multiplier.keys():
        # to numbers
        df[key] = pd.to_numeric(df[key])
        multiplier[key] = float(multiplier[key])

        # calculate
        df['result'] = df['result'] + df[key] * multiplier[key]

    # sort result
    df = df.sort_values(['result'], ascending=False)

    return df


# normalization by z-score
def scaleColumns(df):
    # print(df[:2])
    scaler = preprocessing.StandardScaler()
    matrix = scaler.fit(df).transform(df)
    # print df.index
    cols_to_scale = list(df)
    rows_name = list(df.index)
    df = pd.DataFrame(matrix,columns=cols_to_scale,index=rows_name)
    # print(df[:2])
    return df

# function to calculate cities ranking
def calculatecity(userRequest):
    # read collection
    collection = db.finalCities
    cursor = collection.find()
    listOfData = [c for c in cursor]
    df = pd.DataFrame(listOfData)

    df = df.set_index('city_name')

    # remove unused columns
    df = df.drop(columns=['uk_region', 'region', '_id', 'happiness', 'latitude', 'longitude', 'sample'])
    df = df.fillna(0)

    # generate new normalized columns
    df['number_of_universities_per_person'] = df['number_of_universities'] / df['population']
    df['pubs_number_per_person'] = df['pubs_number'] / df['population']
    df['total_jobs_per_person'] = df['total_jobs'] / df['population']
    df['school_number_per_person'] = df['school_number'] / df['population']
    df['stations_number_per_person'] = df['stations_number'] / df['population']
    df['hospitals_number_per_person'] = df['hospitals_number'] / df['population']

    # remove old columns
    df = df.drop(['hospitals_number', 'pubs_number', 'stations_number', 'school_number', 'total_jobs',
                  'number_of_universities'], axis=1)

    df.to_csv('output.csv')

    # normalize
    df = scaleColumns(df)

    # sort DataFrame alphabetically
    df.columns = [x.lower() for x in df.columns]
    df = df.sort_index(axis=1)

    # read weights
    collection = db.SurveyWeights
    cursor = collection.find()
    weightsList = [c for c in cursor]
    # factors = factors[0]
    # factors.pop('_id')
    # factors = {k.lower(): v for k, v in factors.items()}

    # read Pearson's correlation coefficients
    collection = db.pearsonr_correlation_coefficient
    cursor = collection.find()
    pearsonList = [c for c in cursor]
    pearson = pearsonList[0]
    pearson.pop('_id')
    # sort alphabetically
    pearson = {k.lower(): v for k, v in pearson.items()}
    # drop some keys
    pearson.pop('number_of_universities')
    pearson.pop('pubs_number')
    pearson.pop('total_jobs')
    pearson.pop('school_number')
    pearson.pop('stations_number')
    pearson.pop('hospitals_number')

    # sort Pearson's coefficients
    # factors_np = []
    # for key in sorted(factors.iterkeys()):
    #     factors_np.append(factors[key])
    # factors_np = np.asarray(factors_np)

    # check if there are different column names
    for i in pearson.keys():
        if i in df.columns.values:
            pass
        else:
            print(i)

    # calculate ranking using numpy
    # data = df.values
    # array = np.dot(data, factors_np)
    # print(type(array))
    # print(array)
    # df['result2'] = array
    # df = df.sort_values(['result2'])

    # calculate the ranking - with for loop
    # df['result'] = 0
    # for key in factors.keys():
    #     df[key] = pd.to_numeric(df[key])
    #     factors[key] = float(factors[key])
    #     df['result'] = df['result'] + df[key] * factors[key]
    # df = df.sort_values(['result'])

    # print
    # print(df.count(axis=1))
    # print('----------')
    # print(len(pearson))
    # df.to_csv('output.csv', columns=['result2'])

    # calculate rank according to user input
    df = calculate_user_rank(userRequest, pearson, df)

    # 3 best cities
    best = df[0:3]
    bestList = list(best.index)
    # print(bestList)

    # 3 worst cities
    worst = df[-3:]
    worstList = list(worst.index)
    # print(worstList)
    print(df['result'])

    listUser = bestList + worstList

    collection = db.SurveyWeights

    # calculate rank according to user's age
    if userRequest['Age'] == 'age2':
        myfilter = {'type': 'Weights for 18-25:'}
    elif userRequest['Age'] == 'age3':
        myfilter = {'type': 'Weights for 26-35:'}
    elif userRequest['Age'] == 'age4':
        myfilter = {'type': {'$regex': '.*36.*'}}
    else:
        myfilter = {'type': 'Weights all categories:'}

    cursor = collection.find(myfilter)
    weights = [c for c in cursor]
    weights = weights[0]
    # print(weights)

    res1 = calculate_survey_rank(weights, pearson, df)
    # 3 best cities
    best = res1[0:3]
    bestList = list(best.index)

    # 3 worst cities
    worst = res1[-3:]
    worstList = list(worst.index)

    # print(df['result'])

    listAge = bestList + worstList

    # calculate rank according to user's region
    if userRequest['Gender'] == 'gender_f':
        myfilter = {'type': {'$regex': '.*female.*'}}
    elif userRequest['Gender'] == 'gender_m':
        myfilter = {'type': 'Weights for male only:'}
    else:
        myfilter = {'type': 'Weights all categories:'}

    cursor = collection.find(myfilter)
    weights = [c for c in cursor]
    weights = weights[0]
    # print(weights)

    res1 = calculate_survey_rank(weights, pearson, df)
    # 3 best cities
    best = res1[0:3]
    bestList = list(best.index)

    # 3 worst cities
    worst = res1[-3:]
    worstList = list(worst.index)

    listGender = bestList + worstList

    # calculate rank according to user's Region
    if userRequest['Region'] == 'region_EU':
        myfilter = {'type': {'$regex': '.*Europe.*'}}
    elif userRequest['Region'] == 'region_UK':
        myfilter = {'type': 'Weights for UK:'}
    elif userRequest['Region'] == 'region_Asia':
        myfilter = {'type': {'$regex': '.*Asian.*'}}
    elif userRequest['Region'] == 'region_NA':
        myfilter = {'type': {'$regex': '.*North America.*'}}
    else:
        myfilter = {'type': 'Weights all categories:'}

    cursor = collection.find(myfilter)
    weights = [c for c in cursor]
    weights = weights[0]
    # print(weights)

    res1 = calculate_survey_rank(weights, pearson, df)
    # 3 best cities
    best = res1[0:3]
    bestList = list(best.index)

    # 3 worst cities
    worst = res1[-3:]
    worstList = list(worst.index)

    listRegion = bestList + worstList

    # calculate rank according to user's employment status
    if userRequest['Employment'] == 'work_s1':
        myfilter = {'type': {'$regex': '.*Self-employed.*'}}
    elif userRequest['Employment'] == 'work_s2':
        myfilter = {'Employment': {'$regex': '.*for wages:.*'}}
    elif userRequest['Employment'] == 'work_s3':
        myfilter = {'type': {'$regex': '.*Looking for*'}}
    elif userRequest['Employment'] == 'work_s4':
        myfilter = {'type': {'$regex': '.*Got jobs.*'}}
    elif userRequest['Employment'] == 'work_s5':
        myfilter = {'type': {'$regex': '.*homemaker.*'}}
    elif userRequest['Employment'] == 'work_s6':
        myfilter = {'type': {'$regex': '.*Student.*'}}
    elif userRequest['Employment'] == 'work_s7':
        myfilter = {'type': {'$regex': '.*Military.*'}}
    else:
        myfilter = {'type': {'$regex': '.*IT.*'}}

    cursor = collection.find(myfilter)
    weights = [c for c in cursor]
    weights = weights[0]
    # print(weights)

    res1 = calculate_survey_rank(weights, pearson, df)
    # 3 best cities
    best = res1[0:3]
    bestList = list(best.index)

    # 3 worst cities
    worst = res1[-3:]
    worstList = list(worst.index)

    listEmployment = bestList + worstList

    finalList = []
    finalList.append(listUser)
    finalList.append(listAge)
    finalList.append(listGender)
    finalList.append(listEmployment)
    finalList.append(listRegion)

    return finalList


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/request', methods=['POST'])
def makerequest():
    collection = db.finalCities
    currentResult = collection.find_one()
    # gender = request.form['Gender']
    # age = request.form['Age']
    # region = request.form['Region']
    # employment = request.form['Employment']

    # transform user request
    userRequest = request.form.to_dict()
    print(userRequest)

    # calculate rank according to user input
    cityList = calculatecity(userRequest)
    listUser = cityList[0]
    listAge = cityList[1]
    listGender = cityList[2]
    listEmployment = cityList[3]
    listRegion = cityList[3]

    return render_template('result.html', bestOne=listUser[0], bestTwo=listUser[1], bestThree=listUser[2], worstThree=listUser[3], worstTwo=listUser[4], worstOne=listUser[5],
                           bestOneAge=listAge[0], bestTwoAge=listAge[1], bestThreeAge=listAge[2], worstThreeAge=listAge[3],
                           worstTwoAge=listAge[4], worstOneAge=listAge[5], bestOneGender=listGender[0], bestTwoGender=listGender[1], bestThreeGender=listGender[2], worstThreeGender=listGender[3], worstTwoGender=listGender[4], worstOneGender=listGender[5],
                           bestOneRegion=listRegion[0], bestTwoRegion=listRegion[1], bestThreeRegion=listRegion[2],
                           worstThreeRegion=listRegion[3], worstTwoRegion=listRegion[4], worstOneRegion=listRegion[5],
                           bestOneEmployment=listEmployment[0], bestTwoEmployment=listEmployment[1], bestThreeEmployment=listEmployment[2],
                           worstThreeEmployment=listEmployment[3], worstTwoEmployment=listEmployment[4], worstOneEmployment=listEmployment[5]
                           )


if __name__ == '__main__':
    app.run()
