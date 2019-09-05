import glob
import os.path as op
# import seaborn as sns
from pyqtgraph.parametertree import Parameter
import imageio
import skimage
import numpy as np
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from loguru import logger
from exsu.report import Report



# datapath = op.expanduser("~/data/lynx_lynx/fotopasti_20170825/videa/s rysem/**/**")


class ActivityDetector:
    def __init__(self, report=None):
        params = [
            {
                "name": "Activity Video Cut Threshold",
                "type": "float",
                "value": 1.0,
                'tip': "Applied on activity frames cropping out frames without activity",
                "suffix": "%",
                "siPrefix": False

            },
            {
                "name": "Activity Crop Threshold",
                "type": "float",
                "value": .3,
                'tip': "Applied on activity frames filtered by time and space"
                # "suffix": "",
                # "siPrefix": True

            },
            {
                "name": "Start Frame Offset",
                "type": "int",
                "value": 1,
                'tip': "ignore first few frames"
                # "suffix": "",
                # "siPrefix": True

            },
            {
                "name": "End Frame Offset",
                "type": "int",
                "value": 0,
                'tip': "ignore last few frames"
                # "suffix": "",
                # "siPrefix": True

            },
            # {
            #     "name": "GLCM Levels",
            #     "type": "int",
            #     "value": 64
            # },

        ]

        self.parameters = Parameter.create(name="Activity Detector", type="group", children=params, expanded=False)
        self.input_path = None
        self.output_path = None
        self.report=report

    def set_input_path(self, input_path):
        """
        :param input_path: can be with '~' for home dir and with /**/* for any subdir
        :return:
        """
        self.input_path = Path(input_path)

    def set_output_path(self, output_path):
        self.output_path = Path(output_path)


    def run(self):
        logger.debug(f"Reading files in dir: {self.input_path}")
        fnvideos = glob.glob(op.join(op.expanduser(self.input_path), "*"))
        logger.debug(f"number files in dir: {len(fnvideos)}")
        for fn in fnvideos:
            plt.figure(figsize=(14, 8))
            try:
                self.run_one(Path(fn))
            # except Exception as e:
            except ValueError as e:
                import traceback
                logger.info(f"Problem with processing file: {fn}")
                logger.warning(traceback.format_exc())
        pass

    def run_one(self, fn:Path):
        """
        """
        report = self.report
        logger.info(f"reading file {fn}")
        vid = imageio.get_reader(fn)
        logger.debug("background model extraction")

        background_model, frame_size = create_background_model(vid)
        if report is not None:
            logger.debug("saving")
            logger.debug(
                f"min: {np.min(background_model)}, mean: {np.mean(background_model)}, max: {np.max(background_model)}")
            report.imsave(f"{fn.stem}_background", background_model / 255.0, level=50, level_skimage=10)
        logger.debug("activity estimation")
        begin_offset = int(self.parameters.param("Start Frame Offset").value())
        end_offset = int(self.parameters.param("End Frame Offset").value())
        # end_offset = 10
        error, time, errmax = activity_estimation(vid, background_model, begin_offset=begin_offset, end_offset=end_offset)
        import scipy
        error_filt = scipy.signal.medfilt(error, 5)
        if report is not None:
            fig = plt.figure()
            self.plt_activity(time, error, error_filt=error_filt)
            report.savefig_and_show(fn.stem + "_activity", fig)
        frame, iframe = get_max_image(vid, error)
        if report is not None:
            report.imsave(f"{fn.stem}_maxframe", frame, level=50, level_skimage=10)
        errim = get_activity_diff_image(frame, background_model)
        if report is not None:
            report.imsave(f"{fn.stem}_errim", errim, level=45, level_skimage=10)
        #     return background_model, error, time, errmax, image, imax
        filtered_activity = activity_filter_time_and_space(vid, iframe, background_model)
        if report is not None:

            report.imsave(f"{fn.stem}_filtered_activity", filtered_activity, level=40, level_skimage=10)
            fig = plt.figure()
            plt.imshow(filtered_activity)
            plt.colorbar()
            report.savefig_and_show(f"{fn.stem}_filtered_activity_fig", fig, level=40)

        thr = float(self.parameters.param("Activity Crop Threshold").value())
        roi = activity_roi(filtered_activity, activity_threshold=thr)
        if roi is not None:
            cropped_frame = crop_frame(frame, *roi)
            if report is not None:
                report.imsave(f"{fn.stem}_max_activity_crop", cropped_frame, level=60, level_skimage=10)

        self._cut_video(vid, fn, error_filt)


    def _cut_video(self, vid, fn:Path, error):

        thr = float(self.parameters.param("Activity Video Cut Threshold").value()) * 0.01
        reader = vid
        # reader = imageio.get_reader('imageio:cockatoo.mp4')
        fps = reader.get_meta_data()['fps']

        opath = self.output_path/(fn.stem + "_cut" + fn.suffix)

        writer = imageio.get_writer(opath, fps=fps)
        logger.info(f"write video: {str(opath)}")
        logger.debug(f"video cut threshold: {thr} ")

        i = int(self.parameters.param("Start Frame Offset").value())
        for im in reader:
            if i < len(error):
                if error[i] > thr:
                    writer.append_data(im)  # [:, :, 1])
                    # pass
            i += 1
        writer.close()

    def plt_activity(self, time, error, error_filt=None):
        thr_percent = float(self.parameters.param("Activity Video Cut Threshold").value())
        plt.semilogy(time, 100 * (error))
        if error_filt is not None:
            plt.semilogy(time, 100 * (error_filt), "r")
        # plt.ylim(base, 1+base)
        plt.ylim(0.1, 100)
        # plt.hlines([thr_percent])
        logger.debug(f"thr percent: {thr_percent}")
        plt.axhline(thr_percent, ls='--')
        plt.xlabel("Time [s]")
        plt.ylabel("Activity [%]")




