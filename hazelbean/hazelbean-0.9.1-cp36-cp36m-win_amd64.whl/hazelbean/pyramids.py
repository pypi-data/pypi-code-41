import os, sys, warnings, logging, inspect, math, time

from osgeo import gdal, osr, ogr
import numpy as np
import hazelbean as hb
import time
from collections import OrderedDict
from decimal import Decimal

L = hb.get_logger('pyramids', logging_level='info')

mollweide_compatible_resolutions = OrderedDict()
mollweide_compatible_resolutions[10.0] = 309.2208077590933 # calculated via hb.size_of_one_arcdegree_at_equator_in_meters / (60 * 6)
mollweide_compatible_resolutions[30.0] = 309.2208077590933 * (30.0 / 10.0)
mollweide_compatible_resolutions[300.0] = 309.2208077590933 * (300.0 / 10.0)
mollweide_compatible_resolutions[900.0] = 309.2208077590933 * (900.0 / 10.0)
mollweide_compatible_resolutions[1800.0] = 309.2208077590933 * (1800.0 / 10.0)
mollweide_compatible_resolutions[3600.0] = 309.2208077590933 * (3600.0 / 10.0)
mollweide_compatible_resolutions[7200.0] = 309.2208077590933 * (7200.0 / 10.0)
mollweide_compatible_resolutions[14400.0] = 309.2208077590933 * (14400.0 / 10.0)

# Define the resolutions compatible with pyramid calculation as key = arcseconds, value = resolution in 64 bit notation, precisely defined with the right amount of significant digits.
pyramid_compatible_arcseconds = [10.0,
                                                     30.0,
                                                     300.0,
                                                     900.0,
                                                     1800.0,
                                                     3600.0,
                                                     7200.0,
                                                     14400.0,]

pyramid_compatible_resolution_to_arcseconds = OrderedDict()
pyramid_compatible_resolution_to_arcseconds[0.002777777777777778] =    10.0
pyramid_compatible_resolution_to_arcseconds[0.008333333333333333] =    30.0
pyramid_compatible_resolution_to_arcseconds[0.08333333333333333] =   300.0
pyramid_compatible_resolution_to_arcseconds[0.25] =   900.0
pyramid_compatible_resolution_to_arcseconds[0.5] =  1800.0
pyramid_compatible_resolution_to_arcseconds[1.0] =  3600.0
pyramid_compatible_resolution_to_arcseconds[2.0] =  7200.0
pyramid_compatible_resolution_to_arcseconds[4.0] = 14400.0

pyramid_compatible_resolutions = OrderedDict()
pyramid_compatible_resolutions[10.0] =    0.002777777777777778
pyramid_compatible_resolutions[30.0] =    0.008333333333333333
pyramid_compatible_resolutions[300.0] =   0.08333333333333333
pyramid_compatible_resolutions[900.0] =   0.25
pyramid_compatible_resolutions[1800.0] =  0.5
pyramid_compatible_resolutions[3600.0] =  1.0
pyramid_compatible_resolutions[7200.0] =  2.0
pyramid_compatible_resolutions[14400.0] = 4.0

# Define the bounds of what should raise an assertion that the file is close but not exactly matching one of the supported resolutions.
pyramid_compatible_resolution_bounds = OrderedDict()
pyramid_compatible_resolution_bounds[10.0] =    (0.0027777, 0.00277778)
pyramid_compatible_resolution_bounds[30.0] =    (0.0083333, 0.00833334)
pyramid_compatible_resolution_bounds[300.0] =   (0.083333, 0.0833334)
pyramid_compatible_resolution_bounds[900.0] =   (0.24999, 0.25001)
pyramid_compatible_resolution_bounds[1800.0] =  (0.4999, 0.5001)
pyramid_compatible_resolution_bounds[3600.0] =  (0.999, 1.001)
pyramid_compatible_resolution_bounds[7200.0] =  (1.999, 2.001)
pyramid_compatible_resolution_bounds[14400.0] = (3.999, 4.001)


## DEFINED IN CONFIG:
# geotransform_global_4deg = (-180.0, 4.0, 0.0, 90.0, 0.0, -4.0)
# geotransform_global_2deg = (-180.0, 2.0, 0.0, 90.0, 0.0, -2.0)
# geotransform_global_1deg = (-180.0, 1.0, 0.0, 90.0, 0.0, -1.0)
# geotransform_global_30m = (-180.0, 0.5, 0.0, 90.0, 0.0, -0.5)
# geotransform_global_15m = (-180.0, 0.25, 0.0, 90.0, 0.0, -0.25)
# geotransform_global_5m = (-180.0, 0.08333333333333333, 0.0, 90.0, 0.0, -0.08333333333333333)  # NOTE, the 0.08333333333333333 is defined very precisely as the answer a 64 bit compiled python gives from the answer 1/12 (i.e. 5 arc minutes)
# geotransform_global_30s = (-180.0, 0.008333333333333333, 0.0, 90.0, 0.0, -0.008333333333333333)  # NOTE, the 0.008333333333333333 is defined very precisely as the answer a 64 bit compiled python gives from the answer 1/120 (i.e. 30 arc seconds) Note that this has 1 more digit than 1/12 due to how floating points are stored in computers via exponents.
# geotransform_global_10s = (-180.0, 0.002777777777777778, 0.0, 90.0, 0.0, -0.002777777777777778)  # NOTE, the 0.002777777777777778 is defined very precisely

