import numpy as np
import pandas as pd
from scipy import stats

# pandas configuration
pd.options.mode.chained_assignment = None  # default='warn'


class Interval(object):
    def fit(self, y_pred=None):
        self.y_pred = y_pred
        try:
            if self.y_pred is None:
                raise Exception("Please specify y-prediction!!")

            s = self.y_pred.std(ddof=1)
            x_bar = self.y_pred.mean()
            n = len(self.y_pred)
            SE = s / np.sqrt(n)
            alpha = 0.05
            DF = n - 1
            t_critical = abs(stats.t.ppf(alpha, DF))
            self.err = t_critical * SE
            self.confidence_interval = (x_bar - self.err, x_bar + self.err)

        except Exception as e:
            raise Exception(e)


class IQROutlier(object):
    def fit(self, series):
        try:
            q25 = series.quantile(0.25)
            q75 = series.quantile(0.75)
            IQR = q75 - q25
            min_threshold = round(q25 - (IQR*1.5), 3)
            max_threshold = round(q75 + (IQR*1.5), 3)
            self.threshold = (min_threshold, max_threshold)
        except Exception as e:
            raise Exception(e)


class SummaryStatistics(object):
    def __init__(self, num_features=None, cat_features=None,
                 y_label=None, include=None, exclude=None):
        self.__num_features = num_features
        self.__cat_features = cat_features
        self.__include = include
        self.__exclude = exclude
        self.__y_label = y_label
        self.__num_dtypes = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        self.__cat_dtypes = ["object", "category"]

    def __numeric(self):
        if self.__num_features is None:
            self.__df_num = self.__df._get_numeric_data()
            # self.__df_num = self.__df.select_dtypes(include=self.__num_dtypes)
        else:
            self.__df_num = self.__df[self.__num_features]

        if not self.__df_num.empty:
            self.__dtype_handler(type="numerical")

            self.num_stats = self.__df_num.describe().T
            # Finding skewness
            self.num_stats["skewness"] = self.__df_num.skew().tolist()
            # Finding kurtosis
            self.num_stats["kurtosis"] = self.__df_num.kurtosis().tolist()
            # Finding missing
            self.num_stats.insert(1, "missing", self.__df_num.isnull().sum().tolist())
            # Finding correlation
            if self.__y_label is not None:
                for col in self.num_stats.index:
                    self.num_stats.loc[col, "correlation"] = self.__df_num[col].corr(self.__df[self.__y_label])

            self.num_correlation = self.__df_num.corr()

    def __categorical(self):
        if self.__cat_features is None:
            self.__df_cat = self.__df.select_dtypes(include=self.__cat_dtypes)
        else:
            self.__df_cat = self.__df[self.__cat_features]

        if not self.__df_cat.empty:
            self.__dtype_handler(type="categorical")
            self.cat_stats = pd.DataFrame(columns=["count", "missing"])
            self.cat_stats["count"] = self.__df_cat.count().tolist()
            self.cat_stats["missing"] = self.__df_cat.isnull().sum().tolist()
            self.cat_stats["unique"] = self.__df_cat.nunique().tolist()
            self.cat_stats.index = self.__df_cat.columns

    def __dtype_handler(self, type="categorical"):
        if type == "categorical":
            for col in self.__df_cat.columns:
                self.__df_cat[col] = self.__df_cat[col].astype("category")
        elif type == "numerical":
            for col in self.__df_num.columns:
                self.__df_num[col] = self.__df_num[col].astype("float")

    def describe(self, df):
        if self.__include is not None:
            self.__df = df[self.__include]
        elif self.__exclude is not None:
            include = [col for col in df.columns if col not in self.__exclude]
            self.__df = df[include]
        else:
            self.__df = df

        self.__numeric()
        self.__categorical()
