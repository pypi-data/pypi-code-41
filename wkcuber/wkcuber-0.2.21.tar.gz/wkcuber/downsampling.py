import logging
import wkw
import re
import numpy as np
from argparse import ArgumentParser
import os
from scipy.ndimage.interpolation import zoom
from itertools import product
from enum import Enum
from .mag import Mag
from .metadata import read_datasource_properties

from .utils import (
    add_verbose_flag,
    open_wkw,
    WkwDatasetInfo,
    ensure_wkw,
    time_start,
    time_stop,
    add_distribution_flags,
    get_executor_for_args,
    wait_and_ensure_success,
    add_isotropic_flag,
    setup_logging,
)

DEFAULT_EDGE_LEN = 256
CUBE_REGEX = re.compile(r"z(\d+)/y(\d+)/x(\d+)(\.wkw)$")


def parse_cube_file_name(filename):
    m = CUBE_REGEX.search(filename)
    return (int(m.group(3)), int(m.group(2)), int(m.group(1)))


class InterpolationModes(Enum):
    MEDIAN = 0
    MODE = 1
    NEAREST = 2
    BILINEAR = 3
    BICUBIC = 4
    MAX = 5
    MIN = 6


def create_parser():
    parser = ArgumentParser()

    parser.add_argument("path", help="Directory containing the dataset.")

    parser.add_argument(
        "--layer_name",
        "-l",
        help="Name of the cubed layer (color or segmentation)",
        default="color",
    )

    parser.add_argument(
        "--interpolation_mode",
        "-i",
        help="Interpolation mode (median, mode, nearest, bilinear or bicubic)",
        default="default",
    )

    parser.add_argument(
        "--from_mag",
        "--from",
        "-f",
        help="Resolution to base downsampling on",
        type=str,
        default="1",
    )

    # Either provide the maximum resolution to be downsampled OR a specific, anisotropic magnification.
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--max",
        "-m",
        help="Max resolution to be downsampled. In case of anisotropic downsampling, the process is considered "
        "done when max(current_mag) >= max(max_mag) where max takes the largest dimension of the mag tuple "
        "x, y, z. For example, a maximum mag value of 8 (or 8-8-8) will stop the downsampling as soon as a "
        "magnification is produced for which one dimension is equal or larger than 8.",
        type=int,
        default=512,
    )

    group.add_argument(
        "--anisotropic_target_mag",
        help="Specify an explicit anisotropic target magnification which should be "
        "created (e.g., --anisotropic_target_mag 2-2-1). Consider using --anisotropic "
        "instead which automatically creates multiple anisotropic magnifications depending "
        "on the dataset's scale",
        type=str,
    )

    parser.add_argument(
        "--buffer_cube_size",
        "-b",
        help="Size of buffered cube to be downsampled (i.e. buffer cube edge length)",
        type=int,
        default=DEFAULT_EDGE_LEN,
    )

    parser.add_argument(
        "--no_compress",
        help="Don't compress data during downsampling",
        default=False,
        action="store_true",
    )

    add_verbose_flag(parser)
    add_isotropic_flag(parser)
    add_distribution_flags(parser)

    return parser


def cube_addresses(source_wkw_info):
    # Gathers all WKW cubes in the dataset
    with open_wkw(source_wkw_info) as source_wkw:
        wkw_addresses = list(parse_cube_file_name(f) for f in source_wkw.list_files())
        wkw_addresses.sort()
        return wkw_addresses