pyramid_compatible_geotransforms = OrderedDict()
pyramid_compatible_geotransforms[10.0] = (-180.0, 0.002777777777777778, 0.0, 90.0, 0.0, -0.002777777777777778)
pyramid_compatible_geotransforms[30.0] = (-180.0, 0.008333333333333333, 0.0, 90.0, 0.0, -0.008333333333333333)
pyramid_compatible_geotransforms[300.0] = (-180.0, 0.08333333333333333, 0.0, 90.0, 0.0, -0.08333333333333333)
pyramid_compatible_geotransforms[900.0] = (-180.0, 0.25, 0.0, 90.0, 0.0, -0.25)
pyramid_compatible_geotransforms[1800.0] = (-180.0, 0.5, 0.0, 90.0, 0.0, -0.5)
pyramid_compatible_geotransforms[3600.0] = (-180.0, 1.0, 0.0, 90.0, 0.0, -1.0)
pyramid_compatible_geotransforms[7200.0] = (-180.0, 2.0, 0.0, 90.0, 0.0, -2.0)
pyramid_compatible_geotransforms[14400.0] = (-180.0, 4.0, 0.0, 90.0, 0.0, -4.0)

pyramid_compatible_overview_levels = OrderedDict()
pyramid_compatible_overview_levels[10.0] = [2, 3, 6, 12, 24, 30, 60, 90]
pyramid_compatible_overview_levels[30.0] = [2, 4, 8, 10, 20, 30, 60]
pyramid_compatible_overview_levels[300.0] = [2, 3, 6, 12]
pyramid_compatible_overview_levels[900.0] = [2, 4]
pyramid_compatible_overview_levels[1800.0] = [2]
pyramid_compatible_overview_levels[3600.0] = []
pyramid_compatible_overview_levels[7200.0] = []
pyramid_compatible_overview_levels[14400.0] = []

pyramid_compatible_full_overview_levels = OrderedDict()
pyramid_compatible_full_overview_levels[10.0] = [2, 3, 2*3, 4*3, 8*3, 10*3, 20*3, 30*3, 60*3, 120*3, 240*3, 480*3, 960*3]
pyramid_compatible_full_overview_levels[30.0] = [2, 4, 8, 10, 20, 30, 60, 120, 240, 480, 960]
pyramid_compatible_full_overview_levels[300.0] = [2, 3, 6, 12, 24, 48, 96]
pyramid_compatible_full_overview_levels[900.0] = [2, 4, 8, 16, 32]
pyramid_compatible_full_overview_levels[1800.0] = [2, 4, 8, 16]
pyramid_compatible_full_overview_levels[3600.0] = [2, 4, 8]
pyramid_compatible_full_overview_levels[7200.0] = [2, 4]
pyramid_compatible_full_overview_levels[14400.0] = [2]


def get_global_block_list_from_resolution(coarse_resolution, fine_resolution):
    """Get list of 6-length lists that define tiles of the world, based only on coarse and fine resolutions. Returns list of lists.

    Return: [ul fine col, ul fine row, fine width, fine height, coarse col, coarse row]
    """
    n_h_blocks = int(360.0 / float(coarse_resolution))
    n_v_blocks = int(180.0 / float(coarse_resolution))
    n_blocks = n_h_blocks * n_v_blocks

    block_list = []
    block_size = coarse_resolution / fine_resolution
    for h_b in range(n_h_blocks):

        for v_b in range(n_v_blocks):
            block_list.append([int(h_b * block_size), int(v_b * block_size), int(block_size), int(block_size), int(h_b), int(v_b)])

    return block_list



def determine_pyramid_resolution(input_path):
    """ Check if input_path has a resolution the is exactly equal or close to a pyramid-supported resolution.

    Return the input resolution if correct, the snapped-to resolution if close enough. Otherwise raise exception."""
    ds = gdal.OpenEx(input_path)
    if ds is None:
        raise Exception('Could not open ' + str(input_path))
    gt = ds.GetGeoTransform()
    ulx, xres, _, uly, _, yres = gt[0], gt[1], gt[2], gt[3], gt[4], gt[5]

    resolution = None
    if xres in pyramid_compatible_resolutions.keys():
        resolution = xres

    else:
        for k, v in pyramid_compatible_resolution_bounds.items():
            if v[0] < xres < v[1]:
                resolution = pyramid_compatible_resolutions[k]
                if resolution != xres:
                    L.info('Input res was ' + str(xres) + ' for ' + str(input_path) + ' but should have been ' + str(resolution) + ' to make pyramid-ready.')

    if resolution is None:
        raise NameError('determine_pyramid_resolution found no suitably close resolution for ' + str(input_path) + ' with ulx, xres, uly, yres of ' + str(ulx) + ' ' + str(xres) + ' ' + str(uly) + ' ' + str(yres) + ' ')

    ds = None
    return resolution

