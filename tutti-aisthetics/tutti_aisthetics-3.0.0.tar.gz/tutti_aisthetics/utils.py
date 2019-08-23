import json
import pathlib
from typing import List, Dict, Union, Any, Tuple

import numpy as np
import tensorflow as tf


def load_json(file_path: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Read a json file into a Python object

    :param file_path: name of the file to read
    :return: python object with the processed json contents
    """
    with open(file_path, 'r') as fd:
        return json.load(fd)


def save_json(data: Union[List[Dict[str, str]], Dict[str, str]], target_file: str) -> None:
    """
    Save a data object (a dict or a list of dicts) in json format

    :param data: data to store
    :param target_file: name of the output file
    :return: nothing
    """
    with open(target_file, 'w') as fd:
        json.dump(data, fd, indent=2, sort_keys=True)


def random_crop(img: np.ndarray, crop_dims: Tuple[int, int]) -> np.ndarray:
    """
    Crop an image randomly into the given dimensions

    :param img: image array
    :param crop_dims: final dimensions of the image
    :return: cropped image array
    """
    h, w = img.shape[0], img.shape[1]
    ch, cw = crop_dims[0], crop_dims[1]
    assert h >= ch, 'image height is less than crop height'
    assert w >= cw, 'image width is less than crop width'
    x = np.random.randint(0, w - cw + 1)
    y = np.random.randint(0, h - ch + 1)
    return img[y:(y + ch), x:(x + cw), :]


def random_horizontal_flip(img: np.ndarray) -> np.ndarray:
    """
    Apply a horizontal flip to an image with a 50% probability

    :param img: image array
    :return: same image with 50% probability of being horizontally flipped
    """
    assert len(img.shape) == 3, 'input tensor must have 3 dimensions (height, width, channels)'
    assert img.shape[2] == 3, 'image not in channels last format'
    if np.random.random() < 0.5:
        img = img.swapaxes(1, 0)
        img = img[::-1, ...]
        img = img.swapaxes(0, 1)
    return img


def load_image(img_file: str, target_size: Tuple[int, int]) -> np.ndarray:
    """ Load an image from a file and return it as an array """
    return np.asarray(tf.keras.preprocessing.image.load_img(img_file, target_size=target_size))


def normalize_labels(labels: Union[List[float], np.ndarray]) -> np.ndarray:
    """ Normalize a list by dividing each element by the total sum """
    labels_np = np.array(labels)
    return labels_np / labels_np.sum()


def calc_mean_score(score_dist: Union[List[float], np.ndarray]) -> float:
    """ Compute the mean from a histogram with values from 1 to 10 """
    score_dist = normalize_labels(score_dist)
    return (score_dist * np.arange(1, 11)).sum()


def calc_sd_score(score_dist: Union[List[float], np.ndarray]) -> float:
    """ Compute the standard deviation from a histogram with values from 1 to 10 """
    mean = calc_mean_score(score_dist)
    score_dist = normalize_labels(score_dist)
    return np.sqrt((np.square(np.arange(1, 11) - mean) * score_dist).sum())


def ensure_dir_exists(dirname: str) -> None:
    """ Creates a directory if it doesn't exist """
    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)


def image_file_to_json(img_path: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Convert a path to an image into a tuple (dir, [file])

    :param img_path: path to file
    :return: tuple (dir, list(dict)) where the list has only one element, being the name of the file without
    extension
    """
    p = pathlib.Path(img_path)
    img_dir = str(p.parent)
    img_id = str(p.stem)

    return img_dir, [{'image_id': img_id}]


def image_dir_to_json(img_dir, img_type='jpg') -> List[Dict[str, str]]:
    """
    Given a path to a directory, return a list of files of the specified extension

    :param img_dir: path to directory containing images
    :param img_type: extension of images to collect
    :return: tuple (dir, list(dict)), where the list contain all the images of the specified img_type
    """
    img_paths = pathlib.Path(img_dir).glob('*.{}'.format(img_type))

    return [{'image_id': str(p.stem)} for p in img_paths]
