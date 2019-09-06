"""
Prediction script crYOLO
"""

# ! /usr/bin/env python
#
# COPYRIGHT
#
# All contributions by Ngoc Anh Huyn:
# Copyright (c) 2017, Ngoc Anh Huyn.
# All rights reserved.
#
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#
from __future__ import print_function
import multiprocessing
import time
import argparse
import os
import sys
import json
import traceback
import numpy as np
from lineenhancer import line_enhancer, maskstackcreator
from . import CoordsIO
from . import imagereader
from . import utils
from . import filament_tracer
from . import config_tools
from . import lowpass
from gooey import Gooey, GooeyParser

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
try:
    os.environ["CUDA_VISIBLE_DEVICES"]
except KeyError:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"


filament_tracers = None
ARGPARSER = None


def create_parser(parser, use_gooed=True):

    required_group = parser.add_argument_group(
        "Required arguments", "These options are mandatory to run crYOLO prediction"
    )
    args = ["-c", "--conf"]
    kwargs = {
        "help": "Path to configuration file.",
        "required": True,
        "gooey_options": {
            "validator": {
                "test": 'user_input.endswith("json")',
                "message": "File has to end with .json!",
            },
            "wildcard": "*.json"
        },
    }

    if use_gooed:
        kwargs["widget"] = "FileChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-w", "--weights"]
    kwargs = {
        "help": "Path to the trained model (.h5 file).",
        "required": True,
        "gooey_options": {
            "validator": {
                "test": 'user_input.endswith("h5")',
                "message": "File has to end with .h5!",
            },
            "wildcard": "*.h5"
        },
    }

    if use_gooed:
        kwargs["widget"] = "FileChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-i", "--input"]
    kwargs = {
        "nargs": "+",
        "help": "Path to one or multiple image folders / images.",
        "required": True,
    }
    if use_gooed:
        kwargs["widget"] = "DirChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-o", "--output"]
    kwargs = {"help": "Specify the output folder.", "required": True}
    if use_gooed:
        kwargs["widget"] = "DirChooser"

    required_group.add_argument(*args, **kwargs)

    optional_group = parser.add_argument_group(
        "Optional arguments", "Optional arguments for crYOLO"
    )

    optional_group.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.3,
        help="Confidence threshold. Have to be between 0 and 1. The higher, the more conservative.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "-g",
        "--gpu",
        default="",
        # type=int,
        nargs="+",
        help="Specifiy which gpu(s) should be used. Multiple GPUs are separated by a whitespace.",
    )

    optional_group.add_argument(
        "-d",
        "--distance",
        default=0,
        type=int,
        help="Particles with a distance less than this value (in pixel) will be removed",
    )

    optional_group.add_argument(
        "-pbs",
        "--prediction_batch_size",
        default=3,
        type=int,
        help="How many images should be predicted in one batch. Smaller values might resolve memory issues.",
    )

    optional_group.add_argument(
        "--gpu_fraction",
        type=float,
        default=1.0,
        help="Specify the fraction of memory per GPU used by crYOLO during prediction. Only values between 0.0 and 1.0 are allowed.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "-nc",
        "--num_cpu",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of CPUs used during filtering / filament tracing. By default it will use all of the available CPUs.",
    )

    optional_group.add_argument(
        "--norm_margin",
        type=float,
        default=0.0,
        help="Relative margin size for normalization.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "--otf",
        action="store_true",
        default=False,
        help="On the fly filtering. Filtered micrographs will not be written to disk. Might be slower",
    )



    filament_group = parser.add_argument_group(
        "Filament options",
        "These options are only relevant if you want to use  the filament mode",
    )

    filament_group.add_argument(
        "--filament", action="store_true", help="Activate filament mode"
    )

    filament_group.add_argument(
        "--nosplit",
        action="store_true",
        help="The filament mode does not split to curved filaments",
    )

    filament_group.add_argument(
        "--nomerging",
        action="store_true",
        help="The filament mode does not merge filaments",
    )

    filament_group.add_argument(
        "-fw",
        "--filament_width",
        default=None,
        type=int,
        help="Filament width (in pixel)",
    )

    filament_group.add_argument(
        "-mw", "--mask_width", default=100, type=int, help="Mask width (in pixel)"
    )

    filament_group.add_argument(
        "-bd",
        "--box_distance",
        default=None,
        type=int,
        help="Distance between two boxes(in pixel)",
    )

    filament_group.add_argument(
        "-mn",
        "--minimum_number_boxes",
        default=None,
        type=int,
        help="Minimum number of boxes per filament.",
    )

    filament_group.add_argument(
        "-sr",
        "--search_range_factor",
        type=float,
        default=1.41,
        help="The search range for connecting boxes is the box size times this factor.",
    )

    depexp_group = parser.add_argument_group(
        "Deprecated/Experimental/Special ",
        "Contains either deprecated / experimental or very special options.",
    )
    depexp_group.add_argument(
        "-p",
        "--patch",
        type=int,
        help="(DEPRECATED) Number of patches. Use the config file in case you want to use patches.",
    )

    depexp_group.add_argument(
        "--write_empty",
        action="store_true",
        help="Write empty box files when not particle could be found.",
    )


