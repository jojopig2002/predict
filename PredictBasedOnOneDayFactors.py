import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from PredictBaseModel import PredictBaseModel


class PredictBasedOnOneDayFactors(PredictBaseModel):
    def __init__(self, conn, code, daysBeforePredictDay, daysDisplayedInChart, xStep):
        self.conn = conn
        self.code = code
        self.daysBeforePredictDay = daysBeforePredictDay
        self.daysDisplayedInChart = daysDisplayedInChart
        self.xStep = xStep

    def predict(self):
        origDf = pd.read_sql('select * from s_' + self.code + ' order by dateTime asc', self.conn)
        df = origDf[['startPrice', 'maxPrice', 'endPrice', 'diffPrice', 'diffPercent', 'turnoverAmount', 'amount',
                     'amplitude', 'turnoverPercent']]
        indexToRemoveInX = []
        indexToRemoveInY = []
        for i in range(self.daysBeforePredictDay):
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
                        df.values[len(origDf) - self.daysBeforePredictDay - 1][j] * lr.coef_[0][j]
        print(
            '{} predict price from human calculation: {}'.format(
                origDf.loc[len(origDf) - self.daysBeforePredictDay, 'dateTime'],
                lastPrice + c))
        print('{} predict price from machine calculation: {}'.format(
            origDf.loc[len(origDf) - self.daysBeforePredictDay, 'dateTime'],
            predictOfTestY[len(predictOfTestY) - 1][0]))
        predictDf = pd.DataFrame()
        realDf = pd.DataFrame()
        # for i in range(daysBeforePredictDay):
        #     predictPrice = 0
        #     for j in range(lr.coef_.size):
        #         predictPrice = predictPrice + \
        #                        df.values[len(origDf) - daysBeforePredictDay + i][j] * lr.coef_[0][j]
        #         predictDf.loc[i, 'date'] = origDf.loc[len(origDf) - daysBeforePredictDay + i, 'dateTime'][5:]
        #         predictDf.loc[i, 'predictEndPrice'] = origDf.loc[len(origDf) - daysBeforePredictDay + i, 'endPrice']
        #         realDf.loc[i, 'date'] = origDf.loc[len(origDf) - daysBeforePredictDay + i, 'dateTime'][5:]
        #         realDf.loc[i, 'realEndPrice'] = origDf.loc[len(origDf) - daysBeforePredictDay + i, 'endPrice']
        #         predictDf.loc[i + daysBeforePredictDay, 'date'] = 'Day ' + str(i + 1)
        #         predictDf.loc[i + daysBeforePredictDay, 'predictEndPrice'] = predictPrice + c
        #     print('stock {} {}, predict day {} price: {}'.format(code, origDf[['stockName']].values[0][0], i + 1,
        #                                                          predictPrice + c))
        # predictDf = predictDf.sort_index(ascending=True)
        index = 0
        j = self.daysDisplayedInChart - 1
        for i in range(self.daysDisplayedInChart - 1, -1, -1):
            realDf.loc[index, 'realEndPrice'] = float(origDf.loc[len(origDf) - 1 - i, 'endPrice'])
            realDf.loc[index, 'date'] = origDf.loc[len(origDf) - 1 - i, 'dateTime']
            print('date: {}'.format(origDf.loc[len(origDf) - 1 - i, 'dateTime']))
            predictDf.loc[index, 'predictEndPrice'] = round(float(predictOfTestY[len(predictOfTestY) - 1 - j][0]), 2)
            print('predicted by machine: {}'.format(predictDf.loc[index, 'predictEndPrice']))
            predictVal = 0
            for m in range(lr.coef_.size):
                predictVal = predictVal + test_x[len(predictOfTestY) - 1 - j][m] * lr.coef_[0][m]
            print('predicted by human: {}'.format(predictVal + lr.intercept_))
            print('actual: {}'.format(realDf.loc[index, 'realEndPrice']))
            if index >= 1:
                print(
                    'diff: {}'.format(predictDf.loc[index, 'predictEndPrice'] - realDf.loc[index - 1, 'realEndPrice']))
            predictDf.loc[index, 'date'] = origDf.loc[len(origDf) - 1 - i, 'dateTime']
            j -= 1
            index += 1
        self.draw(self.code, origDf, predictDf, realDf, self.xStep, 'Based on one day')
