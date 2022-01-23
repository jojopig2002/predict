# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

import pymysql as pymysql

from PredictBasedOnNDaysPrices import PredictBasedOnNDaysPrices
from PredictBasedOnOneDayFactors import PredictBasedOnOneDayFactors


def run():
    host = 'localhost'
    user = 'root'
    password = 'memore8111'
    dbname = 'STOCK_DATA_FULL'
    startTime = datetime.datetime.now()
    print('start time: {}'.format(startTime))
    conn = pymysql.connect(host=host, user=user, password=password, db=dbname)
    codes = ['002174', '002460', '300122', '002007', '002250', '601888', '601012', '002978', '605066', '603225']
    # PredictBasedOnOneDayFactors(conn, '002174', daysBeforePredictDay=5, daysDisplayedInChart=200, xStep=5).predict()
    PredictBasedOnNDaysPrices(conn, '603225', basedOnDays=10, daysDisplayedInChart=200, xStep=5,
                              predictDays=5).predict()
    conn.close()
    endTime = datetime.datetime.now()
    print('end time: {}'.format(endTime))
    print('total time: {}'.format(endTime - startTime))


try:
    run()
except Exception as e:
    logging.exception(e)
    print(str(e))
