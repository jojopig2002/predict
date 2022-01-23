from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties


class PredictBaseModel:
    def predict(self):
        pass

    def draw(self, code, origDf, predictDf, realDf, step, titlePart):
            ax = plt.gca()
            predictDf.plot(kind='line', x='date', y='predictEndPrice', color='red', ax=ax)
            realDf.plot(kind='line', x='date', y='realEndPrice', color='blue', ax=ax)
            font_set = FontProperties(fname=r"/System/Library/Fonts/STHeiti Medium.ttc", size=10)
            plt.title(titlePart + ': ' + code + ' ' + origDf[['stockName']].values[0][0], fontproperties=font_set)
            major_index = realDf.index[realDf.index % step == 0]
            major_xticks = realDf['date'][realDf.index % step == 0]
            plt.xticks(major_index, major_xticks)
            plt.setp(plt.gca().get_xticklabels(), rotation=30)
            plt.grid(linestyle='dotted')
            plt.show()