def downsample(
    source_wkw_info,
    target_wkw_info,
    source_mag: Mag,
    target_mag: Mag,
    interpolation_mode,
    cube_edge_len,
    compress,
    args=None,
):

    assert source_mag < target_mag
    logging.info("Downsampling mag {} from mag {}".format(target_mag, source_mag))

    mag_factors = [
        t // s for (t, s) in zip(target_mag.to_array(), source_mag.to_array())
    ]
    # Detect the cubes that we want to downsample
    source_cube_addresses = cube_addresses(source_wkw_info)

    target_cube_addresses = list(
        set(
            tuple(dim // mag_factor for (dim, mag_factor) in zip(xyz, mag_factors))
            for xyz in source_cube_addresses
        )
    )
    target_cube_addresses.sort()
    logging.debug(
        "Found source cubes: count={} size={} min={} max={}".format(
            len(source_cube_addresses),
            (cube_edge_len,) * 3,
            min(source_cube_addresses),
            max(source_cube_addresses),
        )
    )
    logging.debug(
        "Found target cubes: count={} size={} min={} max={}".format(
            len(target_cube_addresses),
            (cube_edge_len,) * 3,
            min(target_cube_addresses),
            max(target_cube_addresses),
        )
    )

    with open_wkw(source_wkw_info) as source_wkw:
        num_channels = source_wkw.header.num_channels
        header_block_type = (
            wkw.Header.BLOCK_TYPE_LZ4HC if compress else wkw.Header.BLOCK_TYPE_RAW
        )
        ensure_wkw(
            target_wkw_info, block_type=header_block_type, num_channels=num_channels
        )

    with get_executor_for_args(args) as executor:
        job_args = []
        for target_cube_xyz in target_cube_addresses:
            job_args.append(
                (
                    source_wkw_info,
                    target_wkw_info,
                    mag_factors,
                    interpolation_mode,
                    cube_edge_len,
                    target_cube_xyz,
                    compress,
                )
            )
        wait_and_ensure_success(executor.map_to_futures(downsample_cube_job, job_args))

    logging.info("Mag {0} successfully cubed".format(target_mag))


def downsample_cube_job(args):
    (
        source_wkw_info,
        target_wkw_info,
        mag_factors,
        interpolation_mode,
        cube_edge_len,
        target_cube_xyz,
        compress,
    ) = args
    logging.info("Downsampling of {}".format(target_cube_xyz))

    try:
        time_start("Downsampling of {}".format(target_cube_xyz))
        header_block_type = (
            wkw.Header.BLOCK_TYPE_LZ4HC if compress else wkw.Header.BLOCK_TYPE_RAW
        )

        with open_wkw(source_wkw_info) as source_wkw:
            num_channels = source_wkw.header.num_channels
            source_dtype = source_wkw.header.voxel_type
            with open_wkw(
                target_wkw_info, block_type=header_block_type, num_channels=num_channels
            ) as target_wkw:
                wkw_cubelength = (
                    source_wkw.header.file_len * source_wkw.header.block_len
                )
                shape = (num_channels,) + (wkw_cubelength,) * 3
                file_buffer = np.zeros(shape, source_dtype)
                tile_length = cube_edge_len
                tile_count_per_dim = wkw_cubelength // tile_length
                assert (
                    wkw_cubelength % cube_edge_len == 0
                ), "buffer_cube_size must be a divisor of wkw cube length"

                tile_indices = list(range(0, tile_count_per_dim))
                tiles = product(tile_indices, tile_indices, tile_indices)
                file_offset = wkw_cubelength * np.array(target_cube_xyz)

                for tile in tiles:
                    target_offset = np.array(
                        tile
                    ) * tile_length + wkw_cubelength * np.array(target_cube_xyz)
                    source_offset = mag_factors * target_offset

                    # Read source buffer
                    cube_buffer_channels = source_wkw.read(
                        source_offset,
                        (wkw_cubelength * np.array(mag_factors) // tile_count_per_dim),
                    )

                    for channel_index in range(num_channels):
                        cube_buffer = cube_buffer_channels[channel_index]

                        if np.all(cube_buffer == 0):
                            logging.debug(
                                "        Skipping empty cube {} (tile {})".format(
                                    target_cube_xyz, tile
                                )
                            )
                        else:
                            # Downsample the buffer

                            data_cube = downsample_cube(
                                cube_buffer, mag_factors, interpolation_mode
                            )

                            buffer_offset = target_offset - file_offset
                            buffer_end = buffer_offset + tile_length

                            file_buffer[
                                channel_index,
                                buffer_offset[0] : buffer_end[0],
                                buffer_offset[1] : buffer_end[1],
                                buffer_offset[2] : buffer_end[2],
                            ] = data_cube

                # Write the downsampled buffer to target
                target_wkw.write(file_offset, file_buffer)
        time_stop("Downsampling of {}".format(target_cube_xyz))

    except Exception as exc:
        logging.error("Downsampling of {} failed with {}".format(target_cube_xyz, exc))
        raise exc


def non_linear_filter_3d(data, factors, func):
    ds = data.shape
    assert not any((d % factor > 0 for (d, factor) in zip(ds, factors)))
    data = data.reshape((ds[0], factors[1], ds[1] // factors[1], ds[2]), order="F")
    data = data.swapaxes(0, 1)
    data = data.reshape(
        (
            factors[0] * factors[1],
            ds[0] * ds[1] // (factors[0] * factors[1]),
            factors[2],
            ds[2] // factors[2],
        ),
        order="F",
    )
    data = data.swapaxes(2, 1)
    data = data.reshape(
        (
            factors[0] * factors[1] * factors[2],
            (ds[0] * ds[1] * ds[2]) // (factors[0] * factors[1] * factors[2]),
        ),
        order="F",
    )
    data = func(data)
    data = data.reshape(
        (ds[0] // factors[0], ds[1] // factors[1], ds[2] // factors[2]), order="F"
    )
    return data


def linear_filter_3d(data, factors, order):
    factors = np.array(factors)

    if not np.all(factors == factors[0]):
        logging.debug(
            "the selected filtering strategy does not support anisotropic downsampling. Selecting {} as uniform downsampling factor".format(
                factors[0]
            )
        )
    factor = factors[0]

    ds = data.shape
    assert not any((d % factor > 0 for d in ds))
    return zoom(
        data,
        1 / factor,
        output=data.dtype,
        # 0: nearest
        # 1: bilinear
        # 2: bicubic
        order=order,
        # this does not mean nearest interpolation,
        # it corresponds to how the borders are treated.
        mode="nearest",
        prefilter=True,
    )


def _max(x):
    return np.max(x, axis=0)


def _min(x):
    return np.min(x, axis=0)


def _median(x):
    return np.median(x, axis=0).astype(x.dtype)


def _mode(x):
    """
    Fast mode implementation from: https://stackoverflow.com/a/35674754
    """
    # Check inputs
    ndim = x.ndim
    axis = 0
    # Sort array
    sort = np.sort(x, axis=axis)
    # Create array to transpose along the axis and get padding shape
    transpose = np.roll(np.arange(ndim)[::-1], axis)
    shape = list(sort.shape)
    shape[axis] = 1
    # Create a boolean array along strides of unique values
    strides = (
        np.concatenate(
            [
                np.zeros(shape=shape, dtype="bool"),
                np.diff(sort, axis=axis) == 0,
                np.zeros(shape=shape, dtype="bool"),
            ],
            axis=axis,
        )
        .transpose(transpose)
        .ravel()
    )
    # Count the stride lengths
    counts = np.cumsum(strides)
    counts[~strides] = np.concatenate([[0], np.diff(counts[~strides])])
    counts[strides] = 0
    # Get shape of padded counts and slice to return to the original shape
    shape = np.array(sort.shape)
    shape[axis] += 1
    shape = shape[transpose]
    slices = [slice(None)] * ndim
    slices[axis] = slice(1, None)
    # Reshape and compute final counts
    counts = counts.reshape(shape).transpose(transpose)[tuple(slices)] + 1

    # Find maximum counts and return modals/counts
    slices = [slice(None, i) for i in sort.shape]
    del slices[axis]
    index = np.ogrid[slices]
    index.insert(axis, np.argmax(counts, axis=axis))
    return sort[tuple(index)]


def downsample_cube(cube_buffer, factors, interpolation_mode):
    if interpolation_mode == InterpolationModes.MODE:
        return non_linear_filter_3d(cube_buffer, factors, _mode)
    elif interpolation_mode == InterpolationModes.MEDIAN:
        return non_linear_filter_3d(cube_buffer, factors, _median)
    elif interpolation_mode == InterpolationModes.NEAREST:
        return linear_filter_3d(cube_buffer, factors, 0)
    elif interpolation_mode == InterpolationModes.BILINEAR:
        return linear_filter_3d(cube_buffer, factors, 1)
    elif interpolation_mode == InterpolationModes.BICUBIC:
        return linear_filter_3d(cube_buffer, factors, 2)
    elif interpolation_mode == InterpolationModes.MAX:
        return non_linear_filter_3d(cube_buffer, factors, _max)
    elif interpolation_mode == InterpolationModes.MIN:
        return non_linear_filter_3d(cube_buffer, factors, _min)
    else:
        raise Exception("Invalid interpolation mode: {}".format(interpolation_mode))


def downsample_mag(
    path,
    layer_name,
    source_mag: Mag,
    target_mag: Mag,
    interpolation_mode="default",
    cube_edge_len=DEFAULT_EDGE_LEN,
    compress=False,
    args=None,
):
    if interpolation_mode == "default":
        interpolation_mode = (
            InterpolationModes.MEDIAN
            if layer_name == "color"
            else InterpolationModes.MODE
        )
    else:
        interpolation_mode = InterpolationModes[interpolation_mode.upper()]

    source_wkw_info = WkwDatasetInfo(path, layer_name, None, source_mag.to_layer_name())
    with open_wkw(source_wkw_info) as source:
        target_wkw_info = WkwDatasetInfo(
            path, layer_name, source.header.voxel_type, target_mag.to_layer_name()
        )
    downsample(
        source_wkw_info,
        target_wkw_info,
        source_mag,
        target_mag,
        interpolation_mode,
        cube_edge_len,
        compress,
        args,
    )


def downsample_mags(
    path: str,
    layer_name: str = None,
    from_mag: Mag = None,
    max_mag: Mag = Mag(32),
    interpolation_mode: str = "default",
    cube_edge_len: int = DEFAULT_EDGE_LEN,
    compress: bool = True,
    args=None,
    anisotropic: bool = True,
):
    assert layer_name and from_mag or not layer_name and not from_mag, (
        "You provided only one of the following "
        "parameters: layer_name, from_mag but both "
        "need to be set or none. If you don't provide "
        "the parameters you need to provide the path "
        "argument with the mag and layer to downsample"
        " (e.g dataset/color/1)."
    )
    scale = getattr(args, "scale", None) if args else None
    if not layer_name or not from_mag:
        layer_name = os.path.basename(os.path.dirname(path))
        from_mag = Mag(os.path.basename(path))
        path = os.path.dirname(os.path.dirname(path))

    if anisotropic:
        if scale is None:
            try:
                scale = read_datasource_properties(path)["scale"]
            except Exception as exc:
                logging.error(
                    f"Could not get the scale from the datasource-properties.json. Probably your path is wrong. "
                    "If you do not provide the layer_name or from_mag, they need to be included in the path."
                    "(e.g. dataset/color/1). Otherwise the path should just point at the dataset directory."
                    "the path: {path}"
                )
                raise exc
        downsample_mags_anisotropic(
            path,
            layer_name,
            from_mag,
            max_mag,
            scale,
            interpolation_mode,
            cube_edge_len,
            compress,
            args,
        )
    else:
        downsample_mags_isotropic(
            path,
            layer_name,
            from_mag,
            max_mag,
            interpolation_mode,
            cube_edge_len,
            compress,
            args,
        )


def downsample_mags_isotropic(
    path,
    layer_name,
    from_mag: Mag,
    max_mag: Mag,
    interpolation_mode,
    cube_edge_len,
    compress,
    args=None,
):

    target_mag = from_mag.scaled_by(2)
    while target_mag <= max_mag:
        source_mag = target_mag.divided_by(2)
        downsample_mag(
            path,
            layer_name,
            source_mag,
            target_mag,
            interpolation_mode,
            cube_edge_len,
            compress,
            args,
        )
        target_mag.scale_by(2)


def downsample_mags_anisotropic(
    path,
    layer_name,
    from_mag: Mag,
    max_mag: Mag,
    scale,
    interpolation_mode,
    cube_edge_len,
    compress,
    args=None,
):

    prev_mag = from_mag
    target_mag = get_next_anisotropic_mag(from_mag, scale)
    while target_mag <= max_mag:
        source_mag = prev_mag
        downsample_mag(
            path,
            layer_name,
            source_mag,
            target_mag,
            interpolation_mode,
            cube_edge_len,
            compress,
            args,
        )
        prev_mag = target_mag
        target_mag = get_next_anisotropic_mag(target_mag, scale)


def get_next_anisotropic_mag(mag, scale):
    max_index, min_index = detect_larger_and_smaller_dimension(scale)
    mag_array = mag.to_array()
    scale_increase = [1, 1, 1]
    if (
        mag_array[min_index] * scale[min_index]
        < mag_array[max_index] * scale[max_index]
    ):
        for i in range(len(scale_increase)):
            scale_increase[i] = 1 if i == max_index else 2
    else:
        scale_increase = [2, 2, 2]
    return Mag(
        [
            mag_array[0] * scale_increase[0],
            mag_array[1] * scale_increase[1],
            mag_array[2] * scale_increase[2],
        ]
    )


def detect_larger_and_smaller_dimension(scale):
    scale_np = np.array(scale)
    return np.argmax(scale_np), np.argmin(scale_np)


if __name__ == "__main__":
    args = create_parser().parse_args()
    setup_logging(args)

    from_mag = Mag(args.from_mag)
    max_mag = Mag(args.max)

    if args.anisotropic_target_mag:
        anisotropic_target_mag = Mag(args.anisotropic_target_mag)

        downsample_mag(
            args.path,
            args.layer_name,
            from_mag,
            anisotropic_target_mag,
            args.interpolation_mode,
            args.buffer_cube_size,
            not args.no_compress,
            args,
        )
    elif not args.isotropic:
        try:
            scale = read_datasource_properties(args.path)["scale"]
        except Exception as exc:
            logging.error(
                "Could not determine scale which is necessary "
                "to find target magnifications for anisotropic downsampling. "
                "Does the provided dataset have a datasource-properties.json file?"
            )
            raise exc

        downsample_mags_anisotropic(
            args.path,
            args.layer_name,
            from_mag,
            max_mag,
            scale,
            args.interpolation_mode,
            DEFAULT_EDGE_LEN,
            not args.no_compress,
            args,
        )
    else:
        downsample_mags_isotropic(
            args.path,
            args.layer_name,
            from_mag,
            max_mag,
            args.interpolation_mode,
            args.buffer_cube_size,
            not args.no_compress,
            args,
        )
