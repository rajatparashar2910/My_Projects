# -*- coding: utf-8 -*-
"""
@author:J.Zhou

@contact:zyfzjsc988@outlook.com

@file:count.py

@time:02/12/2017 13:49

@desc:

"""

import csv
import json
import xlrd
import operator
# def max_min_normalize(dic):
#     maxi = max(dic.iteritems(), key=operator.itemgetter(1))[1]
#     mini = min(dic.iteritems(), key=operator.itemgetter(1))[1]
#     for key in dic:
#         dic[key] = (dic[key]-mini)/float(maxi-mini)
#     return dic
def read_csv(filename):
    dic = dict()
    with open(filename) as f:
        f_csv = csv.reader(f)

        for row in f_csv:
            city_name = row[5]
            if city_name != 'local_authority':
                if city_name not in dic:
                    dic[city_name] = 1
                else:
                    dic[city_name] += 1
    # dic = max_min_normalize(dic)
    with open('pubs.json', 'w') as f:
        json.dump(dic, f)



def read_hospitals(filename):
    # 打开文件
    workbook = xlrd.open_workbook(filename)
    dic = dict()
    sheet2 = workbook.sheet_by_index(0)
    for col in sheet2.col_values(3):
        if col not in dic:
            dic[col] = 1
        else:
            dic[col] += 1
    # dic = max_min_normalize(dic)
    with open('hospitals.json', 'w') as f:
        json.dump(dic, f)



def read_education(filename):
    # 打开文件
    workbook = xlrd.open_workbook(filename)
    dic = dict()
    sheet2 = workbook.sheet_by_index(0)
    for col in sheet2.col_values(3):
        if col != '':
            if col not in dic:
                dic[col] = 1
            else:
                dic[col] += 1
    # dic = max_min_normalize(dic)

    with open('education.json', 'w') as f:
        json.dump(dic, f)


def read_station(filename):
    # 打开文件
    dic = dict()
    with open(filename) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            col = row[6]
            if col != '' and col!='District or Unitary Authority':
                p = col.split(' - ')
                if p[0] not in dic:
                    dic[p[0]] = 1
                else:
                    dic[p[0]] += 1

    # dic = max_min_normalize(dic)
    with open('railway_station.json', 'w') as f:
        json.dump(dic, f)


def read_city(filename):
    # 打开文件
    l = list()
    s = set()
    with open(filename) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            town = row[6]
            if town!='town':
                if town =='':
                    town  = row[7]
                if town not in s:
                    l.append({'city_name': town, 'region': row[7], 'latitude': row[4], 'longitude': row[5],
                                      'uk_region': row[8]})
                    s.add(town)
    print(len(l))



    with open('cities.json', 'w') as f:
        json.dump(l, f)

if __name__ == '__main__':
    read_csv('5.open_pubs.csv')
    read_hospitals('6.Hospitals.xlsx')
    read_education('4.Education_2017.xlsx')
    read_station('12.railway-stations.csv')
    # read_city('postcodes_reference.csv')