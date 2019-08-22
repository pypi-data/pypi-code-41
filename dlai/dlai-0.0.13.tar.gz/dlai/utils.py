import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import doctest


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


def plot_df_images(df: pd.DataFrame, target_column: str, cols: int, rows: int) -> None:
    """
    Plots images from Pandas DataFrame column where paths are added.
    :param df: Pandas DataFrame with needed info.
    :param target_column: Column where paths are defined.
    :param cols: How many columns with images you want to plot.
    :param rows: How many rows with images you want to plot.
    :return: None
    """
    # TODO add random and len checking
    pictures = df[target_column].tolist()
    fig = plt.figure(figsize=(5 * cols, 5* rows))
    for i in range(1, cols * rows + 1):
        image = pictures[i - 1]
        if image.find('/'):
            img_name = image.split('/')[-1]
        else:
            img_name = image
        fig.add_subplot(rows, cols, i, title=img_name)
        plt.imshow(Image.open(image))
    plt.show()


if __name__ == '__main__':

    plot_df_images(df, target_column, 3, 1)