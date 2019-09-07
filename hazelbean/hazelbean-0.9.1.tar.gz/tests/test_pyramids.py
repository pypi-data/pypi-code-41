from unittest import TestCase
import os, sys, time

# NOTE Awkward inclusion heere so that I don't have to run the test via a setup config each  time
sys.path.extend(['../..'])

import hazelbean as hb
import pandas as pd
import numpy as np

class DataStructuresTester(TestCase):
    def setUp(self):
        self.global_15m_floats_path = 'data/ag_30km_change.tif'
        self.global_1deg_raster_path = 'data/global_1deg_floats.tif'
        self.two_polygon_shapefile_path = 'data/two_poly_wgs84_aoi.shp'
        self.country_zones_path = r"optional_test_data\countries_wgs84_zone_ids.tif"
        self.global_15m_raster_path = r"optional_test_data\c3ann.tif"

    def tearDown(self):
        pass

    def test_load_geotiff_chunk_by_cr(self):

        hb.load_geotiff_chunk_by_cr_size(self.global_1deg_raster_path, (1, 2, 5, 5))

    def test_load_geotiff_chunk_by_bb(self):
        input_path = self.global_15m_floats_path
        left_lat = -40
        bottom_lon = -25
        lat_size = .2
        lon_size = 1
        bb = [left_lat,
              bottom_lon,
              left_lat + lat_size,
              bottom_lon + lon_size]
        hb.load_geotiff_chunk_by_bb(input_path, bb)

    def test_add_rows_or_cols_to_geotiff(self):
        incomplete_array = hb.load_geotiff_chunk_by_bb(self.global_1deg_raster_path, [-180, -80, 180, 70])
        temp_path = hb.temp('.tif', 'test_add_rows_or_cols_to_geotiff', True)
        geotransform_override = hb.get_raster_info(self.global_1deg_raster_path)['geotransform']
        geotransform_override = [-180, 1, 0, 80, 0, -1]
        n_rows_override = 150

        hb.save_array_as_geotiff(incomplete_array, temp_path, self.global_1deg_raster_path, geotransform_override=geotransform_override, n_rows_override=n_rows_override)
        r_above, r_below, c_above, c_below = 10, 20, 0, 0
        hb.add_rows_or_cols_to_geotiff(temp_path, r_above, r_below, c_above, c_below, remove_temporary_files=True)

    # def test_fill_ndv_to_match_extent(self):
    #
    #     incomplete_array = hb.load_geotiff_chunk_by_bb(self.global_1deg_raster_path, 80, -180, 150, 360)
    #     # TODO Here is an interesting starting point to assess the question of how to generalize AF as flex inputs. For now it is path based.
    #
    #     temp_path = hb.temp('.tif', 'test_add_rows_or_cols_to_geotiff', True)
    #     geotransform_override = hb.get_raster_info(self.global_1deg_raster_path)['geotransform']
    #     geotransform_override = [-180, 1, 0, 80, 0, -1]
    #     n_rows_override = 150
    #
    #     hb.save_array_as_geotiff(incomplete_array, temp_path, self.global_1deg_raster_path, geotransform_override=geotransform_override, n_rows_override=n_rows_override)
    #
    #     temp2_path = hb.temp('.tif', 'expand_to_bounding_box', True)
    #
    #     hb.fill_to_match_extent(temp_path, self.global_1deg_raster_path, None, temp2_path)


    def test_fill_to_match_extent(self):

        incomplete_array = hb.load_geotiff_chunk_by_bb(self.global_1deg_raster_path, [-180, -80, 180, 70])
        # TODO Here is an interesting starting point to assess the question of how to generalize AF as flex inputs. For now it is path based.

        temp_path = hb.temp('.tif', 'test_add_rows_or_cols_to_geotiff', True)
        geotransform_override = hb.get_raster_info(self.global_1deg_raster_path)['geotransform']
        geotransform_override = [-180, 1, 0, 80, 0, -1]
        n_rows_override = 150

        hb.save_array_as_geotiff(incomplete_array, temp_path, self.global_1deg_raster_path, geotransform_override=geotransform_override, n_rows_override=n_rows_override)

        temp2_path = hb.temp('.tif', 'expand_to_bounding_box', True)

        hb.fill_to_match_extent(temp_path, self.global_1deg_raster_path, temp2_path)



    def test_fill_to_match_extent_manual(self):

        incomplete_array = hb.load_geotiff_chunk_by_bb(self.global_1deg_raster_path, [-180, -80, 180, 70])
        # TODO Here is an interesting starting point to assess the question of how to generalize AF as flex inputs. For now it is path based.

        temp_path = hb.temp('.tif', 'test_add_rows_or_cols_to_geotiff', True)
        geotransform_override = hb.get_raster_info(self.global_1deg_raster_path)['geotransform']
        geotransform_override = [-180, 1, 0, 80, 0, -1]
        n_rows_override = 150

        hb.save_array_as_geotiff(incomplete_array, temp_path, self.global_1deg_raster_path, geotransform_override=geotransform_override, n_rows_override=n_rows_override)

        temp2_path = hb.temp('.tif', 'expand_to_bounding_box', True)

        hb.fill_to_match_extent(temp_path, self.global_1deg_raster_path, temp2_path)




    def test_make_path_global_pyramid(self):
        hb.make_path_global_pyramid(self.global_1deg_raster_path, verbose=False)