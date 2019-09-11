from imblearn.over_sampling import ADASYN
from imblearn.over_sampling import SMOTE
from imblearn.over_sampling import SMOTENC
import operator
import pandas as pd


class Sampling(object):
    def __init__(self, num_features=[], cat_features=[],
                 technique="SMOTE", sampling_percent=50):
        self.num_features = num_features
        self.cat_features = cat_features
        self.__sampling_percent = sampling_percent
        self.technique = technique

        if self.num_features == []:
            raise Exception("Numerical features must be passed!!")

    def __find_sampling_ratio(self, y):
        print("Detecting class imbalance..")
        label_counts = y.value_counts().reset_index()
        self.ratio = dict(zip(label_counts.iloc[:, 0],
                              label_counts.iloc[:, 1]))
        max_key = max(self.ratio.items(), key=operator.itemgetter(1))[0]
        min_key = [key for key in self.ratio.keys() if key != max_key][0]
        self.sampling_threshold = int(self.ratio[max_key]*self.__sampling_percent)
        if self.sampling_threshold > self.ratio[min_key]:
            print("Class imbalance detected.")
            self.ratio[min_key] = self.sampling_threshold
            return True
        else:
            print("No class imbalance Detected!!")
            return False


    def fit_transform(self, X, y):
        try:
            FLAG = self.__find_sampling_ratio(y)
            if FLAG:
                cols = self.cat_features + self.num_features

                if self.cat_features != []:
                    X = X[cols]
                    cat_features_range = len(self.cat_features)

                    sampling = SMOTENC(categorical_features=
                                       [i for i in range(cat_features_range)],
                                       sampling_strategy=self.ratio,
                                       random_state=42, k_neighbors=5, n_jobs=-1)
                else:
                    if self.technique == "SMOTE":
                        sampling = SMOTE(ratio=self.ratio, n_jobs=-1,
                                         random_state=42)
                    elif self.technique == "ADASYN":
                        sampling = ADASYN(ratio=self.ratio,
                                          random_state=42)

                X, y = sampling.fit_resample(X, y)
                X = pd.DataFrame(X, columns=cols)
                y = pd.Series(y)

            return X, y

        except Exception as e:
            raise Exception(e)

if __name__ == "__main__":
    data = {"amount": [200, 300, 400, 500, 600, 700, 150, 340, 550, 420, 610, 330],
            "trans_count": [1, 5, 12, 2, 4, 5, 7, 11, 15, 20, 2, 11]}
    X = pd.DataFrame(data)
    y = pd.Series([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0])
    s = Sampling(num_features=["amount", "trans_count"])
    X_samp, y_samp = s.fit_transform(X, y)