def get_parser():
    parser = GooeyParser(
        description="Pick particles with crYOLO on any dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    create_parser(parser)
    return parser


def _main_():
    import sys

    # if sys.argv[1] == "gui":
    if len(sys.argv) >= 2:
        if not "--ignore-gooey" in sys.argv:
            sys.argv.append("--ignore-gooey")

    # r'^\d+ particles are found in .* \( (\d+) % \)$'
    kwargs = {"terminal_font_family": "monospace",
              "richtext_controls": True}
    Gooey(
        main,
        program_name="crYOLO Predict",
        image_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../icons"),
        progress_regex=r"^.* \( Progress:\s+(-?\d+) % \)$",
        disable_progress_bar_animation=True,
        tabbed_groups=True,
        **kwargs
    )()


def main(args=None):
    if args is None:
        parser = get_parser()
        args = parser.parse_args()

    if isinstance(args.gpu, list):
        if len(args.gpu) == 1:
            num_gpus = 1
            if args.gpu[0] != "-1":
                str_gpus = args.gpu[0].strip().split(" ")
                num_gpus = len(str_gpus)
                os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)
        else:
            str_gpus = [str(entry) for entry in args.gpu]
            num_gpus = len(str_gpus)
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)
    else:
        num_gpus = 1
        if args.gpu != -1 and len(args.gpu) > 0:
            str_gpus = str(args.gpu)
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)

    if args.gpu_fraction < 1.0 and args.gpu_fraction > 0.0:
        import tensorflow as tf
        from keras.backend.tensorflow_backend import set_session

        config = tf.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = args.gpu_fraction
        set_session(tf.Session(config=config))

    config_path = args.conf
    weights_path = args.weights
    input_path = args.input
    obj_threshold = args.threshold
    min_distance = args.distance
    mask_width = args.mask_width
    prediction_batch_size = args.prediction_batch_size
    no_merging = args.nomerging
    otf = args.otf
    do_merging = True
    norm_margin = args.norm_margin
    search_range_factor = args.search_range_factor
    if no_merging:
        do_merging = False

    nosplit = False
    if args.nosplit is not None:
        nosplit = args.nosplit

    outdir = None
    if args.output is not None:
        outdir = str(args.output)
    write_empty = args.write_empty

    num_cpus = multiprocessing.cpu_count()
    if args.num_cpu != -1:
        num_cpus = args.num_cpu

    with open(config_path) as config_buffer:
        try:
            config = json.load(config_buffer)
        except json.JSONDecodeError:
            print(
                "Your configuration file seems to be corruped. Please check if it is valid."
            )
        if config["model"]["input_size"] % 32 > 0:
            new_input_size = int(32 * round(float(config["model"]["input_size"]) / 32))
            print(
                "You input size is not a multiple of 32. Round it to the next multiple of 32:",
                new_input_size,
            )
            config["model"]["input_size"] = new_input_size

    filament_mode = args.filament
    if filament_mode:
        if args.filament_width is None:
            sys.exit("Please specifiy your filament width ( -fw / --filament_width)")
        else:
            filament_width = args.filament_width
        if args.box_distance is None:
            sys.exit("Please specifiy your box distance ( -bd / --box_distance)")
        else:
            box_distance = args.box_distance
        minimum_number_boxes = 1
        if args.minimum_number_boxes is not None:
            minimum_number_boxes = args.minimum_number_boxes

    if args.patch is not None and args.patch > 0:
        num_patches = int(args.patch)
    else:
        num_patches = config_tools.get_number_patches(config)

    # Get overlap patches
    overlap_patches = 0
    if "overlap_patches" in config["model"]:
        overlap_patches = int(config["model"]["overlap_patches"])
    elif not len(config["model"]["anchors"]) > 2:
        overlap_patches = config["model"]["anchors"][0]

    picking_results = do_prediction(
        config_path=config_path,
        weights_path=weights_path,
        input_path=input_path,
        obj_threshold=obj_threshold,
        num_patches=num_patches,
        filament_mode=filament_mode,
        write_empty=write_empty,
        overlap=overlap_patches,
        num_images_batch_prediction=prediction_batch_size,
        num_gpus=num_gpus,
        num_cpus=num_cpus,
        otf=otf,
        normalization_margin=norm_margin,
    )

    # Resacle to image dimensions, resize boxes

    if "particle_diameter" in config["model"]:
        if isinstance(config["model"]["particle_diameter"], list):
            export_size = config["model"]["particle_diameter"][0]
        else:
            export_size = config["model"]["particle_diameter"]
    elif len(config["model"]["anchors"]) == 2:
        export_size = config["model"]["anchors"][0]
    else:
        export_size = None

    # Rescaling

    for picking_result_micrograph in picking_results:

        # if num_patches > 1:
        #    image_width = int(picking_result_micrograph["img_width"]/num_patches)+2*overlap_patches
        #    image_height = int(picking_result_micrograph["img_height"]/num_patches)+2*overlap_patches
        # else:
        image_width = picking_result_micrograph["img_width"]
        image_height = picking_result_micrograph["img_height"]
        picking_result_micrograph["boxes"] = [
            rescale(box, image_height, image_width, export_size)
            for box in picking_result_micrograph["boxes"]
        ]

        picking_result_micrograph["boxes_unfiltered"] = [
            rescale(box, image_height, image_width, export_size)
            for box in picking_result_micrograph["boxes_unfiltered"]
        ]

    # Min distance filter
    if min_distance > 0:
        sum_particles_before_filtering = np.sum(
            [len(res["boxes"]) for res in picking_results]
        )
        for picking_result_micrograph in picking_results:
            picking_result_micrograph["boxes"] = min_distance_filter(
                picking_result_micrograph["boxes"], min_distance
            )

        num_remain_particles = np.sum([len(res["boxes"]) for res in picking_results])
        print(
            sum_particles_before_filtering - num_remain_particles,
            "particles were filtered because of the distance threshold",
            min_distance,
        )

        print("Total picked particles after distance filtering:", num_remain_particles)

    # Filtering of particles which are not fully immersed in the micrograph
    deleted = 0
    for picking_result_micrograph in picking_results:
        image_width = picking_result_micrograph["img_width"]
        image_height = picking_result_micrograph["img_height"]

        boxes = picking_result_micrograph["boxes"]
        boxes_to_delete = get_not_fully_immersed_box_indices(
            boxes, image_height, image_width
        )
        for index in sorted(boxes_to_delete, reverse=True):
            del boxes[index]
        deleted += len(boxes_to_delete)

        boxes = picking_result_micrograph["boxes_unfiltered"]
        boxes_to_delete = get_not_fully_immersed_box_indices(
            boxes, image_height, image_width
        )
        for index in sorted(boxes_to_delete, reverse=True):
            del boxes[index]
    print(
        "Deleted",
        deleted,
        "particles as they were not fully immersed in the micrograph",
    )

    ###############################
    #   Filament Post Processing
    ###############################

    # 1. Build sets of images (size = number of processors)
    # 2. Enhance
    # 3. Filamental post processing

    if filament_mode:
        picking_result_with_boxes = []
        picking_result_no_boxes = []
        picking_result_with_boxes_subsets = []
        picked_filaments = 0
        for picking_result_micrograph in picking_results:
            if picking_result_micrograph["boxes"]:
                picking_result_with_boxes.append(picking_result_micrograph)
            else:
                picking_result_micrograph["filaments"] = []
                picking_result_no_boxes.append(picking_result_micrograph)

        if picking_result_with_boxes:
            image_width, image_height = imagereader.read_width_height(
                picking_result_with_boxes[0]["img_path"]
            )
            rescale_factor = 1024.0 / max(image_width, image_height)
            rescale_factor_x = 1024.0 / image_width
            rescale_factor_y = 1024.0 / image_height

            mask_creator = maskstackcreator.MaskStackCreator(
                filament_width=filament_width * rescale_factor,
                mask_size=1024,
                mask_width=mask_width,
                angle_step=2,
                bright_background=True,
            )
            print("Start filament tracing")
            print("Initialisation mask stack")
            mask_creator.init()
            # Devide picking result into chunks

            number_processors = num_cpus

            picking_result_with_boxes_subsets = [
                picking_result_with_boxes[i : i + number_processors]
                for i in range(0, len(picking_result_with_boxes), number_processors)
            ]
            process_counter = 1

            # Parallel tracing

            filament_width_scaled = filament_width * rescale_factor
            search_radius_scaled = export_size * rescale_factor * search_range_factor
            for picking_result_subset in picking_result_with_boxes_subsets:
                image_subset = [
                    picking_result_subset[i]["img_path"]
                    for i in range(0, len(picking_result_subset))
                ]
                boxes_subset = [
                    picking_result_subset[i]["boxes"]
                    for i in range(0, len(picking_result_subset))
                ]
                print(
                    " Enhance subset ",
                    process_counter,
                    "of",
                    len(picking_result_with_boxes_subsets),
                )
                enhanced_images = line_enhancer.enhance_images(
                    image_subset, mask_creator
                )
                angle_images = [
                    enhanced_images[i]["max_angle"] for i in range(len(enhanced_images))
                ]

                print(
                    " Trace subset ",
                    process_counter,
                    "of",
                    len(picking_result_with_boxes_subsets),
                )
                global filament_tracers
                filament_tracers = []
                for index, boxset in enumerate(boxes_subset):
                    angle_image_flipped = np.flipud(angle_images[index])
                    tracer = filament_tracer.FilamentTracer(
                        boxes=boxset,
                        orientation_image=angle_image_flipped,
                        filament_width=filament_width_scaled,
                        search_radius=search_radius_scaled,
                        angle_delta=10,
                        rescale_factor=rescale_factor,
                        rescale_factor_x=rescale_factor_x,
                        rescale_factor_y=rescale_factor_y,
                        do_merging=do_merging,
                        box_distance=box_distance,
                    )
                    filament_tracers.append(tracer)

                pool = multiprocessing.Pool(processes=num_cpus)

                subset_new_filaments = pool.map(
                    trace_subset_filements, range(len(filament_tracers)), chunksize=1
                )
                pool.close()
                pool.join()

                for index_subset in range(len(picking_result_subset)):
                    new_filaments = subset_new_filaments[index_subset]

                    resamples_filaments = utils.resample_filaments(
                        new_filaments, box_distance
                    )

                    # Make straight filaments
                    if not nosplit:
                        resamples_filaments = filament_tracer.split_filaments_by_straightness(
                            resamples_filaments
                        )

                    # NMS for filaments:
                    resamples_filaments = filament_tracer.nms_for_filaments(
                        resamples_filaments, filament_width
                    )

                    # Min number of boxes filter:
                    resamples_filaments = filament_tracer.filter_filaments_by_num_boxes(
                        resamples_filaments, minimum_number_boxes
                    )

                    picked_filaments += len(resamples_filaments)

                    if len(resamples_filaments) >= 1:
                        picking_result_subset[index_subset][
                            "filaments"
                        ] = resamples_filaments
                    else:
                        picking_result_subset[index_subset]["filaments"] = None

                print("Total number of filaments picked so far: ", picked_filaments)
                process_counter += 1

        if write_empty:
            picking_result_with_boxes_subsets.append(picking_result_no_boxes)

        print("Total number of filaments picked: ", picked_filaments)

        ###############################
        #   Write bounding boxes
        ###############################
        for picking_result_subset in picking_result_with_boxes_subsets:

            for result in picking_result_subset:

                if (result["filaments"] is not None) or write_empty:
                    pth = result["pth"]
                    eman_helix_segmented_path = pth
                    eman_start_end = pth
                    star_start_end = pth[:-3] + "star"

                    if outdir is not None:
                        filename = os.path.basename(pth)
                        eman_helix_segmented_path = os.path.join(
                            outdir, "EMAN_HELIX_SEGMENTED", filename
                        )
                        eman_start_end = os.path.join(
                            outdir, "EMAN_START_END", filename
                        )
                        filename = filename[:-3] + "star"
                        star_start_end = os.path.join(
                            outdir, "STAR_START_END", filename
                        )

                    if not os.path.exists(os.path.dirname(eman_helix_segmented_path)):
                        os.makedirs(os.path.dirname(eman_helix_segmented_path))

                    if not os.path.exists(os.path.dirname(eman_start_end)):
                        os.makedirs(os.path.dirname(eman_start_end))

                    if not os.path.exists(os.path.dirname(star_start_end)):
                        os.makedirs(os.path.dirname(star_start_end))
                    CoordsIO.write_eman1_helicon(
                        filaments=result["filaments"],
                        path=eman_helix_segmented_path,
                        image_filename=os.path.basename(result["img_path"]),
                    )

                    CoordsIO.write_eman1_filament_start_end(
                        filaments=result["filaments"], path=eman_start_end
                    )

                    CoordsIO.write_star_filemant_file(
                        filaments=result["filaments"], path=star_start_end
                    )

    else:
        ###############################
        #   Write bounding boxes
        ###############################

        for box_to_write in picking_results:

            original_path = box_to_write["pth"]
            eman1_path = original_path

            star_path = os.path.splitext(original_path)[0] + ".star"
            cbox_path = os.path.splitext(original_path)[0] + ".cbox"

            if outdir is not None:
                filename = os.path.basename(eman1_path)
                eman1_path = os.path.join(outdir, "EMAN", filename)

            # Create directory if it does not existes
            if not os.path.exists(os.path.dirname(eman1_path)):
                os.makedirs(os.path.dirname(eman1_path))

            CoordsIO.write_eman1_boxfile(path=eman1_path, boxes=box_to_write["boxes"])

            if outdir is not None:
                filename = os.path.basename(star_path)
                star_path = os.path.join(outdir, "STAR", filename)

            # Create directory if it does not existes
            if not os.path.exists(os.path.dirname(star_path)):
                os.makedirs(os.path.dirname(star_path))
            CoordsIO.write_star_file(path=star_path, boxes=box_to_write["boxes"])

            if outdir is not None:
                filename = os.path.basename(cbox_path)
                star_path = os.path.join(outdir, "CBOX", filename)

            # Create directory if it does not existes
            if not os.path.exists(os.path.dirname(star_path)):
                os.makedirs(os.path.dirname(star_path))
            CoordsIO.write_cbox_file(
                path=star_path, boxes=box_to_write["boxes_unfiltered"]
            )


