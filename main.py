# !/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

import pymysql as pymysql

from PredictBasedOnNDays import PredictBasedOnNDays
from PredictBasedOnOneDay import PredictBasedOnOneDay


def run():
    host = 'localhost'
    user = 'root'
    password = 'memore8111'
    dbname = 'STOCK_DATA_FULL'
    startTime = datetime.datetime.now()
    print('start time: {}'.format(startTime))
    conn = pymysql.connect(host=host, user=user, password=password, db=dbname)
    codes = ['002174', '002460', '300122', '000725', '000100', '002047', '002699', '000665', '600847', '605289']
    # PredictBasedOnOneDay(conn, '002174', daysBeforePredictDay=5, daysDisplayedInChart=200, xStep=5).predict()
    PredictBasedOnNDays(conn, '002174', basedOnDays=5, daysDisplayedInChart=200, xStep=5).predict()
    conn.close()
    endTime = datetime.datetime.now()
    print('end time: {}'.format(endTime))
    print('total time: {}'.format(endTime - startTime))


try:
    run()
except Exception as e:
    logging.exception(e)
    print(str(e))
