import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from typing import Optional
from .utils import plot_df_images


def deprocess_image(x):
    x -= x.mean()
    x /= (x.std() + 1e-5)
    x *= 0.1

    x += 255
    x = np.clip(x, 0, 1)

    x *= 255
    x = np.clip(x, 0, 255).astype('uint8')
    return x


def visualize_one_filter(model, layer_name: str, filter_index: int, size=150):
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
    loss = tf.reduce_mean(layer_output[:, :, :, filter_index])

    grads = tf.gradients(loss, model.input)[0]
    grads /= (tf.sqrt(tf.reduce_mean(tf.square(grads))) + 1e-5)

    iterate = tf.function([model.input], [loss, grads])

    input_img_data = np.random.random((1, size, size, 3)) * 20 + 128

    step = 1
    for i in range(40):
        loss_value, grads_value = iterate([input_img_data])
        input_img_data += grads_value * step

    img = input_img_data[0]
    return deprocess_image(img)


def visualize_filters(model, layer_name, size=64, margin=5):
    results = np.zeros((8 * size + 7 * margin, 8 * size + 7 * margin, 3))
    for i in range(8):
        for j in range(8):
            filter_img = visualize_one_filter(model, layer_name, i + (j * 8), size=size)

            horizontal_start = i * size + i * margin
            horizontal_end = horizontal_start + size
            vertical_start = j * size + j * margin
            vertical_end = vertical_start + size
            results[horizontal_start: horizontal_end, vertical_start: vertical_end, :] = filter_img

    plt.figure(figsize=(20, 20))
    plt.imshow(results)


def save_model_json(model_arch_path, model):
    with open(model_arch_path, "w") as f:
        f.write(model.to_json())


def load_model_json(model_arch_path, model_weights_path):
    with open(model_arch_path, "r") as f:
        model = keras.models.model_from_json(f.read())
    model.load_weights(model_weights_path)
    return model


def get_most_confused(
        df: pd.DataFrame,
        path_column: str,
        predictions: np.array,
        labels: np.array,
        image_count: int,
        difference_rate: Optional[float]=None,
        plot: Optional[bool]=True,
        random_plot: Optional[bool]=True,
    ) -> pd.DataFrame:
    """
    Plots given number of images from DataFrame, which predicted values differs from real values
    by specified difference_rate.
    :param df: DataFrame you use for predictions.
    :param path_column: Column where image paths are specified
    :param predictions: Predictions tensor.
    :param labels: Label tensor.
    :param image_count: number of images you want to plot
    :param difference_rate: percentage of difference between predicted and real values (0-1)
    :param plot: If True images are plotted, otherwise returns pd.DataFrame. Default True
    :param random_plot: If True selects images randomly. Default True
    :return: pd.DataFrame
    """
    max_predictions = predictions.argmax(axis=1)
    data = {
        'pred_label / label / df_label': [],
        'image': []
    }
    for i, (a, b, c) in enumerate(zip(max_predictions, labels, df['AdoptionSpeed'].tolist())):
        if not difference_rate:
            if a != b:
                data['pred_label / label / df_label'].append(f'{a} / {b} / {c}')
                data['image'].append(df.iloc[i].image)
        else:
            y_hat = int(a)
            y = int(b)
            if predictions[i][y_hat] - predictions[i][y] >= difference_rate:
                predicted = str(round(predictions[i][y_hat], 4))
                real_class = str(round(predictions[i][y], 4))
                data['pred_label / label / df_label'].append(f'{y_hat}: {predicted} / {y}: {real_class} / {c}')
                data['image'].append(df.iloc[i].image)

    confused_df = pd.DataFrame(data)

    if not plot:
        return confused_df

    print(
        f'From {len(df)} images of tested dataframe {len(confused_df)} images were predicted incorrectly with the difference_rate = {difference_rate}.\n')
    plot_df_images(confused_df, 'image', image_count, 'pred_label / label / df_label', random_plot=random_plot)



# TODO create class with predictions: do evaluate, predict, test_labels, plot_most_confused??
# TODO check fast.ai API to cleanup dataset

if __name__ == '__main__':
    layer_name = 'block1_conv1'
    filter_index = 0
    # plt.imshow(visualise_one_filter(model, layer_name, filter_index, size=150))