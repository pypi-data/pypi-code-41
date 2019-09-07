from unittest import TestCase
import os, sys, time

# NOTE Awkward inclusion heere so that I don't have to run the test via a setup config each  time
sys.path.extend(['../..'])

import hazelbean as hb
import pandas as pd
import numpy as np

class DataStructuresTester(TestCase):
    def setUp(self):
        self.global_5m_raster_path = 'data/ha_per_cell_5m.tif'
        self.global_1deg_raster_path = 'data/global_1deg_floats.tif'
        self.two_polygon_shapefile_path = 'data/two_poly_wgs84_aoi.shp'

        self.ag_30km_change_wgs84_path = 'optional_test_data/ag_30km_change.tif'
        self.countries_mollweide_path = 'optional_test_data/countries_mollweide.shp'
        self.countries_wgs84_path = 'optional_test_data/countries_wgs84.shp'

    def tearDown(self):
        pass

    def test_zonal_statistics_faster(self):
        hb.get_wkt_from_epsg_code(hb.common_epsg_codes_by_name['robinson'])

        hb.zonal_statistics_faster(self.global_5m_raster_path, self.two_polygon_shapefile_path)

        # Results in memory error because not matching projecitons/units
        hb.zonal_statistics_faster(self.ag_30km_change_wgs84_path, self.countries_mollweide_path)


        hb.zonal_statistics_faster(self.ag_30km_change_wgs84_path, self.countries_wgs84_path)
