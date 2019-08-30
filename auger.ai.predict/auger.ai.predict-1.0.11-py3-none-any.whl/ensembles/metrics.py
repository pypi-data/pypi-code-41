from sklearn.metrics import *


def neg_log_loss(y_true, y_pred):
    return -log_loss(y_true, y_pred)


# =============== Regression Scores ===============

def neg_mean_squared_error_score(y_true, y_pred):
    return -mean_squared_error(y_true, y_pred)


def neg_mean_squared_log_error_score(y_true, y_pred):
    return -mean_squared_log_error(y_true, y_pred)


def neg_mean_absolute_error_score(y_true, y_pred):
    return -mean_absolute_error(y_true, y_pred)


def neg_median_absolute_error_score(y_true, y_pred):
    return -median_absolute_error(y_true, y_pred)
