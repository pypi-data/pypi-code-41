import numpy as np
import copy

class XYNumpyDataPrep(object):

    def __init__(self, options):
        self.modelFeatures = None #options.get("featureColumns", None)
        self.predictFeatures = [options.get("targetFeature", None)]
        self.extraPredictColumns = options.get("extraPredictColumns", [])

    def fill_model_features(self, df):    
        if not self.modelFeatures:
            self.modelFeatures = copy.deepcopy(df.columns)
            if self.predictFeatures:
                self.modelFeatures = [x for x in self.modelFeatures if x not in self.predictFeatures]    

    def split_training(self, df):
        self.fill_model_features(df)

        trainingX = df[self.modelFeatures].astype(np.float32, copy=False)
        trainingY = np.ravel(df[self.predictFeatures].astype(np.float64, copy=False), order='C')
        return trainingX, trainingY

    def split_predict_timeseries(self, df):
        self.fill_model_features(df)

        selected_features = self.modelFeatures + self.extraPredictColumns
        testX = df[selected_features].astype(np.float32, copy=False)
        testY = np.ravel(df[self.predictFeatures].astype(np.float64, copy=False), order='C')
        return testX, testY

    def split_predict(self, df):
        self.fill_model_features(df)

        selected_features = self.modelFeatures + self.extraPredictColumns
        return df[selected_features].astype(np.float32, copy=False)

    def split_score(self, df):
        return self._split_training(df)


class XYNumpyDataPrepFromSpark(XYNumpyDataPrep):

    def _split(self, data, selected_features):
        pData = data.select(selected_features).toPandas()
        return self._split_base(pData)
