# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import pandas as pd
import pymysql as pymysql
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
    predictDays = 15
    for i in range(len(codes)):
        predict(conn, codes[i], predictDays)
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
    print('last predict price from human calculation: {}'.format(lastPrice + c))
    print('last predict price from machine calculation: {}'.format(predictOfTestY[len(predictOfTestY) - 1][0]))
    for i in range(predictDays):
        predictPrice = 0
        for j in range(lr.coef_.size):
            predictPrice = predictPrice + \
                           df.values[len(origDf) - i - 1][j] * lr.coef_[0][j]
        print('stock {} day {} price: {}'.format(origDf[['stockName']].values[0][0], predictDays - i, predictPrice + c))


# print(predictOfTestY)

# # 组装数据
# index = 0
# # 在前80%的交易日中，设置预测结果和收盘价一致
# while index < len(origDf) - predictDays:
#     df.loc[index, 'predictedVal'] = origDf.loc[index, 'endPrice']
#     df.loc[index, 'dateTime'] = origDf.loc[index, 'dateTime']
#     index = index + 1
#
# # 在后20%的交易日中，用测试集推算预测股价
# predictedCnt = 0
# while predictedCnt < predictDays:
#     if index >= len(df):
#         break
#     df.loc[index, 'predictedVal'] = predictOfTestY[predictedCnt]
#     df.loc[index, 'dateTime'] = origDf.loc[index, 'dateTime']
#     predictedCnt = predictedCnt + 1
#     index = index + 1

# plt.figure()
# data1 = {
#     "a": [1, 2, 3],
#     "b": [4, 5, 6],
#     "c": [7, 8, 9]
# }
# df1 = pd.DataFrame(data1)
# # df['predictedVal'].plot(color="red", label='predicted Data')
# df1['a'].plot(color="blue", label='Real Data')
# plt.legend(loc='best')  # 绘制图例
# # 设置x坐标的标签
# major_index = origDf.index[origDf.index % 10 == 0]
# major_xtics = origDf['dateTime'][origDf.index % 10 == 0]
# plt.xticks(major_index, major_xtics)
# plt.setp(plt.gca().get_xticklabels(), rotation=30)
# # 带网格线，且设置了网格样式
# plt.grid(linestyle='-.')
# plt.show()


try:
    run()
except Exception as e:
    print(str(e))
