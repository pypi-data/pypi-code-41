import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import doctest
from typing import Optional
import numpy as np
import math


def check_df_image_size(df: pd.DataFrame, target_column: str) -> None:
    """
    Checks image sizes from Pandas DataFrame and adds two additional columns to it with sizes
    :param df: Pandas dataFrame where you have info.
    :param target_column: Column where paths to images are defined
    :return: None
    """
    col_indx = list(df.columns).index(target_column)
    for i, row in df.iterrows():
        im = Image.open(row[col_indx])
        w, h = im.size
        df.at[i, 'width'] = w
        df.at[i, 'height'] = h
        # df.at[i, 'shape'] = str(f'{w},{h}')


def plot_df_images(
        df: pd.DataFrame,
        path_column: str,
        image_count: int,
        label_column: Optional[str]=None,
        random_plot: Optional[bool]=False,
    ) -> None:
    """
    Plots images from Pandas DataFrame column where paths are added.
    :param df: Pandas DataFrame with needed info.
    :param path_column: Column where paths are defined.
    :param image_count: How many images you want to plot.
    :param label_column: image label if you want to add it to the name.
    :param random_plot: Whether you want to plot images from DataFrame randomly.
    :return: None
    """
    pictures = df[path_column].tolist()
    if image_count < 3:
        cols, rows = (image_count, 1)
    else:
        cols, rows = (3, math.ceil(image_count / 3))
    fig = plt.figure(figsize=(5 * cols, 5 * rows))

    if len(pictures) < image_count:
        image_count = len(pictures)

    if not random_plot:
        images_to_plot = range(image_count)
    else:
        images_to_plot = np.random.choice(range(len(pictures)), image_count, replace=False)

    for i, value in enumerate(images_to_plot):
        image = pictures[value]
        if label_column:
            label = f' / {df[df[path_column] == image][label_column].values[0]}'
        else:
            label = ''
        if image.find('/'):
            img_name = image.split('/')[-1]
        else:
            img_name = image
        fig.add_subplot(rows, cols, i + 1, title=f'{img_name}{label}')
        plt.imshow(Image.open(image))

    plt.show()


if __name__ == '__main__':
    pass
    # plot_df_images(df, target_column, 3, 1)