def make_path_global_pyramid(input_path, output_path=None, make_overviews=True, overwrite_overviews=False,
                             calculate_stats=True, overwrite_stats=False,
                             clean_temporary_files=False, raise_exception=False, make_overviews_external=True, set_ndv_below_value=None, verbose=True):
    """Throw exception if input_path is not pyramid-ready. This requires that the file be global, geographic projection, and with resolution
    that is a factor/multiple of arcdegrees.

    If output_path is specified, write to that location. Otherwise, make changes in-place but saving a temporary backup file of the input.

    # LEARNING POINT: Able to access specific overview bands!
    # ovr_band = src_ds.GetRasterBand(i).GetOverview(1)
    """
    if verbose:
        L.info('Running make_path_global_pyramid on ' + str(input_path))

    resolution = hb.determine_pyramid_resolution(input_path)
    arcseconds = pyramid_compatible_resolution_to_arcseconds[resolution]

    ds = gdal.OpenEx(input_path)
    n_c, n_r = ds.RasterXSize, ds.RasterYSize
    gt = ds.GetGeoTransform()

    ulx, xres, _, uly, _, yres = gt[0], gt[1], gt[2], gt[3], gt[4], gt[5]
    if verbose:
        L.info('   ulx: ' + str(ulx) + ', uly: ' + str(uly) + ', xres: ' + str(xres) + ', yres: ' + str(yres) + ', n_c: ' + str(n_c) + ', n_r: ' + str(n_r))

    if -180.001 < ulx < -179.999:
        ulx = -180.0
    if 90.001 > uly > 89.999:
        uly = 90.0

    if ulx != -180.0 or uly != 90.0:
        result_string = 'Input path not pyramid ready because UL not at -180 90 (or not close enough): ' + str(input_path)
        if raise_exception:
            raise NameError(result_string)
        else:
            L.info(result_string)
            return False
    lrx = ulx + resolution * n_c
    lry = uly + -1.0 * resolution * n_r

    if lrx != 180.0 or lry != -90.0:

        result_string = 'Input path not pyramid ready because its not the right size: ' + str(input_path) + '\n    ulx ' + str(ulx) + ', xres ' + str(xres) + ', uly ' + str(uly) + ', yres ' + str(yres) + ', lrx ' + str(lrx) + ', lry ' + str(lry)
        if raise_exception:
            raise NameError(result_string)
        else:
            L.warning(result_string)
            return False

    output_geotransform = pyramid_compatible_geotransforms[arcseconds]
    ds = None

    if output_geotransform != gt:
        L.warning('Changing geotransform of ' + str(input_path) + ' to ' + str(output_geotransform) + ' from ' + str(gt))

    hb.set_geotransform_to_tuple(input_path, output_geotransform)

    ds = gdal.OpenEx(input_path, gdal.GA_Update)
    md = ds.GetMetadata()
    image_structure = ds.GetMetadata('IMAGE_STRUCTURE')
    compression = image_structure.get('COMPRESSION', None)
    if verbose:
        L.info('Compression of ' + str(input_path) + ': ' + str(compression))

    # Consider operations that may need rewriting the underlying data
    rewrite_array = False

    # Check if compressed (pyramidal file standards require compression)
    if str(compression).lower() not in  ['deflate']:
        L.critical('rewrite_array triggered because compression was not deflate.')
        rewrite_array = True

    data_type = ds.GetRasterBand(1).DataType
    ndv = ds.GetRasterBand(1).GetNoDataValue()

    if data_type >= 6:
        DEFAULT_GTIFF_CREATION_OPTIONS = (
            'TILED=YES',
            'BIGTIFF=YES',
            'COMPRESS=DEFLATE',
            'BLOCKXSIZE=256',
            'BLOCKYSIZE=256',
            'PREDICTOR=3',
        )
    else:
        options = hb.DEFAULT_GTIFF_CREATION_OPTIONS

    new_ndv = False
    below_ndv = False

    L.info('input data_type: ' + str(data_type) + ', input ndv: ' + str(ndv))
    if data_type == 1:
        if ndv != 255:
            old_ndv = ndv
            ndv = 255
            L.critical('rewrite_array triggered because ndv was not 255 and datatype was 1.')
            rewrite_array = True
            new_ndv = True
    elif data_type < 6:
        if ndv != 9999:  # NOTE INT
            old_ndv = ndv
            ndv = 9999
            L.critical('rewrite_array triggered because ndv was not 9999 and datatype was of int type.')
            rewrite_array = True
            new_ndv = True
    else:
        if ndv != -9999.0:
            old_ndv = ndv
            ndv = -9999.0
            L.critical('rewrite_array triggered because ndv was not -9999.0 and datatype was > 5 (i.e. is a float).')
            rewrite_array = True
            new_ndv = True

    if set_ndv_below_value is not None:
        if data_type == 1:
            if ndv != 255:
                ndv = 255
                rewrite_array = True
                new_ndv = True
        elif data_type < 6:
            if ndv != 9999:  # NOTE INT
                ndv = 9999
                rewrite_array = True
                new_ndv = True
        else:
            if ndv != -9999.0:
                ndv = -9999.0
                rewrite_array = True
                new_ndv = True

    if verbose:
        L.info('output data_type: ' + str(data_type) + ', output ndv: ' + str(ndv))

    ds.SetMetadataItem('last_processing_on', str(time.time()))

    ds = None
    if verbose:
        L.info('rewrite_array ' + str(rewrite_array))

    displacement_path = hb.temp('.tif', filename_start='displaced_by_make_path_global_pyramid_on_' + str(hb.file_root(input_path)), remove_at_exit=clean_temporary_files)
    temp_write_path = hb.temp('.tif', filename_start='temp_write_' + str(hb.file_root(input_path)), remove_at_exit=clean_temporary_files)
    # if rewrite_array:
    #     L.info('make_path_global_pyramid triggered rewrite_array for ' + str(input_path))
    #     input_ds = gdal.OpenEx(input_path)
    #
    #     driver = gdal.GetDriverByName('GTiff')
    #     new_ds = driver.Create(temp_write_path, n_c, n_r, 1, data_type, options=options)
    #     new_ds.SetGeoTransform(output_geotransform)
    #     new_ds.SetProjection(hb.wgs_84_wkt)
    #     new_ds.GetRasterBand(1).SetNoDataValue(ndv)
    #
    #     new_ds.GetRasterBand(1).WriteArray(input_ds.ReadAsArray().astype(hb.gdal_number_to_numpy_type[data_type]))
    #
    #     input_ds = None
    #     new_ds = None

    if rewrite_array:
        L.info('make_path_spatially_clean triggered rewrite_array for ' + str(input_path))
        input_ds = gdal.OpenEx(input_path)

        driver = gdal.GetDriverByName('GTiff')
        new_ds = driver.Create(temp_write_path, n_c, n_r, 1, data_type, options=options)
        new_ds.SetGeoTransform(output_geotransform)
        new_ds.SetProjection(hb.wgs_84_wkt)
        new_ds.GetRasterBand(1).SetNoDataValue(ndv)

        array = input_ds.ReadAsArray().astype(hb.gdal_number_to_numpy_type[data_type])

        if new_ndv and set_ndv_below_value is None:
            np.where(np.isclose(array, old_ndv), ndv, array)

        if set_ndv_below_value is not None:
            array[array < set_ndv_below_value] = ndv

        new_ds.GetRasterBand(1).WriteArray(array)

        input_ds = None
        new_ds = None

    # Rename files to displace old input. This has to be done before external-file operations are completed.
    if output_path:
        hb.create_directories(os.path.split(output_path)[0])
        os.rename(temp_write_path, output_path)
        processed_path = output_path
    else:
        if os.path.exists(temp_write_path):
            os.rename(input_path, displacement_path)
            os.rename(temp_write_path, input_path)
        processed_path = input_path


    # Do metadata and compression tasks
    if make_overviews_external:
        ds = gdal.OpenEx(processed_path)
    else:
        ds = gdal.OpenEx(processed_path, gdal.GA_Update)

    # make_rat = False  # Arcaic form from ESRI, KEPT FOR REFERENCE ONLY
    # if make_rat:
    #     rat = gdal.RasterAttributeTable()
    #
    #     attr_dict = {0: 0, 1: 11, 2: 22}
    #     column_name = 'values'
    #
    #     rat.SetRowCount(len(attr_dict))
    #
    #     # create columns
    #     rat.CreateColumn('Value', gdal.GFT_Integer, gdal.GFU_MinMax)
    #     rat.CreateColumn(column_name, gdal.GFT_String, gdal.GFU_Name)
    #
    #     row_count = 0
    #     for key in sorted(attr_dict.keys()):
    #         rat.SetValueAsInt(row_count, 0, int(key))
    #         rat.SetValueAsString(row_count, 1, attr_dict[key])
    #         row_count += 1
    #
    #     ds.GetRasterBand(1).SetDefaultRAT(rat)

    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
    # gdal.SetConfigOption('USE_RRD', 'YES')  # FORCE EXTERNAL ,possibly as ovr? # USE_RRD is outdated (saves x.aux file). If you want external, just make sure you open the DS in read only.

    if make_overviews or overwrite_overviews:
        if not os.path.exists(processed_path + '.ovr') or overwrite_overviews:
            if verbose:
                L.info('Starting to make overviews for ' + str(processed_path))
            ds.BuildOverviews('nearest', pyramid_compatible_overview_levels[arcseconds])  # Based on commonly used data shapes

    if calculate_stats or overwrite_stats:
        if not os.path.exists(processed_path + '.aux.xml') or overwrite_overviews:
            if verbose:
                L.info('Starting to calculate stats for ' + str(processed_path))
            ds.GetRasterBand(1).ComputeStatistics(False)  # False here means approx NOT okay
            ds.GetRasterBand(1).GetHistogram(approx_ok=0)
    ds = None
    return True

