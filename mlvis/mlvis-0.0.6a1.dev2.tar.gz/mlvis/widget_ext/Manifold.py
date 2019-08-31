from mlvis.widget import CommonComponent
import pandas as pd
import numpy as np

class Manifold(CommonComponent):
    def __init__(self, props={}):
        if 'data' not in props:
            raise Exception('data must be specified')

        valid, data = self.validate_data(props['data'], give_exception=True)
        if not valid:
            raise data
        props['data']['x'] = self.process_x(props['data']['x'])
        props['data']['yPred'] = self.process_y_pred(props['data']['yPred'])
        props['data']['yTrue'] = self.process_y_true(props['data']['yTrue'])
        super(Manifold, self).__init__(props)


    def validate_data(self, data, give_exception=False):
        if not isinstance(data, dict):
            return False if not give_exception else (False, Exception('Data must in dict.'))
        for key in ['x', 'yPred', 'yTrue']:
            if key not in data:
                return False if not give_exception else (False, Exception('Missing data attribute ' + key + '.'))
        for key in data:
            if key not in ['x', 'yPred', 'yTrue']:
                return False if not give_exception else (False, Warning('Unrecognized data attribute ' + key + '.'))
        for key in ['x', 'yTrue']:
            if not (isinstance(data[key], list) or isinstance(data[key], np.ndarray)):
                return False if not give_exception else (False, Exception(key + ' must be a list/ndarray.'))
        if not isinstance(data['yPred'], list):
            return False if not give_exception else (False, Exception(key + ' must be a list.'))
        for key in ['x', 'yPred', 'yTrue']:
            if len(data[key]) == 0:
                return False if not give_exception else (False, Exception(key + ' can not be empty.'))
        for l in data['yPred']:
            if not (isinstance(l, list) or isinstance(l, pd.DataFrame)):
                return False if not give_exception else (False, Exception('Every item in yPred must be list/DataFrame.'))
        return True if not give_exception else (True, data)


    def process_x(self, x):
        """
        Convert the x data frame into the format manifold recognizes
        :param x: A numpy-array/list for the feature list
        :return: A list for the x attribute of the data that with the manifold data format
        """
        if isinstance(x, np.ndarray):
            return x.tolist()
        else:
            return x


    def process_y_pred(self, y_pred):
        """
        Convert y pred feature -- the predictions of each features for each model into the manifold recognized informat
        :param y_pred: A list of data frames. Each data frame is the predict probability of one model,
            which each column being the predicted probability for one class
        :return: A list for the y_pred attribute with the manifold data format
        """
        y_pred_r = [0] * len(y_pred)
        for i, y in enumerate(y_pred):
            if isinstance(y, list):
                y_pred_r[i] = y
            else:
                # using the old school index way to iterate over data frame for fast performance
                y_pred_r[i] = [dict((y.columns[k], y.iloc[j, k]) for k in range(0, y.shape[1])) for j in range(0, y.shape[0])]
        return y_pred_r


    def process_y_true(self, y_true):
        """
        Convert y true feature into the format manifold recognizes
        :param y_true: A numpy-array/list for the ground truth
        :return: A list of the ground truths with the manifold data format
        """
        if isinstance(y_true, np.ndarray):
            return y_true.tolist()
        else:
            return y_true
