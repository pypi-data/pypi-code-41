import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt


def check_df_image_size(df, target_column):
    col_indx = list(df.columns).index(target_column)
    for i, row in df.iterrows():
        im = Image.open(row[col_indx])
        w, h = im.size
        df.at[i, 'width'] = w
        df.at[i, 'height'] = h
        # df.at[i, 'shape'] = str(f'{w},{h}')


def plot_df_images(df, target_column, cols: int, rows: int) -> None:
    pictures = df[target_column].tolist()
    fig = plt.figure(figsize=(5 * cols, 5* rows))
    for i in range(1, cols * rows + 1):
        image = pictures[i - 1]
        img_name = image.split('/')[-1]
        fig.add_subplot(rows, cols, i, title=img_name)
        plt.imshow(Image.open(image))
    plt.show()