def make_dir_global_pyramid(input_dir, output_path=None, make_overviews=True, calculate_stats=True, clean_temporary_files=False,
                            resolution=None, raise_exception=False, make_overviews_external=True, verbose=True):
    """Throw exception if input_path is not pyramid-ready. This requires that the file be global, geographic projection, and with resolution
    that is a factor/multiple of arcdegrees.

    If output_path is specified, write to that location. Otherwise, make changes in-place but saving a temporary backup file of the input.

    # LEARNING POINT
    # ovr_band = src_ds.GetRasterBand(i).GetOverview(1)
    """
    for file_path in hb.list_filtered_paths_nonrecursively(input_dir, include_extensions='.tif'):
        hb.make_path_global_pyramid(file_path, output_path=output_path, make_overviews=make_overviews, calculate_stats=calculate_stats, clean_temporary_files=clean_temporary_files,
                                    resolution=resolution, raise_exception=raise_exception, make_overviews_external=make_overviews_external, verbose=verbose)


def make_path_spatially_clean(input_path, output_path=None, make_overviews=True, overwrite_overviews=False,
                              calculate_stats=True, overwrite_stats=False, clean_temporary_files=False,
                              resolution=None,
                              raise_exception=False, make_overviews_external=True,
                              set_ndv_below_value=None, verbose=True):


    """Similar to make_path_global_pyramid, except doesnt change anything that would alter the data.
    Specifically, it only changes (optionally) compression, overviews, and NDV (based on observed data_type_.

    output_path
    overwrite_overviews
    resolution


    """
    ds = gdal.OpenEx(input_path, gdal.GA_Update)
    n_c, n_r = ds.RasterXSize, ds.RasterYSize
    output_geotransform = ds.GetGeoTransform()

    md = ds.GetMetadata()
    image_structure = ds.GetMetadata('IMAGE_STRUCTURE')
    compression = image_structure.get('COMPRESSION', None)

    # Consider operations that may need rewriting the underlying data
    rewrite_array = False

    # Check if compressed (pyramidal file standards require compression)
    if str(compression).lower() != 'deflate':
        rewrite_array = True

    L.info('Running make_path_spatially_clean on ' + str(input_path))
    data_type = ds.GetRasterBand(1).DataType
    ndv = ds.GetRasterBand(1).GetNoDataValue()
    ds.SetMetadataItem('last_processing_on', str(time.time()))
    # ds = None

    if data_type >= 6:
        options = (
            'TILED=YES',
            'BIGTIFF=YES',
            'COMPRESS=DEFLATE',
            'BLOCKXSIZE=256',
            'BLOCKYSIZE=256',
            'PREDICTOR=3', #
        )
    else:
        options = hb.DEFAULT_GTIFF_CREATION_OPTIONS


    new_ndv = False
    below_ndv = False

    L.info('input data_type: ' + str(data_type) + ', input ndv: ' + str(ndv))
    if data_type == 1:
        if ndv != 255:
            old_ndv = ndv
            ndv = 255
            L.critical('rewrite_array triggered because ndv was not 255 and datatype was 1.')
            rewrite_array = True
            new_ndv = True
    elif data_type < 6:
        if ndv != 9999:  # NOTE INT
            old_ndv = ndv
            ndv = 9999
            L.critical('rewrite_array triggered because ndv was not 9999 and datatype was of int type.')
            rewrite_array = True
            new_ndv = True
    else:
        if ndv != -9999.0:
            old_ndv = ndv
            ndv = -9999.0
            L.critical('rewrite_array triggered because ndv was not -9999.0 and datatype was > 5 (i.e. is a float).')
            rewrite_array = True
            new_ndv = True

    if set_ndv_below_value is not None:
        if data_type == 1:
            if ndv != 255:
                ndv = 255
                rewrite_array = True
                new_ndv = True
        elif data_type < 6:
            if ndv != 9999:  # NOTE INT
                ndv = 9999
                rewrite_array = True
                new_ndv = True
        else:
            if ndv != -9999.0:
                ndv = -9999.0
                rewrite_array = True
                new_ndv = True

    L.info('output data_type: ' + str(data_type) + ', output ndv: ' + str(ndv))



    ds = None

    L.info('rewrite_array ' + str(rewrite_array))
    temp_write_path = hb.temp('.tif', filename_start='temp_write_' + str(hb.file_root(input_path)), remove_at_exit=clean_temporary_files)
    displacement_path = hb.temp('.tif', filename_start='displaced_by_make_path_global_pyramid_on_' + str(hb.file_root(input_path)), remove_at_exit=clean_temporary_files)

    if rewrite_array:

        input_ds = gdal.OpenEx(input_path)

        driver = gdal.GetDriverByName('GTiff')
        new_ds = driver.Create(temp_write_path, n_c, n_r, 1, data_type, options=options)
        new_ds.SetGeoTransform(output_geotransform)
        new_ds.SetProjection(hb.wgs_84_wkt)
        new_ds.GetRasterBand(1).SetNoDataValue(ndv)

        array = input_ds.ReadAsArray().astype(hb.gdal_number_to_numpy_type[data_type])

        if new_ndv and  set_ndv_below_value is None:
            np.where(np.isclose(array, old_ndv), ndv, array)
            # array[array == old_ndv] = ndv

        if set_ndv_below_value is not None:
            # array = np.where(array < set_ndv_below_value, ndv, array)
            array[array < set_ndv_below_value] = ndv

        new_ds.GetRasterBand(1).WriteArray(array)

        input_ds = None
        new_ds = None

        # Rename files to displace old input. This has to be done before external-file operations are completed.
        os.rename(input_path, displacement_path)
        os.rename(temp_write_path, input_path)
    # Rename files to displace old input. This has to be done before external-file operations are completed.
    if output_path:
        hb.create_directories(os.path.split(output_path)[0])
        os.rename(temp_write_path, output_path)
        processed_path = output_path
    else:
        if os.path.exists(temp_write_path):
            os.rename(input_path, displacement_path)
            os.rename(temp_write_path, input_path)
        processed_path = input_path

    # Do metadata and compression tasks
    if make_overviews_external:
        ds = gdal.OpenEx(input_path)
    else:
        ds = gdal.OpenEx(input_path, gdal.GA_Update)

    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
    # gdal.SetConfigOption('USE_RRD', 'YES')  # FORCE EXTERNAL ,possibly as ovr? # USE_RRD is outdated (saves x.aux file). If you want external, just make sure you open the DS in read only.

    if make_overviews or overwrite_overviews:
        if not os.path.exists(processed_path + '.ovr') or overwrite_overviews:
            if verbose:
                L.info('Starting to make overviews for ' + str(processed_path))
            ds.BuildOverviews('nearest', [2, 4, 8, 16, 32])  # Based on commonly used data shapes

    if calculate_stats or overwrite_stats:
        if not os.path.exists(processed_path + '.aux.xml') or overwrite_overviews:
            if verbose:
                L.info('Starting to calculate stats for ' + str(processed_path))
            ds.GetRasterBand(1).ComputeStatistics(False)  # False here means approx NOT okay
            ds.GetRasterBand(1).GetHistogram(approx_ok=0)


    ds = None
    return True


