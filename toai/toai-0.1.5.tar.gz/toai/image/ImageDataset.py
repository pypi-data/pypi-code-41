import math
import os
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf


class ImageDataset:
    def __init__(
        self,
        batch_size: int,
        img_dims: Tuple[int, int, int],
        regression: bool = False,
        shuffle: bool = False,
        prefetch: int = 1,
        n_parallel_calls: int = -1,
    ):
        self.classes = None
        self.batch_size = batch_size
        self.img_dims = img_dims
        self.regression = regression
        self.shuffle = shuffle
        self.prefetch = prefetch
        self.n_parallel_calls = n_parallel_calls

    def dataset(self, x: np.array, y: np.array):
        self.x = x
        self.y = y
        self.length = len(self.y)
        self.steps = math.ceil(self.length / self.batch_size)
        if not self.regression:
            self.classes = np.unique(self.y)
            self.n_classes = len(self.classes)

    def load_df(
        self, df: pd.DataFrame, path_col: str, label_col: str
    ) -> "ImageDataset":
        self.dataset(df[path_col].values, df[label_col].values)
        return self

    def load_subfolders(self, path: Union[Path, str]) -> "ImageDataset":
        return self

    def load_files_re(
        self,
        path: Union[Path, str],
        regex: str,
        default: Optional[Union[int, float, str, bool]] = None,
    ) -> "ImageDataset":
        paths = []
        labels = []
        for value in os.listdir(path):
            match = re.match(regex, value)
            if match:
                labels.append(match.group(1))
            elif default:
                labels.append(default)
            else:
                raise ValueError(
                    f"No match found and no default value provided for value: {value}"
                )
            paths.append(f"{path}/{value}")

        self.dataset(np.asarray(paths), np.asarray(labels).astype(int))
        return self

    def _preprocess_with_pipeline(
        self, dataset: tf.data.Dataset, pipeline: List[Callable]
    ) -> tf.data.Dataset:
        for fun in pipeline:
            dataset = dataset.map(fun, num_parallel_calls=self.n_parallel_calls)
        return dataset

    def preprocess(
        self,
        image_pipeline: Optional[List[Callable]] = None,
        label_pipeline: Optional[List[Callable]] = None,
    ) -> "ImageDataset":
        self.image_pipeline = image_pipeline or []
        self.label_pipeline = label_pipeline or []

        image_ds = tf.data.Dataset.from_tensor_slices(self.x)
        image_ds = self._preprocess_with_pipeline(image_ds, self.image_pipeline)
        label_ds = tf.data.Dataset.from_tensor_slices(self.y)
        label_ds = self._preprocess_with_pipeline(label_ds, self.label_pipeline)

        dataset = tf.data.Dataset.zip((image_ds, label_ds))
        if self.shuffle:
            dataset = dataset.shuffle(self.batch_size)
        self.data = dataset.repeat().batch(self.batch_size).prefetch(self.prefetch)
        return self

    def show(self, cols: int = 8, n_batches: int = 1):
        if cols >= self.batch_size * n_batches:
            cols = self.batch_size * n_batches
            rows = 1
        else:
            rows = math.ceil(self.batch_size * n_batches / cols)
        _, ax = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
        i = 0
        for x_batch, y_batch in self.data.take(n_batches):
            for (x, y) in zip(x_batch.numpy(), y_batch.numpy()):
                idx = (i // cols, i % cols) if rows > 1 else i % cols
                ax[idx].axis("off")
                ax[idx].imshow(x)
                ax[idx].set_title(y)
                i += 1
