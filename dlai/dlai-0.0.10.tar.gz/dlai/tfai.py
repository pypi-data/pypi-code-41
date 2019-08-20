import tensorflow as tf
import pandas as pd
from tensorflow import keras
from keras import backend as K
import numpy as np
import matplotlib.pyplot as plt


def deprocess_image(x):
    x -= x.mean()
    x /= (x.std() + 1e-5)
    x *= 0.1

    x += 255
    x = np.clip(x, 0, 1)

    x *= 255
    x = np.clip(x, 0, 255).astype('uint8')
    return x


def visualise_one_filter(model, layer_name, filter_index, size=150):
    """
    Builds a loss function that maximizes the activation of the nth filter of the specified layer.
    To plot filter image use plt.imshow(visualise_one_filter(model, layer_name, filter_index, size=150))
    :param model: trained model.
    :param layer_name: layer you want to visualise.
    :param filter_index: filter index.
    :param size: size of filter
    :return:
    """
    layer_output = model.get_layer(layer_name).output
    loss = K.mean(layer_output[:, :, :, filter_index])

    grads = K.gradients(loss, model.input)[0]
    grads /= (K.sqrt(K.mean(K.square(grads))) + 1e-5)

    iterate = K.function([model.input], [loss, grads])

    input_img_data = np.random.random((1, size, size, 3)) * 20 + 128

    step = 1
    for i in range(40):
        loss_value, grads_value = iterate([input_img_data])
        input_img_data += grads_value * step

    img = input_img_data[0]
    return deprocess_image(img)


def visualise_filters(model, layer_name, size=64, margin=5):
    results = np.zeros((8 * size + 7 * margin, 8 * size + 7 * margin, 3))
    for i in range(8):
        for j in range(8):
            filter_img = visualise_one_filter(model, layer_name, i + (j * 8), size=size)

            horizontal_start = i * size + i * margin
            horizontal_end = horizontal_start + size
            vertical_start = j * size + j * margin
            vertical_end = vertical_start + size
            results[horizontal_start: horizontal_end, vertical_start: vertical_end, :] = filter_img

    plt.figure(figsize=(20, 20))
    plt.imshow(results)