def compress_path(input_path, clean_temporary_files=False):
    hb.make_path_spatially_clean(input_path, make_overviews=False, calculate_stats=False, clean_temporary_files=clean_temporary_files)

def assert_paths_same_pyramid(path_1, path_2, raise_exception=False):

    bool_3 = hb.is_path_same_geotransform(path_1, path_2)

    results = [bool_3]
    if all(results):
        return True
    else:
        result_string = '\nPaths not pyramidal:\n' + str(path_1) + '\n' + str(path_2)
        if raise_exception:
            if raise_exception:
                raise NameError(result_string)
            else:
                L.critical(result_string)
                return False


def set_geotransform_to_tuple(input_path, desired_geotransform):
    """
    FROM CONFIG:
    geotransform_global_5m = (-180.0, 0.08333333333333333, 0.0, 90.0, 0.0, -0.08333333333333333)  # NOTE, the 0.08333333333333333 is defined very precisely as the answer a 64 bit compiled python gives from the answer 1/12 (i.e. 5 arc minutes)
    geotransform_global_30s = (-180.0, 0.008333333333333333, 0.0, 90.0, 0.0, -0.008333333333333333)  # NOTE, the 0.008333333333333333 is defined very precisely as the answer a 64 bit compiled python gives from the answer 1/120 (i.e. 30 arc seconds) Note that this has 1 more digit than 1/12 due to how floating points are stored in computers via exponents.
    geotransform_global_10s = (-180.0, 0.002777777777777778, 0.0, 90.0, 0.0, -0.002777777777777778)  # NOTE, the 0.002777777777777778 is defined very precisely
    """
    ds = gdal.OpenEx(input_path, gdal.GA_Update)
    gt = ds.GetGeoTransform()
    ds.SetGeoTransform(desired_geotransform)
    gt = ds.GetGeoTransform()
    ds = None

def set_projection_to_wkt(input_path, desired_projection_wkt):
    ds = gdal.OpenEx(input_path, gdal.GA_Update)
    ds.SetProjection(desired_projection_wkt)
    ds = None

