import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels


def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap="Blues",
                          ax=None):
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
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    if not ax:
        fig, ax = plt.subplots()

    # We need to reverse rows of the `cm`, because `imshow` will flip it back during displaying. We also reverse order
    # of `yticklabels` below to match this behaviour
    ccm = np.flip(cm, axis=0)

    im = ax.imshow(ccm, cmap=cmap)
    ax.figure.colorbar(im, ax=ax)

    # We want to show all ticks...
    ax.set(xticks=np.arange(ccm.shape[1]),
           yticks=np.arange(ccm.shape[0]),
           # ... extend both axis in order to display all the squares
           xlim=[-.5, ccm.shape[0] - .5],
           ylim=[-.5, ccm.shape[1] - .5],
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes[::-1],
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = ccm.max() / 2.
    for i in range(ccm.shape[0]):
        for j in range(ccm.shape[1]):
            ax.text(j, i, format(ccm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if ccm[i, j] > thresh else "black")

    if not ax:
        ax.figure.tight_layout()

    return ax, cm
