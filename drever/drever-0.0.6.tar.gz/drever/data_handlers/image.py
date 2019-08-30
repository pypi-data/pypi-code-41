'''
2D Image Data
'''
import os
import errno
import math
import numpy as np


MIN_IMAGE_WIDTH = 1
MIN_IMAGE_HEIGHT = 1
# Set maxmimum image size to 4K resolution
MAX_IMAGE_WIDTH = 3840
MAX_IMAGE_HEIGHT = 2160
MAX_BITDEPTH = 16
DEFAULT_BITDEPTH = 8


class ImageData():
    '''
    classdocs
    '''

    # Define valid ranges for the several ImageData parameters
    PARAMS_RANGE = {
        "width":    range(MIN_IMAGE_WIDTH, MAX_IMAGE_WIDTH+1),
        "height":   range(MIN_IMAGE_HEIGHT, MAX_IMAGE_HEIGHT+1),
        "bitdepth": range(1, 17),
        "channels": range(1, 4)  # e.g. 1 for gray image,
                                 # 2 for 422 YUV, 3 for RGB image
    }

    COMMON_BITDEPTHS = [1, 8, 10, 12]

    def __init__(self, params=None):
        '''
        Constructor
        '''
        self.params = {
            "width":    0,
            "height":   0,
            "bitdepth": 8,
            "channels": 3
        }
        self.image_data = None
        self.set_params(params)

    def __getitem__(self, key):
        return self.get_image_data()[key]

    def __setitem__(self, key, value):
        self.get_image_data()[key] = value

    def __eq__(self, other):

        objs = (
            {"obj": self, "data": None, "image": False},
            {"obj": other, "data": None, "image": False}
        )

        for obj in objs:

            if isinstance(obj["obj"], ImageData):
                obj["data"] = obj["obj"].get_image_data()
                obj["image"] = True
            elif isinstance(obj["obj"], np.ndarray):
                obj["data"] = obj["obj"]
            else:
                return NotImplemented

        if not np.array_equal(objs[0]["data"], objs[1]["data"]):
            return False

        if (objs[0]["image"] and objs[1]["image"]) is True:
            if self.params != other.params:
                return False

        return True

    def check_params(self, params, use_assertions=False):

        keys_are_equal = set(params.keys()) == set(self.PARAMS_RANGE.keys())

        if use_assertions:
            assert keys_are_equal, \
                "Parameter keys are invalid!"

        if not keys_are_equal:
            return False

        if use_assertions:
            for key, value in params.items():
                assert value in self.PARAMS_RANGE[key], \
                    'Parameter "' + key + '" is out of range!'

        for key, value in params.items():
            if value not in self.PARAMS_RANGE[key]:
                return False

        return True

    def set_params(self, params):

        if params is None:
            self.params = None
        elif self.check_params(params, True):
            self.params = params

    @classmethod
    def extract_params(cls, data, use_bitdepth=None):

        assert data.dtype == np.uint16, \
            "Data is not np.uint16"

        assert len(data.shape) in range(2, 4), \
            "Data has unsupported array dimensions!"

        max_value = np.amax(data)
        if max_value == 0:
            max_value = 2**DEFAULT_BITDEPTH-1

        if use_bitdepth == "Real":
            bitdepth = math.ceil(math.log2(max_value))
        elif use_bitdepth in cls.PARAMS_RANGE["bitdepth"]:

            bitdepth = use_bitdepth

            assert max_value < 2**bitdepth, \
                "Given bitdepth missmatches the maximum image_data value"

        else:

            depths = cls.COMMON_BITDEPTHS

            # If no common bitdepth can be found, use the maximum bitdepth
            bitdepth = MAX_BITDEPTH

            for test_bitdepth in depths:
                if max_value < 2**test_bitdepth:
                    bitdepth = test_bitdepth
                    break

        if len(data.shape) == 2:
            num_channels = 1
        else:

            assert data.shape[2] in range(1, 4), \
                "Data has unsupported array dimensions!"

            num_channels = data.shape[2]

        return {
            "width":    data.shape[1],
            "height":   data.shape[0],
            "bitdepth": bitdepth,
            "channels": num_channels
        }

    def get_np_shape(self):
        return (
            self.params['height'],
            self.params['width'],
            self.params['channels']
        )

    def check_data(self, data, use_bitdepth=None):

        assert data.dtype == np.uint16, \
            "Data is not np.uint16"

        extracted_params = self.extract_params(data, use_bitdepth)

        if extracted_params != self.params:
            print("*************************************************")
            print("Data Check Error")
            print("*************************************************")
            print("- Extracted Parameters:")
            print(extracted_params)
            print("- Set Parameters:")
            print(self.params)
            print("*************************************************")
            return False

        return True

    def init_with_data(self, data, extract_params=True, use_bitdepth=None):

        if extract_params:
            self.params = self.extract_params(data, use_bitdepth)
        else:
            assert self.check_data(data, use_bitdepth), \
                "Check Data failed!"

        assert self.params is not None, \
            "Image parameters needs to be set first!"

        self.image_data = data.reshape(
            (self.params['height'],
             self.params['width'],
             self.params['channels'])
        )

    def init_with_random(self, seed=None):

        assert self.params is not None, \
            "Image parameters needs to be set first!"

        upper_limit = 2**self.params['bitdepth']

        if seed is not None:
            np.random.seed(seed)

        dim = self.get_np_shape()

        rnd_data = (upper_limit*np.random.rand(*dim)).astype(np.uint16)

        self.init_with_data(rnd_data, False, None)

    def get_image_data(self):
        return self.image_data

    def load(self, path, is_two_channels=False):
        '''
        Loads image data (numpy array) from ppm file.

        Parameters:
        path (str): Path of ppm file
        '''

        if not os.path.isfile(path):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), path)

        ppm_file = open(path, "r")

        states = [
            "HEADER_MAGIC_NUMBER",
            "HEADER_GEOMETRY",
            "HEADER_MAX_VALUE",
            "DATA"
        ]

        image_params = {
            "width":    0,
            "height":   0,
            "bitdepth": 8,
            "channels": 3
        }
        image_data = None
        data_coord = [0, 0, 0]
        num_values = 0
        i = 0

        for raw_line in ppm_file:

            line = raw_line.strip()

            # skip line if empty
            if line == "":
                continue

            if states[0] == "HEADER_MAGIC_NUMBER":

                assert line in ("P2", "P3"), \
                    "Unsupported Magic Number: " + line

                image_params["channels"] = 1 if line == "P2" else 3
                states.remove("HEADER_MAGIC_NUMBER")

            elif states[0] == "HEADER_GEOMETRY":
                image_params["width"], image_params["height"] = \
                    [int(str_data) for str_data in line.split()]
                num_values = \
                    image_params["width"] * \
                    image_params["height"] * \
                    image_params["channels"]
                states.remove("HEADER_GEOMETRY")

            elif states[0] == "HEADER_MAX_VALUE":
                image_params["bitdepth"] = \
                    math.floor(math.log(int(line), 2)) + 1
                image_data = np.zeros(
                    (image_params["height"], image_params["width"], 3),
                    np.uint16)
                states.remove("HEADER_MAX_VALUE")

            else:
                data = [int(str_data) for str_data in line.split()]

                for value in data:

                    i += 1

                    # pylint: disable=E1137
                    image_data[
                        data_coord[0],
                        data_coord[1],
                        data_coord[2]
                    ] = value

                    data_coord[2] += 1
                    if data_coord[2] == image_params["channels"]:
                        data_coord[2] = 0
                        data_coord[1] += 1
                        if data_coord[1] == image_params["width"]:
                            data_coord[1] = 0
                            data_coord[0] += 1

        ppm_file.close()

        assert i == num_values, \
            "Read Error: Number of pixel does not match header"

        if is_two_channels:
            image_params["channels"] = 2

        self.set_params(image_params)
        self.init_with_data(
            image_data[::, ::, 0:image_params["channels"]],
            False,
            image_params["bitdepth"]
        )

    def save(self, path, allow_overwrite=False):
        '''
        Stores image data (numpy array) as ppm file.

        Parameters:
        path (str): Path of ppm file
        allow_overwrite (bool): When true and path already exists, file will
                                be overwritten.
        '''

        if not allow_overwrite and os.path.isfile(path):
            raise FileExistsError(
                errno.EEXIST, os.strerror(errno.EEXIST), path)

        # Set Magic Number in Header
        if self.params['channels'] == 1:
            header = "P2\n"
        else:
            header = "P3\n"

        max_value = 2**self.params['bitdepth'] - 1
        ascii_size = math.floor(math.log(max_value, 10)) + 1

        # Set Width, Height and Maximum Value in Header
        header += str(self.params['width']) + " "
        header += str(self.params['height']) + "\n"
        header += str(max_value) + "\n"

        ppm_file = open(path, "w")
        ppm_file.write(header)

        # Write Image Data
        for row in range(0, self.params['height']):

            line = ""

            for col in range(0, self.params['width']):

                value = ""

                for rgb in range(0, self.params['channels']):
                    data_str = str(self.image_data[row, col, rgb])
                    value += data_str.rjust(ascii_size, " ") + " "

                # For 2 channel images, set third channel 0
                value += "0 " if self.params['channels'] == 2 else ""
                line += value

            ppm_file.write(line + "\n")

        ppm_file.close()


def compare_image(im_a, im_b):

    result = {
        "num_errors": 0,
        "first_error": None
    }

    if im_a.params != im_b.params:
        result['num_errors'] = -1
        return result

    num_errors = 0

    for x_coord in range(0, im_a.params['width']):
        for y_coord in range(0, im_a.params['height']):
            for ch_coord in range(0, im_a.params['channels']):

                a_value = im_a.get_image_data()[y_coord, x_coord, ch_coord]
                b_value = im_b.get_image_data()[y_coord, x_coord, ch_coord]

                if a_value != b_value:
                    num_errors += 1

                    if result['first_error'] is None:
                        result['first_error'] = (x_coord, y_coord, ch_coord)

    result['num_errors'] = num_errors
    return result


def assert_image_equal(im_a, im_b, msg=""):

    result = compare_image(im_a, im_b)

    if result["num_errors"] < 0:
        total_msg = "Image Parameter Missmatch!\n"
        total_msg += msg
        assert result["num_errors"] == 0, total_msg
    elif result["num_errors"] > 0:
        total_msg = "Image Data Missmatch!\n"
        total_msg += msg
        assert result["num_errors"] == 0, total_msg