def load_geotiff_chunk_by_cr_size(input_path, cr_size, datatype=None, output_path=None, ndv=None):
    """Convenience function to load a chunk of an array given explicit row and column info."""
    ds = gdal.OpenEx(input_path)
    n_c, n_r = ds.RasterXSize, ds.RasterYSize

    c = int(cr_size[0])
    r = int(cr_size[1])
    c_size = int(cr_size[2])
    r_size = int(cr_size[3])

    # if not 0 <= r <= n_r:
    #     raise NameError('r given to load_geotiff_chunk_by_cr_size didnt fit. r, n_r: ' + str(r) + ' ' + str(n_r) + ' for path ' + input_path)
    #
    # if not 0 <= c <= n_c:
    #     raise NameError('c given to load_geotiff_chunk_by_cr_size didnt fit. c, n_c: ' + str(c) + ' ' + str(n_c) + ' for path ' + input_path)
    #
    # if not 0 <= r + r_size <= n_r:
    #     raise NameError('r_size given to load_geotiff_chunk_by_cr_size didnt fit. r_size, n_r: ' + str(r_size) + ' ' + str(n_r) + ' for path ' + input_path)
    #
    # if not 0 <= c + c_size <= n_c:
    #     raise NameError('c given to load_geotiff_chunk_by_cr_size didnt fit. c, n_c: ' + str(c_size) + ' ' + str(n_c) + ' for path ' + input_path)
    # callback = hb.make_logger_callback("load_geotiff_chunk_by_cr_size %.1f%% complete %s")
    # callback = hb.invoke_timed_callback("load_geotiff_chunk_by_cr_size %.1f%% complete %s")
    callback = hb.make_simple_gdal_callback("load_geotiff_chunk_by_cr_size %.1f%% complete %s")

    a = ds.ReadAsArray(c, r, c_size, r_size, buf_type=datatype, callback=callback, callback_data=[input_path]).astype(datatype)

    if output_path is not None:

        if datatype is not None:
            data_type = datatype

        data_type = hb.get_datatype_from_uri(input_path)

        src_ndv = hb.get_ndv_from_path(input_path)
        if ndv is None:
            ndv = hb.get_ndv_from_path(input_path)

        if ndv != src_ndv:
            a = np.where(np.isclose(a, src_ndv), ndv, a)

        gt = list(hb.get_geotransform_uri(input_path))
        lat, lon = hb.rc_path_to_latlon(r, c, input_path)
        gt[0] = lon
        gt[3] = lat
        geotransform_override = gt
        projection_override = hb.get_dataset_projection_wkt_uri(input_path)
        n_cols_override, n_rows_override = (c_size, r_size)

        if output_path is True:
            output_path = hb.temp('.tif')

        hb.save_array_as_geotiff(a, output_path, data_type=data_type, ndv=ndv, geotransform_override=geotransform_override,
                                 projection_override=projection_override, n_cols_override=n_cols_override, n_rows_override=n_rows_override)

    return a

def load_geotiff_chunk_by_bb(input_path, bb, inclusion_behavior='centroid', datatype=None, output_path=None, ndv=None):
    """Load a geotiff chunk as a numpy array from input_path. Requires that input_path be pyramid_ready. If datatype given,
    returns the numpy array by GDAL number, defaulting to the type the data was saved as.

    Inclusion_behavior determines how cells that are only partially within the bb are considered. Default is centroid, but can be exclusive or exclusive.

    inclusion_behavior = one of 'centroid', 'inclusive', 'exclusive'

    if given output_path will make it write there (potentially EXTREMELY computaitonally slow)
    if output_path is True and not a string, will save to a atemp file.
     """

    c, r, c_size, r_size = hb.bb_path_to_cr_size(input_path, bb, inclusion_behavior=inclusion_behavior)
    L.info('bb_path_to_cr_widthheight generated', c, r, c_size, r_size)

    a = hb.load_geotiff_chunk_by_cr_size(input_path, (c, r, c_size, r_size), datatype)

    if output_path is not None:

        data_type = hb.get_datatype_from_uri(input_path)

        src_ndv = hb.get_ndv_from_path(input_path)
        if ndv is None:
            ndv = hb.get_ndv_from_path(input_path)

        if ndv != src_ndv:
            a = np.where(np.isclose(a, src_ndv), ndv, a)

        gt = list(hb.get_geotransform_uri(input_path))
        gt[0] = bb[0]
        gt[3] = bb[3]
        geotransform_override = gt
        projection_override = hb.get_dataset_projection_wkt_uri(input_path)
        n_cols_override, n_rows_override = (c_size, r_size)

        if output_path is True:
            output_path = hb.temp('.tif')

        hb.save_array_as_geotiff(a, output_path, data_type=data_type, ndv=ndv, geotransform_override=geotransform_override,
                                 projection_override=projection_override, n_cols_override=n_cols_override, n_rows_override=n_rows_override)

    return a

def bb_path_to_cr_size(input_path, bb, inclusion_behavior='centroid'):
    # BB must be in lat-lon units (not projected units yet) in xmin, ymin, xmax, ymax order
    # Useful for getting gdal-type cr_widthheight from a subset of a raster via it's bb from path.
    # Note that gdal Open uses col, row, n_cols, n_row notation. This function converts lat lon bb to rc in this order based on the proportional size of the input_path.
    if not os.path.exists(input_path):
        L.warning('bb_path_to_cr_size unable to open ' + str(input_path))
    ds = gdal.OpenEx(input_path)
    n_c, n_r = ds.RasterXSize, ds.RasterYSize
    gt = hb.get_geotransform_uri(input_path)
    lower_lat = bb[1]
    upper_lat = bb[3]
    left_lon = bb[0]
    right_lon = bb[2]

    if inclusion_behavior == 'inclusive':
        r, c = hb.latlon_path_to_rc(upper_lat, left_lon, input_path, r_shift_direction='up', c_shift_direction='left')
        r_right, c_right = hb.latlon_path_to_rc(lower_lat, right_lon, input_path, r_shift_direction='down', c_shift_direction='right')
    elif inclusion_behavior == 'exclusive':
        r, c = hb.latlon_path_to_rc(upper_lat, left_lon, input_path, r_shift_direction='down', c_shift_direction='right')
        r_right, c_right = hb.latlon_path_to_rc(lower_lat, right_lon, input_path, r_shift_direction='up', c_shift_direction='left')
    else:
        r, c = hb.latlon_path_to_rc(upper_lat, left_lon, input_path, r_shift_direction='centered', c_shift_direction='centered')
        r_right, c_right = hb.latlon_path_to_rc(lower_lat, right_lon, input_path, r_shift_direction='centered', c_shift_direction='centered')
    r_size = r_right - r
    c_size = c_right - c

    if c_size == 0 or r_size == 0:
        L.debug('Inputs given result in zero size: ' + str(c) + ' ' + str(r) + ' ' + str(c_size) + ' ' + str(r_size))

    return round(c), round(r), round(c_size), round(r_size)