def create_background_model(vid, begin_offset=1, end_offset=50, step=10):

    vid_len = vid.get_length() - end_offset - begin_offset
    frame_size = vid.get_meta_data()["size"]

    background_model = np.zeros([frame_size[1], frame_size[0], 3])

    # nums = range(int(begin_offset), int(vid.get_length() - end_offset), int(step))
    nums = range(begin_offset, vid.count_frames() - end_offset, step)

    # nums = [1,5, 10]

    processed_images = 0
    for num in nums:
        image = vid.get_data(num).astype(np.float)
        if processed_images == 0:
            background_model = image
        else:
            background_model = (processed_images * background_model) / (processed_images + 1.) + image / (
                        processed_images + 1.)
        processed_images += 1

    return background_model, frame_size


def activity_estimation(vid, background_model, begin_offset=0, end_offset=0, step=1):
    # error = np.zeros([vid.count_frames()])
    # error = [0.0] * vid.count_frames()
    error = []

    fps = vid.get_meta_data()['fps']
    frame_size = vid.get_meta_data()["size"]
    nums = range(begin_offset, vid.count_frames() - end_offset, step)

    # times = []
    errmax = 255 * 3 * np.prod(frame_size)
    #     print(errmax)
    for num in nums:
        #     print(num)
        image = vid.get_data(num).astype(np.float)
        err = np.sum(np.abs(background_model - image))
        # error[num] = err
        error.append(err)

    time = np.asarray(nums) / fps
    error = np.array(error) / errmax
    return error, time, errmax




import skimage.filters
from skimage.morphology import disk


def get_max_image(vid, error, begin_offset=1, end_offset=10):
    import copy
    error2 = copy.copy(error)
    error2[-end_offset:] = 0
    imax = np.argmax(error2)
    image = get_image(vid, imax, begin_offset)
    return image, imax


def get_image(vid, imax, begin_offset=1):
    return vid.get_data(imax + begin_offset)



