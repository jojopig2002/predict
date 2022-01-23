import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from PredictBaseModel import PredictBaseModel


class PredictBasedOnNDays(PredictBaseModel):
    def __init__(self, conn, code, basedOnDays, daysDisplayedInChart, xStep):
        self.conn = conn
        self.code = code
        self.basedOnDays = basedOnDays
        self.daysDisplayedInChart = daysDisplayedInChart
        self.xStep = xStep

    def predict(self):
        origDf = pd.read_sql('select * from s_' + self.code + ' order by dateTime asc', self.conn)
        df = origDf[['dateTime', 'startPrice', 'maxPrice', 'endPrice', 'diffPrice', 'diffPercent', 'turnoverAmount',
                     'amount', 'amplitude', 'turnoverPercent']]
        dataDf = pd.DataFrame()
        index = 0
        for i in range(len(df) - 1, -1, -1):
            if i - self.basedOnDays < 0:
                break
            for j in range(1, self.basedOnDays + 1):
                dataDf.loc[index, 'day-' + str(j)] = df.loc[i + j - self.basedOnDays - 1, 'endPrice']
            dataDf.loc[index, 'endPrice'] = df.loc[i, 'endPrice']
            dataDf.loc[index, 'dateTime'] = df.loc[i, 'dateTime']
            index += 1
        factors = []
        for i in range(1, self.basedOnDays + 1):
            factors.append('day-' + str(i))
        x = dataDf[factors].sort_index(ascending=False).values
        y = dataDf[['endPrice']].sort_index(ascending=False).values
        train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.2, shuffle=False)
        lr = LinearRegression(normalize=False, positive=True)
        lr.fit(train_x, train_y)
        print('coef: {}'.format(lr.coef_))
        print('intercept: {}'.format(lr.intercept_))
        predictOfTestY = lr.predict(test_x)
        predictDf = pd.DataFrame()
        realDf = pd.DataFrame()
        index = 0
        j = self.daysDisplayedInChart - 1
        for i in range(self.daysDisplayedInChart - 1, -1, -1):
            realDf.loc[index, 'realEndPrice'] = float(dataDf.loc[i, 'endPrice'])
            realDf.loc[index, 'date'] = dataDf.loc[i, 'dateTime']
            print('date: {}'.format(dataDf.loc[i, 'dateTime']))
            if len(predictOfTestY) - 1 - j + 1 <= len(predictOfTestY) - 1:
                predictDf.loc[index, 'predictEndPrice'] = round(
                    float(predictOfTestY[len(predictOfTestY) - 1 - j + 1][0]), 2)
                print('predicted by machine: {}'.format(predictDf.loc[index, 'predictEndPrice']))
                predictVal = 0
                for m in range(lr.coef_.size):
                    predictVal = predictVal + test_x[len(predictOfTestY) - 1 - j + 1][m] * lr.coef_[0][m]
                print('predicted by human: {}'.format(predictVal + lr.intercept_))
                print('actual: {}'.format(realDf.loc[index, 'realEndPrice']))
                if index >= 1:
                    print(
                        'diff: {}'.format(predictDf.loc[index, 'predictEndPrice'] - realDf.loc[index, 'realEndPrice']))
                predictDf.loc[index, 'date'] = dataDf.loc[i, 'dateTime']
            j -= 1
            index += 1
        self.draw(self.code, origDf, predictDf, realDf, self.xStep, 'Based on ' + str(self.basedOnDays) + ' days')