def latlon_path_to_rc(lat, lon, input_path, r_shift_direction='centered', c_shift_direction='centered'):
    """Calculate the row and column index from a raster at input_path for a given lat, lon value.
    Because latlon is continuous and rc is integer, specify the behavior for rounding. Default is centered, but can shift in any direction
    for applications that need precision (e.g. clipping country borders and requiring exclusivity.
    """

    ds = gdal.OpenEx(input_path)
    n_c, n_r = Decimal(ds.RasterXSize), Decimal(ds.RasterYSize)
    gt = ds.GetGeoTransform()
    ulx, xres, _, uly, _, yres = Decimal(gt[0]), Decimal(gt[1]), Decimal(gt[2]), Decimal(gt[3]), Decimal(gt[4]), Decimal(gt[5])

    lat = Decimal(lat)
    lon = Decimal(lon)
    gt_xmin_lon = ulx
    gt_ymin_lat = uly + yres * n_r
    gt_xmax_lon = ulx + xres * n_c
    gt_ymax_lat = uly
    prop_r = (gt_ymax_lat - lat) / (gt_ymax_lat - gt_ymin_lat)
    # prop_r = (lat - gt_ymin_lat) / (gt_ymax_lat - gt_ymin_lat)
    prop_c = (lon - gt_xmin_lon) / (gt_xmax_lon - gt_xmin_lon)
    r = prop_r * n_r
    c = prop_c * n_c

    initial_r = r
    initial_c = c

    if r_shift_direction == 'up':
        r = math.floor(r)
    elif r_shift_direction == 'down':
        r = math.ceil(r)
    elif r_shift_direction == 'nearest':
        r = round(r)

    if c_shift_direction == 'left':
        c = math.floor(c)
    elif c_shift_direction == 'right':
        c = math.ceil(c)
    elif c_shift_direction == 'nearest':
        c = round(c)

    verbose = False
    if verbose:
        print ('latlon_path_to_rc generated: lat', lat, 'lon', lon, 'n_c', n_c, 'n_r', n_r, 'ulx', ulx, 'xres', xres, 'uly', uly, 'yres', yres, 'prop_r', prop_r, 'prop_c', prop_c, 'r', r, 'c', c)

    return r, c

def rc_path_to_latlon(r, c, input_path):
    ds = gdal.OpenEx(input_path)
    n_c, n_r = ds.RasterXSize, ds.RasterYSize
    gt = ds.GetGeoTransform()

    ulx, xres, _, uly, _, yres = gt[0], gt[1], gt[2], gt[3], gt[4], gt[5]

    prop_r = r / n_r
    prop_c = c / n_c

    lat = uly - prop_r * (uly - (uly + yres * n_r))
    lon = ulx - prop_c * (ulx - (ulx + xres * n_c))

    # CAUTION: Recall that a geotransform is ul_LON, xres, 0 ul_LAT, 0, yres)
    return lat, lon

def generate_geotransform_of_chunk_from_cr_size_and_larger_path(cr_size, larger_raster_path):
    # gt = [0, 0, 0, 0, 0, 0]
    lat, lon = hb.rc_path_to_latlon(cr_size[1], cr_size[0], larger_raster_path)
    res = hb.get_cell_size_from_uri(larger_raster_path)
    return [lon, res, 0., lat, 0., -res]

def is_path_same_geotransform(input_path, match_path, raise_exception=False):
    """Throw exception if input_path is not the same geotransform as the match path."""
    ds = gdal.OpenEx(input_path)
    gt = ds.GetGeoTransform()

    ds_match = gdal.OpenEx(match_path)
    gt_match = ds_match.GetGeoTransform()

    if not gt == gt_match:
        result_string = 'Input path did not have the same geotransform as match path:\n' + str(input_path) + '\n' + str(gt) + '\n' + str(match_path) + '\n' + str(gt_match)
        if raise_exception:
            raise NameError(result_string)
        else:
            L.warning(result_string)
            return False


    # Passed all the tests
    return True



def get_aspect_ratio_of_two_arrays(coarse_res_array, fine_res_array):
    # Test that map resolutions are workable multiples of each other
    # assert int(round(fine_res_array.shape[0] / coarse_res_array.shape[0])) == int(
    #     round(fine_res_array.shape[1] / coarse_res_array.shape[1]))
    aspect_ratio = int(round(fine_res_array.shape[0] / coarse_res_array.shape[0]))
    return aspect_ratio


def calc_proportion_of_coarse_res_with_valid_fine_res(coarse_res, fine_res):
    """Useful wehn allocating to border cells."""

    if not isinstance(coarse_res, np.ndarray):
        try:
            coarse_res = hb.as_array(coarse_res).astype(np.float64)
        except:
            raise NameError('Unable to load ' + str(coarse_res) + ' as array in calc_proportion_of_coarse_res_with_valid_fine_res.')

    if not isinstance(fine_res, np.ndarray):
        try:
            fine_res = hb.as_array(fine_res).astype(np.int64)
        except:
            raise NameError('Unable to load ' + str(fine_res) + ' as array in calc_proportion_of_coarse_res_with_valid_fine_res.')

    aspect_ratio = get_aspect_ratio_of_two_arrays(coarse_res, fine_res)

    #
    # coarse_res_proportion_array = np.zeros(coarse_res.shape).astype(np.float64)
    # fine_res_proportion_array = np.zeros(fine_res.shape).astype(np.float64)

    proportion_valid_fine_per_coarse_cell = hb.cython_calc_proportion_of_coarse_res_with_valid_fine_res(coarse_res.astype(np.float64), fine_res.astype(np.int64))

    return proportion_valid_fine_per_coarse_cell