def get_activity_diff_image(image, background_model, safety_multiplicator=0.99):
    diff = np.abs(image.astype(float) - background_model.astype(float))
    errim = (diff[:, :, 0] ** 2 + diff[:, :, 1] ** 2 + diff[:, :, 2] ** 2) ** 0.5
    # normaliza to range <0 ; 1>
    # sqrt(3) because of 3 color channels
    errim = safety_multiplicator * errim / (255. * np.sqrt(3))
    return errim


def activity_time_filter(
        vid, iframe, background_model,
        begin_offset=1, end_offset=50, around_imax=range, time_range=5):
    around_mn = int(max(begin_offset, round(iframe - (time_range / 2))))
    around_mx = int(min(vid.count_frames() - end_offset, round(iframe + (time_range / 2))))

    around_range = range(around_mn, around_mx, 10)

    frames = np.zeros([background_model.shape[0], background_model.shape[1], len(around_range)])

    for i, iiframe in enumerate(around_range):
        #     print(i, iframe)
        frames[:, :, i] = get_activity_diff_image(get_image(vid, iiframe, begin_offset=begin_offset), background_model)
    #     plt.figure()
    #     plt.imshow(frames[:,:,i])

    time_mean_frame = np.mean(frames, axis=2)
    return time_mean_frame


def activity_space_filter(time_mean_frame, median_disk_radius=15, gaussian_sigma=5.0):
    mn = np.min(time_mean_frame)
    print("limits ", mn, np.max(time_mean_frame))
    if mn < -1:
        time_mean_frame = time_mean_frame - mn
    #     if np.min(time_mean_frame) < 0:

    # mean_frame_filtered = skimage.filters.gaussian(mean_frame, sigma=5.0)
    mean_frame_filtered = skimage.filters.median(time_mean_frame, disk(median_disk_radius))
    mean_frame_filtered = skimage.filters.gaussian(mean_frame_filtered, sigma=gaussian_sigma)
    return mean_frame_filtered


import matplotlib.patches as patches

def activity_filter_time_and_space(vid, iframe, background_model):
    """
    Focus on few frames around maximum intensity frame
    :param vid:
    :param iframe:
    :param background_model:
    :return:
    """
    im = activity_time_filter(vid, iframe, background_model)
    im = activity_space_filter(im)
    return im


def roi_size(roi_min, roi_max):
    roi_y_size = roi_max[0] - roi_min[0]
    roi_x_size = roi_max[1] - roi_min[1]
    roi_size = [roi_y_size, roi_x_size]
    return roi_size


def activity_roi(mean_frame_filtered, cut_border=40, activity_threshold=0.1):
    binary_activity_frame = mean_frame_filtered > activity_threshold
    x, y = np.nonzero(binary_activity_frame)
    if len(x) == 0:
        return None
    roi_min = [
        max(np.min(y) - cut_border, 0),
        max(np.min(x) - cut_border, 0)
    ]
    roi_max = [
        min(np.max(y) + cut_border, mean_frame_filtered.shape[1]),
        min(np.max(x) + cut_border, mean_frame_filtered.shape[0]),

    ]
    return roi_min, roi_max

def show_roi(roi_min, roi_max=None, roi_size=None, image=None):
    if roi_size is None:
        roi_y_size = roi_max[0] - roi_min[0]
        roi_x_size = roi_max[1] - roi_min[1]
        roi_size = [roi_y_size, roi_x_size]
    ax = plt.gca()
    if image is not None:
        plt.imshow(image)
    # plt.imshow(binary_activity_frame)

    ax.add_patch(
        patches.Rectangle(
            roi_min,
    #         (10, 10),
            roi_size[0],
            roi_size[1],
            fill=False,      # remove background
            edgecolor="red",
            linewidth=3
        )
    )

def crop_frame(frame, roi_min, roi_max):
    return frame[
        roi_min[1]:roi_max[1],
        roi_min[0]:roi_max[0],
        :
    ]


