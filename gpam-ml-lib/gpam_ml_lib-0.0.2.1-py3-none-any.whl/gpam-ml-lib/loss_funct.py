from keras import backend as K


def dice_coef(y_true, y_pred, smooth=1):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)

    intersetion = K.sum(y_true_f * y_pred_f)
    top = 2 * intersetion * smooth
    bottom = ((K.sum(y_true_f)) + (K.sum(y_pred_f)) + smooth)
    return top / bottom