def min_distance_filter(boxes, min_distance):
    boxes_to_delete = []
    min_distance_sq = min_distance * min_distance
    for box_a_index, box_a in enumerate(boxes):
        for box_b_index in range(box_a_index, len(boxes)):
            if box_a_index != box_b_index:
                distsq = utils.box_squared_distance(box_a, boxes[box_b_index])

                if distsq < min_distance_sq:
                    box_index_to_delte = box_a_index
                    if box_a.c > boxes[box_b_index].c:
                        box_index_to_delte = box_b_index
                    if box_index_to_delte not in boxes_to_delete:
                        boxes_to_delete.append(box_index_to_delte)
    for index in sorted(boxes_to_delete, reverse=True):
        del boxes[index]

    return boxes


def rescale(box, image_height, image_width, export_size=None):
    x_ll = int((box.x - box.w / 2) * image_height)  # lower left
    y_ll = int(
        image_width - box.y * image_width - box.h / 2 * image_width
    )  # lower right
    boxheight_in_pxl = int(box.h * image_width)
    boxwidth_in_pxl = int(box.w * image_height)
    if export_size is not None:
        delta_boxheight = export_size - boxheight_in_pxl
        delta_boxwidth = export_size - boxwidth_in_pxl
        x_ll = x_ll - delta_boxheight / 2
        y_ll = y_ll - delta_boxwidth / 2
        boxheight_in_pxl = export_size
    box.x = x_ll
    box.y = y_ll
    box.w = boxheight_in_pxl
    box.h = boxheight_in_pxl

    return box


