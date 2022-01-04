# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import math

import matplotlib.pyplot as plt
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
    origDf = pd.read_sql('select * from s_002174 where dateTime >= "20160408" order by dateTime asc', conn)
    conn.close()
    df = origDf[['startPrice', 'maxPrice', 'minPrice']].drop(labels=[len(origDf)-1])
    x = df.values
    y = origDf[['endPrice']].drop(labels=[0])
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, shuffle=False)
    lr = LinearRegression(normalize=False, positive=True)
    lr.fit(train_x, train_y)
    print('coef: {}'.format(lr.coef_))
    predictOfTestY = lr.predict(test_x)
    predictDays = int(math.ceil(0.2 * len(origDf)))
    print(predictOfTestY)

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

    endTime = datetime.datetime.now()
    print('end time: {}'.format(endTime))
    print('total time: {}'.format(endTime - startTime))


try:
    run()
except Exception as e:
    print(str(e))
