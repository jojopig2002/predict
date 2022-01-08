# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import pandas as pd
import pymysql as pymysql
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def run():
    host = 'localhost'
    user = 'root'
    password = 'memore8111'
    dbname = 'STOCK_DATA_FULL'
    startTime = datetime.datetime.now()
    print('start time: {}'.format(startTime))
    conn = pymysql.connect(host=host, user=user, password=password, db=dbname)
    codes = ['002174', '002460', '300122', '000725', '000100', '002047', '002699', '000665', '600847', '605289']
    predictDays = 30
    # for i in range(len(codes)):
    #     predict(conn, codes[i], predictDays)
    predict(conn, '002174', 10)
    conn.close()
    endTime = datetime.datetime.now()
    print('end time: {}'.format(endTime))
    print('total time: {}'.format(endTime - startTime))


def predict(conn, code, predictDays):
    origDf = pd.read_sql('select * from s_' + code + ' order by dateTime asc', conn)
    df = origDf[['startPrice', 'maxPrice', 'endPrice', 'diffPrice', 'diffPercent', 'turnoverAmount', 'amount',
                 'amplitude', 'turnoverPercent']]
    indexToRemoveInX = []
    indexToRemoveInY = []
    for i in range(predictDays):
        indexToRemoveInX.append(len(origDf) - i - 1)
        indexToRemoveInY.append(i)
    x = df.drop(labels=indexToRemoveInX).values
    y = origDf[['endPrice']].drop(labels=indexToRemoveInY).values
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, shuffle=False)
    lr = LinearRegression(normalize=False, positive=True)
    lr.fit(train_x, train_y)
    print('coef: {}'.format(lr.coef_))
    predictOfTestY = lr.predict(test_x)
    total = 0
    for j in range(lr.coef_.size):
        total = total + lr.coef_[0][j] * test_x[0][j]
    c = predictOfTestY[0][0] - total
    print('constant: {}'.format(c))
    lastPrice = 0
    for j in range(lr.coef_.size):
        lastPrice = lastPrice + \
                    df.values[len(origDf) - predictDays - 1][j] * lr.coef_[0][j]
    print('{} predict price from human calculation: {}'.format(origDf.values[len(origDf) - predictDays][1],
                                                               lastPrice + c))
    print('{} predict price from machine calculation: {}'.format(origDf.values[len(origDf) - predictDays][1],
                                                                 predictOfTestY[len(predictOfTestY) - 1][0]))
    predictDf = pd.DataFrame()
    realDf = pd.DataFrame()
    for i in range(predictDays):
        predictPrice = 0
        for j in range(lr.coef_.size):
            predictPrice = predictPrice + \
                           df.values[len(origDf) - predictDays + i][j] * lr.coef_[0][j]
            predictDf.loc[i, 'date'] = origDf.values[len(origDf) - predictDays + i, 1][5:]
            predictDf.loc[i, 'predictEndPrice'] = origDf.values[len(origDf) - predictDays + i, 5]
            realDf.loc[i, 'date'] = origDf.values[len(origDf) - predictDays + i, 1][5:]
            realDf.loc[i, 'realEndPrice'] = origDf.values[len(origDf) - predictDays + i, 5]
            predictDf.loc[i + predictDays, 'date'] = 'Day ' + str(i + 1)
            predictDf.loc[i + predictDays, 'predictEndPrice'] = predictPrice + c
        print('stock {} {}, predict day {} price: {}'.format(code, origDf[['stockName']].values[0][0], i + 1,
                                                             predictPrice + c))
    draw(code, origDf, predictDf, realDf)


def draw(code, origDf, predictDf, realDf):
    predictDf = predictDf.sort_index(ascending=True)
    ax = plt.gca()
    predictDf.plot(kind='line', x='date', y='predictEndPrice', color='red', ax=ax)
    realDf.plot(kind='line', x='date', y='realEndPrice', color='blue', ax=ax)
    font_set = FontProperties(fname=r"/System/Library/Fonts/STHeiti Medium.ttc", size=10)
    plt.title(code + ' ' + origDf[['stockName']].values[0][0], fontproperties=font_set)
    major_index = predictDf.index[predictDf.index % 1 == 0]
    major_xtics = predictDf['date'][predictDf.index % 1 == 0]
    plt.xticks(major_index, major_xtics)
    plt.setp(plt.gca().get_xticklabels(), rotation=30)
    plt.grid(linestyle='dotted')
    plt.show()


try:
    run()
except Exception as e:
    print(str(e))