def is_compressed(input_path):
    # Make flex?

    ds = gdal.OpenEx(input_path)
    md = ds.GetMetadata()
    image_structure = ds.GetMetadata('IMAGE_STRUCTURE')
    compression = image_structure.get('COMPRESSION', False)

    if compression:
        return True
    else:
        return False


def add_rows_or_cols_to_geotiff(input_path, r_above, r_below, c_left, c_right, output_path=None, fill_value=None, remove_temporary_files=False):
    # if output_path is None, assume overwriting
    input_ds = gdal.OpenEx(input_path)
    input_gt = input_ds.GetGeoTransform()
    input_projection = input_ds.GetProjection()
    datatype = hb.get_raster_info_hb(input_path)['datatype']

    callback = hb.make_simple_gdal_callback('Reading array')
    input_array = input_ds.ReadAsArray(callback=callback)
    output_gt = list(input_gt)
    output_gt = [input_gt[0] + c_left * input_gt[1], input_gt[1], 0.0, input_gt[3] + r_above * input_gt[1], 0.0, input_gt[5]]

    if fill_value is None:
        fill_value = input_ds.GetRasterBand(1).GetNoDataValue()

    n_rows = int(input_ds.RasterYSize + r_above + r_below)
    n_cols = int(input_ds.RasterXSize + c_left + c_right)

    input_ds = None # Close the dataset so that we can move or overwrite it.

    # If there is no output_path, assume that we are going to be doing the operation in-place. BUT, if remove_temporary_files
    # is not True, simply move the input file to temp as a backup.
    if output_path is None:
        temp_path = hb.temp('.tif', 'displaced_' + hb.file_root(input_path), remove_temporary_files)
        hb.rename_with_overwrite(input_path, temp_path)
        output_path = input_path
        input_path = temp_path

    driver = gdal.GetDriverByName('GTiff')

    local_gtiff_creation_options = list(hb.DEFAULT_GTIFF_CREATION_OPTIONS)
    local_gtiff_creation_options.extend(['COMPRESS=DEFLATE'])

    n_bands = 1

    output_raster = driver.Create(output_path, n_cols, n_rows, n_bands, datatype, options=local_gtiff_creation_options)
    output_raster.SetProjection(input_projection)
    output_raster.SetGeoTransform(output_gt)

    output_band = output_raster.GetRasterBand(1)

    output_band.SetNoDataValue(fill_value) # NOTE, this has to happen before WriteArray or it will assume filling with 0.
    output_band.WriteArray(input_array, c_left, r_above)
    output_raster.FlushCache()
    output_raster = None


def fill_to_match_extent(input_path, match_path, output_path=None, fill_value=None, remove_temporary_files=False):

    # gdal.Translate()

    ds = gdal.OpenEx(input_path)
    input_gt = ds.GetGeoTransform()

    match_ds = gdal.OpenEx(match_path)
    match_gt = match_ds.GetGeoTransform()

    c_left = -1 * (match_gt[0] - input_gt[0]) * match_gt[1]
    r_above = (match_gt[3] - input_gt[3]) / match_gt[1]

    c_right = match_ds.RasterXSize - (c_left + ds.RasterXSize)
    r_below = match_ds.RasterYSize - (r_above + ds.RasterYSize)

    n_cols = ds.RasterXSize + c_left + c_right
    n_rows = ds.RasterYSize + r_above + r_below

    ds = None
    match_ds = None

    hb.add_rows_or_cols_to_geotiff(input_path, r_above, r_below, c_left, c_right, output_path=output_path, fill_value=fill_value, remove_temporary_files=remove_temporary_files)



def fill_to_match_extent_using_warp(input_path, match_path, output_path=None, fill_value=None, remove_temporary_files=False):
    # Slower it seems than fill_to_match_extent.
    match_ds = gdal.OpenEx(match_path)
    match_gt = match_ds.GetGeoTransform()
    match_srs = match_ds.GetProjection()
    match_gdal_win = hb.get_raster_info_hb(match_path)['gdal_win']

    if output_path is None:
        output_path = hb.temp('.tif', 'filled', False)

    width = match_ds.RasterXSize
    height = match_ds.RasterYSize
    callback = hb.make_logger_callback(
        "fill_to_match_extent %.1f%% complete %s")
    gdal.Warp(output_path, input_path, width=width, height=height, outputBounds=match_gdal_win,
              callback=callback, callback_data=[output_path])

def snap_bb_points_to_outer_pyramid(input_bb, pyramidal_raster_path):
    """
    Converts a BB to one that has points that preceisly correspond to the Pyramid definition given by Pyramidal_raster_path.
    :param input_bb:
    :param pyramidal_raster_path:
    :return:
    """
    # NOTE INTERESTING BEHAVIOR: exclusive works, centroid does not. it shifts everyone 1 to the right.
    # Is this a bahavior that happens with centroid and coords that precisely hit a pyramid cell edge?
    res = Decimal(determine_pyramid_resolution(pyramidal_raster_path))

    # Convert to decimal types
    input_bb = [Decimal(input_bb[0]), Decimal(input_bb[1]), Decimal(input_bb[2]), Decimal(input_bb[3])]

    snapped_bb = [Decimal(0.0), Decimal(0.0), Decimal(0.0), Decimal(0.0)]
    snapped_bb[0] = input_bb[0] - (Decimal(input_bb[0]) % res)
    snapped_bb[1] = input_bb[1] - (input_bb[1] % res)
    snapped_bb[2] = input_bb[2] + (res - input_bb[2] % res)
    snapped_bb[3] = input_bb[3] + (res - input_bb[3] % res)

    returned_bb = [float(i) for i in snapped_bb]
    return returned_bb


