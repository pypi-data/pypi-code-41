import pandas as pd
import argparse

from sklearn.metrics import confusion_matrix, mean_absolute_error
from sklearn.utils.multiclass import unique_labels
import matplotlib.pyplot as plt
import numpy as np


# calculates the R of a specific class
def calc_r(tp, np):
    return tp/(tp+np)

#calculates NP of a specific class
def calc_np(cm, tp, row_num):
    np = 0
    for i in range(cm.shape[0]):
        np += cm[row_num][i]
    return np - tp

def calc_mae(cm):
    senior = 8
    young = 1
    adult = 4
    age = {0: adult, 1: senior, 2: young}
    total = 0
    summation = 0

    for i in range(cm.shape[0]):
        for j in range(cm.shape[0]):
            summation += abs(age.get(i) - age.get(j))*cm[i][j]
            total += cm[i][j]

        return summation/total

def calc_ar(cm):
    r = 0
    for i in range(cm.shape[0]):
        tp = cm[i][i]
        np = calc_np(cm, tp, i)
        r += calc_r(tp, np)
    return r/3

def calc_ca(cm):
    sum_right = 0
    sum_all = 0

    for row in range(cm.shape[0]):
        for col in range(cm.shape[0]):
            sum_all += cm[row, col]

    for row in range(cm.shape[0]):
        sum_right += cm[row, row]
    return sum_right / sum_all

def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    #classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax

def get_metrics(data):
    """
    Data -- numpy array the 1st column is expected values, 2nd column is predicted values
    Return: ar, mae, ca 
    """
    cm = confusion_matrix(data[:,0], data[:,1])
    ar = calc_ar(cm)
    mae = calc_mae(cm)
    ca = calc_ca(cm)
    return ar, mae, ca


def main():
    parser = argparse.ArgumentParser(description="Competition validate script")
    parser.add_argument('--report', help="Answers", default="./result.csv")
    args = vars(parser.parse_args())
    result = pd.read_csv(args['report'], index_col=0)
    classes = ['adult', 'senior', 'young']
    data = result.values
    plot_confusion_matrix(data[:,0], data[:,1], classes)
    plt.show()
    ar, mae, ca = get_metrics(data)
    print("AR:", ar)
    print("MAE:", mae)
    print("CA:", ca)

if __name__ == "__main__":
    main()