def do_prediction(
    config_path,
    weights_path,
    input_path,
    num_patches,
    obj_threshold=0.3,
    write_empty=False,
    config_pre=None,
    overlap=0,
    filament_mode=False,
    num_images_batch_prediction=3,
    num_gpus=1,
    num_cpus=-1,
    yolo=None,
    otf=False,
    normalization_margin=0,
):
    """

    :param config_path: Path to the config file
    :param weights_path: Path do weights file (h5)
    :param input_path: Path to the folder containing the input images
    :param num_patches: Number of patches to use
    :param obj_threshold: Threshold for objects
    :param write_empty:
    :param config_pre:
    :param overlap:
    :param filament_mode:
    :param num_images_batch_prediction:
    :param num_gpus:
    :param yolo:
    :return:
    """
    for path in input_path:
        path_exists = os.path.exists(path)
        if not path_exists:
            sys.exit("Input path does not exist: " + path)

    img_paths = []
    if isinstance(input_path, list):

        for path in input_path:
            isdir = os.path.isdir(path)
            if isdir:
                dir_files = os.listdir(path)

                dir_files = [
                    i
                    for i in dir_files
                    if not i.startswith(".")
                    and os.path.isfile(os.path.join(path, i))
                    and i.endswith(("tiff", "tif", "mrc", "mrcs", "png", "jpg", "jpeg"))
                ]

                img_paths.extend(
                    [os.path.join(path, image_file) for image_file in dir_files]
                )
            elif os.path.isfile(path):
                if not path.startswith(".") and path.endswith(
                    ("tiff", "tif", "mrc", "png", "mrcs", "jpg", "jpeg")
                ):
                    img_paths.append(path)
    else:
        isdir = os.path.isdir(input_path)
        if isdir:
            img_paths = os.listdir(input_path)

            img_paths = [
                i
                for i in img_paths
                if not i.startswith(".")
                and os.path.isfile(os.path.join(input_path, i))
                and i.endswith(("tiff", "tif", "mrc", "mrcs", "png", "jpg", "jpeg"))
            ]

    if not img_paths:
        sys.exit("No valid image in your specified input")
    img_paths.sort()
    first_image_path = img_paths[0]
    if config_pre is not None:
        config = config_pre
    else:
        with open(config_path) as config_buffer:
            config = json.load(config_buffer)

    # Read (first) image and check the image depth.

    try:
        img_first = imagereader.image_read(first_image_path)
    except ValueError:
        sys.exit("Image " + first_image_path + " is not valid")
    if img_first is None:
        sys.exit("No valid image: " + first_image_path)

    if len(img_first.shape) == 2:
        depth = 1
    elif img_first.shape[2] == 1:
        depth = 1
    elif np.all(img_first[:, :, 0] == img_first[:, :, 1]) and np.all(
        img_first[:, :, 0] == img_first[:, :, 2]
    ):
        depth = 1
    else:
        depth = 3

    grid_w, grid_h = config_tools.get_gridcell_dimensions(config)

    #############################################
    # Read meta data about the model
    #############################################
    anchors = None
    yolo_kwargs = {}
    import h5py

    with h5py.File(weights_path, mode="r") as f:
        try:
            anchors = list(f["anchors"])
        except KeyError:
            None

    with h5py.File(weights_path, mode="r") as f:
        try:
            num_free_layers = int(list(f["num_free_layers"])[0])
            yolo_kwargs["num_fine_tune_layers"] = num_free_layers
        except KeyError:
            pass

    if anchors is None:

        if len(config["model"]["anchors"]) > 2:
            # general model is used
            img_width = 4096.0 / num_patches
            img_height = 4096.0 / num_patches
            cell_w = img_width / grid_w
            cell_h = img_height / grid_h
            anchors = np.array(config["model"]["anchors"], dtype=float)
            anchors[::2] = anchors[::2] / cell_w
            anchors[1::2] = anchors[1::2] / cell_h

        else:
            # specifc model is used

            img_width = float(img_first.shape[1]) / num_patches
            img_height = float(img_first.shape[0]) / num_patches
            cell_w = img_width / grid_w
            cell_h = img_height / grid_h

            box_width, box_height = config_tools.get_box_size(config)

            anchor_width = 1.0 * box_width / cell_w
            anchor_height = 1.0 * box_height / cell_h

            anchors = [anchor_width, anchor_height]
        print("Calculated Anchors using first image", anchors)
    else:
        print("Read Anchor from model", anchors)

    if yolo is None:
        ###############################
        #   Make the model
        ###############################
        backend_weights = None
        if "backend_weights" in config["model"]:
            backend_weights = config["model"]["backend_weights"]
        from .frontend import YOLO

        yolo = YOLO(
            architecture=config["model"]["architecture"],
            input_size=config["model"]["input_size"],
            input_depth=depth,
            labels=["particle"],
            max_box_per_image=config["model"]["max_box_per_image"],
            anchors=anchors,
            backend_weights=backend_weights,
            pretrained_weights=weights_path,
            **yolo_kwargs
        )

        ###############################
        #   Load trained weights
        ###############################

        # USE MULTIGPU
        if num_gpus > 1:
            from keras.utils import multi_gpu_model

            parallel_model = multi_gpu_model(yolo.model, gpus=num_gpus)
            yolo.model = parallel_model
    else:
        yolo.anchors = anchors

    ##############################
    # Filter the data
    ##############################

    if otf and not "filter" in config["model"]:
        print(
            "You specified the --otf option. However, filtering is not configured in your"
            "config line, therefore crYOLO will ignore --otf."
        )
    do_nn_filter = False
    if "filter" in config["model"]:

        filter_options = config["model"]["filter"]
        if len(filter_options) > 2:
            do_nn_filter = True
            model_path, overlap, nn_batch_size, filter_img_path = filter_options
            if not otf:
                print("Filter data using noise2noise model: ", model_path)
                img_paths = utils.filter_images_nn_dir(
                    img_paths=img_paths,
                    output_dir_filtered_imgs=filter_img_path,
                    model_path=model_path,
                    padding=overlap,
                    batch_size=nn_batch_size,
                )
        else:
            # Normal lowpass filter
            cutoff, filter_img_path = filter_options
            if not otf:
                img_paths = filter_images_lowpass(
                    img_paths, filter_img_path, cutoff, num_cpus=num_cpus
                )

    ###############################
    #   Predict bounding boxes
    ###############################
    print("Reset progress bar: ( Progress: -1 % )")
    total_picked = 0
    boxes_to_write = []
    measured_times = []
    picked_img = 1
    batchsize = num_patches * num_patches * num_images_batch_prediction
    tiles = []
    img_tiles = None
    num_written_tiles = 0
    image_indices = []
    skipped_images = []
    for current_index_image, img_pth in enumerate(img_paths):

        if os.path.basename(img_pth)[0] != ".":

            start = time.time()

            # Read image file!
            try:

                if otf and "filter" in config["model"]:
                    if do_nn_filter:
                        print("Filter", img_pth)
                        image = utils.filter_images_nn_img(
                            img_pth,
                            model_path,
                            padding=overlap,
                            batch_size=nn_batch_size,
                        )
                    else:
                        image = filter_images_lowpass(
                            [img_pth], None, cutoff, num_cpus=num_cpus, otf=True
                        )[0]
                else:
                    image = imagereader.image_read(img_pth)
            except ValueError:
                print("Image not valid: ", img_pth, "SKIPPED")
                skipped_images.append(img_pth)
                continue

            if image is not None or image.shape[0] == 0 or image.shape[1] == 0:
                image_indices.append(current_index_image)

                for patch_x in np.arange(0, num_patches):
                    for patch_y in np.arange(0, num_patches):
                        tile_coordinates = imagereader.get_tile_coordinates(
                            image.shape[1],
                            image.shape[0],
                            num_patches,
                            (patch_x, patch_y),
                            overlap=overlap,
                        )
                        tiles.append(tile_coordinates)
                        img_tmp = image[tile_coordinates[1], tile_coordinates[0]]

                        if img_tiles is None:
                            number_tiles_left = (
                                (len(img_paths) - current_index_image)
                                * num_patches
                                * num_patches
                            )
                            num_tiles = min(batchsize, number_tiles_left)
                            img_tiles = np.empty(
                                shape=(num_tiles, img_tmp.shape[0], img_tmp.shape[1]),
                                dtype=np.float32,
                            )

                        img_tiles[num_written_tiles, :, :] = img_tmp
                        num_written_tiles = num_written_tiles + 1

                if num_written_tiles == batchsize or current_index_image == (
                    len(img_paths) - 1
                ):
                    if filament_mode:
                        nms_thresh = 0.5
                    else:
                        nms_thresh = 0.3
                    boxes_per_image_nms, boxes_per_image_unfiltered = yolo.predict(
                        img_tiles,
                        tiles,
                        image.shape,
                        obj_threshold=obj_threshold,
                        nms_threshold=nms_thresh,
                        num_patches=num_patches,
                        normalize_margin=normalization_margin,
                    )
                    end = time.time()
                    measured_times.append(end - start)
                    for box_img_index, boxes in enumerate(boxes_per_image_nms):
                        boxes_image_path = img_paths[image_indices[box_img_index]]
                        imgh, imgw = imagereader.read_width_height(boxes_image_path)
                        total = len(img_paths)
                        print(
                            len(boxes),
                            "particles are found in",
                            boxes_image_path,
                            " ( Progress: ",
                            int(float(picked_img) * 100 / len(img_paths)),
                            "% )",
                        )

                        picked_img += 1
                        total_picked = total_picked + len(boxes)

                        if boxes or write_empty:
                            box_pth = os.path.join(
                                os.path.dirname(boxes_image_path), "box"
                            )
                            file_name_without_extension = os.path.splitext(
                                os.path.basename(boxes_image_path)
                            )[0]
                            box_pth = os.path.join(
                                box_pth,
                                os.path.basename(file_name_without_extension) + ".box",
                            )

                            box_to_write = {
                                "pth": box_pth,
                                "img_width": imgw,
                                "img_height": imgh,
                                "img_path": boxes_image_path,
                                "boxes": boxes,
                                "boxes_unfiltered": boxes_per_image_unfiltered[
                                    box_img_index
                                ],
                            }
                            boxes_to_write.append(box_to_write)
                        else:
                            print("no boxes: ", boxes_image_path)

                    # Reset variables
                    tiles = []
                    img_tiles = None
                    num_written_tiles = 0
                    image_indices = []
        else:
            print("Not a valid image:", img_pth)
    if len(skipped_images) > 0:
        print(
            "The following images were skipped because of errors during reading them:"
        )
        for img in skipped_images:
            print(img)
    print(
        total_picked,
        "particles in total are found",
        "(",
        int(np.sum(measured_times)),
        "seconds)",
    )

    return boxes_to_write


