'''
Script to build,train and save TIME SERIES REGRESSION models.
As of July 10th, the data are being read from a .csv in the same path
TO CHANGE ---> Data should be queried from BigQuery instead
1. Downloading the data
2. Prep data for time series abalysis
3. Build different models archictecture
4. Train the models
5. Evaluate the models
6. Save the models for further valdiation
From Open, lose, high, low and volume of 30 stocks, I want to predict the close price of one stock in particular)
We will want to save different python objecs
1. the trained models (architecture and weights)
2. the scaler for each stock
3. the training and testing datasets
'''

import numpy as np
from sklearn.preprocessing import MinMaxScaler



def dataset_preparation(dataset, date, look_back_x, look_forward_y, target, test_fraction, validation_fraction):
    """
    Function used to generate data used for training model
    :param dataset: X input (DF)
    :param date: REQUIRED. SERIES. date_index (Series)
    :param look_back_x: REQUIRED. INTEGER. Depends on window (look_back)(Int)
    :param look_forward_y: REQUIRED. INTEGER.
    :param target: REQUIRED. SERIES. Target series.
    :param test_fraction: REQUIRED. FLOAT. ∈ [0,1]. Represents fraction of dataset to use for test dataset
    :param validation_fraction: REQUIRED. FLOAT. ∈ [0,1]. Represents fraction of dataset to use for validation dataset
    :return: predDate : date_predicted on training (Series), predX : all features of training (DF)
     , trainX : random subsamples of DF used for trainning of X (3 dimension df),
     testX : testfeatures, periods : dictionnary containing test data for all models,
      scaler: function to scale data, s : function to scale data (to use for prediction)

    The training and testting datasets are all in the first (1-validation_fraction) percent of the total dataset
    The targets of validation dataset are all consecutive dates, in the futur
    """


    predX, trainX, testX, validX = [], [], [], []
    predY_1, trainY_1, testY_1, validY_1 = [], [], [], []
    predDate = []

    # create random index for training, testing and validation
    # Validation is the last percentage of dataset
    random_index = np.array(range(len(dataset)))
    valid_index = random_index[int(len(dataset) * (1 - validation_fraction)):]
    random_index = np.delete(random_index, valid_index)
    np.random.shuffle(random_index)

    split_train = int(random_index.shape[0] * (1 - test_fraction - validation_fraction) / (1 - validation_fraction))
    split_test = int(random_index.shape[0] * test_fraction)

    train_index = random_index[: split_train]
    test_index = random_index[split_train:]

    # normalize X
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(dataset.values)
    dataset_scaled = scaler.transform(dataset)

    forward = look_forward_y - 1

    for i in range(0, dataset_scaled.shape[0]):

        if ((i <= look_back_x) or ((len(dataset) - i) < look_forward_y)):
            continue

        x = dataset_scaled[(i - 1 - look_back_x):(i - 1), :]
        predX.append(x)
        predDate.append(date[i])

        y_1 = target[i + forward]

        predY_1.append(y_1)

        # Training data
        if i in train_index:
            x = dataset_scaled[(i - 1 - look_back_x):(i - 1), :]
            trainX.append(x)
            y_1 = target[i + forward]
            trainY_1.append(y_1)


        # Testing data
        elif i in test_index:
            x = dataset_scaled[(i - 1 - look_back_x):(i - 1), :]
            testX.append(x)
            y_1 = target[i + forward]
            testY_1.append(y_1)


        # Validation data
        elif i in valid_index:
            x = dataset_scaled[(i - 1 - look_back_x):(i - 1), :]
            validX.append(x)
            y_1 = target[i + forward]
            validY_1.append(y_1)

    # transform and normalize y into arrays
    predX, trainX, testX, validX = np.array(predX), np.array(trainX), np.array(testX), np.array(validX)
    predY_1, trainY_1, testY_1, validY_1 = np.array(predY_1), np.array(trainY_1), np.array(testY_1), np.array(validY_1)

    # normalize the dataset
    s = MinMaxScaler(feature_range=(0, 1))
    s.fit(np.array(target).reshape(-1, 1))
    predY_1, trainY_1, testY_1, validY_1 = s.transform(predY_1.reshape(-1, 1)), s.transform(
        trainY_1.reshape(-1, 1)), s.transform(
        testY_1.reshape(-1, 1)), s.transform(validY_1.reshape(-1, 1))


    periods = {1: [predY_1, trainY_1, testY_1, validY_1]}

    return predDate, predX, trainX, testX, validX, periods, scaler, s

