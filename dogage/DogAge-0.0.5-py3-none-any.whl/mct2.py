import json
import os
import csv
import argparse
import numpy as np
import pandas as pd
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from tqdm import tqdm

class Classificator():
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self._classes = config['classes']
        self._num_classes = len(self._classes)
        self._data_folder = config['data']
        self._results = config['results']

        self._dataset = os.listdir(self._data_folder)
        self._images = []
        self._answers = self.load_results(self._results)
        print(self._answers)
        if self._answers is None:
            self._answers = pd.DataFrame()
            print("Have not old results")
        processed_files = self._answers.index
        print(processed_files)
        for im_name in tqdm(self._dataset):
            im_path = os.path.join(self._data_folder, im_name)
            if os.path.isfile(im_path) and not(im_name in processed_files):
                im = Image.open(im_path)
                im.thumbnail((256, 256), Image.ANTIALIAS)
                self._images.append({"im" : im, "filename" : im_name})

        self._preducted_values = []
        self._buttons = []
        self._save_and_close_button = None
        self._current_image = self._images.pop()

    def get_callback(self, i):
        return lambda event: self.on_select(event, i)

    def init_gui(self):
        fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)
        im = self._current_image['im']

        self.im_ax = plt.imshow(im)
        for i, name in enumerate(self._classes):
            ax_b = plt.axes([0.2+0.1 * i, 0.05, 0.1, 0.075])
            b = Button(ax_b, name)
            b.on_clicked(self.get_callback(i))

            self._buttons.append(b)

        ax_b = plt.axes([0.8, 0.05, 0.15, 0.075])
        b = Button(ax_b, "Save&Exit")
        b.on_clicked(self.save_and_close)
        self._save_and_close_button = b
        plt.show()

    def on_select(self, event, i):
        plt.sca(self.ax)
        self._preducted_values.append({"filename" : self._current_image["filename"], "answer":i})
        try:
            self._current_image = self._images.pop()
        except IndexError:
            self.save_result()
            return
        im = self._current_image['im']
        self.im_ax = plt.imshow(im)
        return

    def load_results(self, file_name):
        results = None
        if os.path.isfile(file_name):
            results = pd.read_csv(file_name, index_col=0)
        return results

    def save_and_close(self, event):
        self.save_result()

    def save_result(self):
        predicted = self._preducted_values
        predicted = pd.DataFrame(predicted)
        predicted = predicted.set_index('filename')
        self._answers = self._answers.append(predicted)
        self._answers = self._answers.loc[~self._answers.index.duplicated(keep='first')]
        self._answers.to_csv(self._results)
        exit()


def main():
    src_path = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(src_path, 'config.json')
    parser = argparse.ArgumentParser(description="Manual classificator tool")
    parser.add_argument('--config', help="configuration file", default=default_config)
    args = vars(parser.parse_args())
    classificator = None
    classificator = Classificator(args["config"])
    classificator.init_gui()

if __name__ == "__main__":
    main()