def get_not_fully_immersed_box_indices(boxes, image_height, image_width):
    boxes_to_delete = []
    for box_index, box in enumerate(boxes):
        if (
            (box.x + box.w) >= image_height
            or box.x < 0
            or box.y < 0
            or (box.y + box.h) >= image_width
        ):
            boxes_to_delete.append(box_index)
    return boxes_to_delete


def filter_images_lowpass(
    img_paths, output_dir_filtered_imgs, cutoff, num_cpus=-1, otf=False
):
    """
    Filteres a list of images and return a new list with the paths to the filtered images.

    :param img_paths: Path to images to filter
    :param output_dir_filtered_imgs: Output directory to save the filtered images
    :param cutoff: Absolute cutoff frequency (0-0.5)
    :return: List of paths to the filtered images
    """
    if not otf and not os.path.isdir(output_dir_filtered_imgs):
        os.makedirs(output_dir_filtered_imgs)

    arg_tubles = []
    for img_id, img_pth in enumerate(img_paths):
        if os.path.basename(img_pth)[0] != ".":
            if otf:
                arg_tubles.append((img_pth, cutoff))
            else:
                arg_tubles.append(
                    (
                        img_pth,
                        cutoff,
                        output_dir_filtered_imgs,
                        img_id + 1,
                        len(img_paths),
                    )
                )

    num_processes = None
    if num_cpus != -1:
        num_processes = num_cpus
    lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(
        initializer=lowpass.init,
        initargs=(lock,),
        maxtasksperchild=1,
        processes=num_processes,
    )

    if otf:
        filtered_images = pool.starmap(
            lowpass.filter_single_image, arg_tubles, chunksize=1
        )
    else:
        filtered_images = pool.starmap(
            lowpass.filter_single_image_and_write_to_disk, arg_tubles, chunksize=1
        )
    pool.close()
    pool.join()

    return filtered_images


def trace_subset_filements(tracer_index):
    return filament_tracers[tracer_index].trace_filaments()


if __name__ == "__main__":
    _main_()
