# coding: utf-8

# In general Geoformat is licensed under an MIT/X style license with the
# following terms:
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# Authors :
#   Guilhain Averlant
#   Eliette Catelin
#   Quentin Lecuire
#   Charlotte Montesinos Chevalley
#   Coralie Rabiniaux

import copy
import os.path
# import json
import sys
import time
import zlib

from osgeo import ogr
from osgeo import osr


## OGR METADATA

####  Data Type
# OFSTBoolean = 1
# OFSTFloat32 = 3
# OFSTInt16 = 2
# OFSTNone = 0
# OFTBinary = 8
# OFTDate = 9
# OFTDateTime = 11
# OFTInteger = 0
# OFTInteger64 = 12
# OFTInteger64List = 13
# OFTIntegerList = 1
# OFTReal = 2
# OFTRealList = 3
# OFTString = 4
# OFTStringList = 5
# OFTTime = 10
# OFTWideString = 6
# OFTWideStringList = 7


#### Geometry Type
# wkb25Bit = -2147483648
# wkb25DBit = -2147483648
# wkbCircularString = 8
# wkbCircularStringM = 2008
# wkbCircularStringZ = 1008
# wkbCircularStringZM = 3008
# wkbCompoundCurve = 9
# wkbCompoundCurveM = 2009
# wkbCompoundCurveZ = 1009
# wkbCompoundCurveZM = 3009
# wkbCurve = 13
# wkbCurveM = 2013
# wkbCurvePolygon = 10
# wkbCurvePolygonM = 2010
# wkbCurvePolygonZ = 1010
# wkbCurvePolygonZM = 3010
# wkbCurveZ = 1013
# wkbCurveZM = 3013
# wkbGeometryCollection = 7
# wkbGeometryCollection25D = -2147483641
# wkbGeometryCollectionM = 2007
# wkbGeometryCollectionZM = 3007
# wkbLineString = 2
# wkbLineString25D = -2147483646
# wkbLineStringM = 2002
# wkbLineStringZM = 3002
# wkbLinearRing = 101
# wkbMultiCurve = 11
# wkbMultiCurveM = 2011
# wkbMultiCurveZ = 1011
# wkbMultiCurveZM = 3011
# wkbMultiLineString = 5
# wkbMultiLineString25D = -2147483643
# wkbMultiLineStringM = 2005
# wkbMultiLineStringZM = 3005
# wkbMultiPoint = 4
# wkbMultiPoint25D = -2147483644
# wkbMultiPointM = 2004
# wkbMultiPointZM = 3004
# wkbMultiPolygon = 6
# wkbMultiPolygon25D = -2147483642
# wkbMultiPolygonM = 2006
# wkbMultiPolygonZM = 3006
# wkbMultiSurface = 12
# wkbMultiSurfaceM = 2012
# wkbMultiSurfaceZ = 1012
# wkbMultiSurfaceZM = 3012
# wkbNDR = 1
# wkbNone = 100
# wkbPoint = 1
# wkbPoint25D = -2147483647
# wkbPointM = 2001
# wkbPointZM = 3001
# wkbPolygon = 3
# wkbPolygon25D = -2147483645
# wkbPolygonM = 2003
# wkbPolygonZM = 3003
# wkbPolyhedralSurface = 15
# wkbPolyhedralSurfaceM = 2015
# wkbPolyhedralSurfaceZ = 1015
# wkbPolyhedralSurfaceZM = 3015
# wkbSurface = 14
# wkbSurfaceM = 2014
# wkbSurfaceZ = 1014
# wkbSurfaceZM = 3014
# wkbTIN = 16
# wkbTINM = 2016
# wkbTINZ = 1016
# wkbTINZM = 3016
# wkbTriangle = 17
# wkbTriangleM = 2017
# wkbTriangleZ = 1017
# wkbTriangleZM = 3017
# wkbUnknown = 0
# wkbXDR = 0


def version():
    return 'Alpha version 20190904'


##############
#
# DATA PRINTING
#
##############
def print_line(field_name_list, max_len_value_list, separator='|'):
    line = separator + separator.join([(' ' * (len_value + 2))[:1] + str(field_name_list[i_field]) + (' ' * (
            len_value + 2))[len(str(field_name_list[i_field])) + 1:] for i_field, len_value in
                                       enumerate(max_len_value_list)]) + separator

    return line


def print_header_separator(max_len_value_list, table_type='RST'):
    if table_type == 'RST':
        separator = '+'
        header = '='


    elif table_type == 'MD':
        separator = '|'
        header = '-'
    else:
        print('error table type valye {} not valid')

    combi = header + separator + header

    return separator + header + combi.join(
        [header * len_value for len_value in max_len_value_list]) + header + separator


def print_line_separator(max_len_value_list):
    return '+-' + '-+-'.join(['-' * len_value for len_value in max_len_value_list]) + '-+'


def print_features_data_table(geolayer, field_name_list=None, print_i_feat=True, table_type='RST', light=True,
                              display_geo_data=False, max_len_coordinates=30):
    if not field_name_list:
        # create field name
        field_name_list = [None] * len(geolayer['metadata']['fields'])
        for i_field, field_name in enumerate(geolayer['metadata']['fields']):
            idx_field = geolayer['metadata']['fields'][field_name]['index']
            field_name_list[idx_field] = field_name

    max_len_value_list = [len(field_name) for field_name in field_name_list]

    if print_i_feat:
        key_max_len = len('i_feat')

    if display_geo_data:
        max_len_value_list += [len('type'), len('coordinates')]

    for i_feat in geolayer['features']:
        len_value_list = [len(str(geolayer['features'][i_feat]['attributes'][field_name])) for field_name in
                          field_name_list]

        if display_geo_data:
            len_coordinates = len(str(geolayer['features'][i_feat]['geometry']['coordinates']))
            if max_len_coordinates:
                if len_coordinates > max_len_coordinates:
                    len_coordinates = max_len_coordinates

            len_value_list += [len(str(geolayer['features'][i_feat]['geometry']['type'])), len_coordinates]

        # compute len data_value
        for i_len_value, len_value in enumerate(len_value_list):
            if len_value > max_len_value_list[i_len_value]:
                max_len_value_list[i_len_value] = len_value

            # compute key len
            if print_i_feat:
                if len(str(i_feat)) > key_max_len:
                    key_max_len = len(str(i_feat))

    if print_i_feat:
        # add key_field_name to field_name_list
        max_len_value_list = [key_max_len] + max_len_value_list
        # add max key len to key len value list
        complete_field_name_list = ['i_feat'] + field_name_list
    else:
        complete_field_name_list = field_name_list

    # add field type and coordinates at the end
    if display_geo_data:
        complete_field_name_list = complete_field_name_list + ['type', 'coordinates']

    if table_type == 'RST':
        yield print_line_separator(max_len_value_list)

    yield print_line(complete_field_name_list, max_len_value_list)
    yield print_header_separator(max_len_value_list, table_type=table_type)

    for i_feat in geolayer['features']:

        field_value_list = [geolayer['features'][i_feat]['attributes'][field_name] for field_name in field_name_list]

        if print_i_feat:
            field_value_list = [i_feat] + field_value_list

        if display_geo_data:
            geometry_type = geolayer['features'][i_feat]['geometry']['type']
            field_value_list += [geometry_type]

            if geometry_type == 'GeometryCollection':
                coordinates_value = str(geolayer['features'][i_feat]['geometry']['geometries'])
            else:
                coordinates_value = str(geolayer['features'][i_feat]['geometry']['coordinates'])

            if max_len_coordinates:
                coordinates_value = coordinates_value[:max_len_coordinates]

                if len(coordinates_value) == max_len_coordinates:
                    if geometry_type.upper() in ['POINT', 'GEOMETRYCOLLECTION']:  # ['Point', 'GeometryCollection']
                        coordinates_value = coordinates_value[:-5] + ' ...]'
                    elif geometry_type.upper() in ['LINESTRING', 'MULTIPOINT']:  # ['LineString', 'MultiPoint']
                        coordinates_value = coordinates_value[:-6] + ' ...]]'
                    elif geometry_type.upper() in ['POLYGON', 'MULTILINESTRING']:  # ['Polygon', 'MultiLineString']
                        coordinates_value = coordinates_value[:-7] + ' ...]]]'
                    elif geometry_type.upper() in ['MULTIPOLYGON']:  # ['MultiPolygon']
                        coordinates_value = coordinates_value[:-8] + ' ...]]]]'

            field_value_list += [coordinates_value]

        yield print_line(field_value_list, max_len_value_list)

        if table_type == 'RST':
            if light is False:
                yield print_line_separator(max_len_value_list)

    if table_type == 'RST':
        yield print_line_separator(max_len_value_list)


def print_metadata_field_table(geolayer, field_name_list=None, key_field_name='name', order_value=True,
                               table_type='RST', light=True):
    """
    Return a generator
    :param geolayer:
    :param field_name_list:
    :param key_field_name:
    :param order_value:
    :return:
    """

    dict_data = geolayer['metadata']['fields']
    if not field_name_list:
        # field_name_list = dict_data.items()[0][1].keys()
        key_0 = list(dict_data.keys())[0]
        field_name_list = list(dict_data[key_0].keys())

    max_len_value_list = [len(str(field_name)) for field_name in field_name_list]

    # create a calling list who is
    call_feature_order = list(dict_data.keys())

    # compute max len for data_value
    key_max_len = 0
    for i_field, key in enumerate(dict_data):
        len_value_list = [len(str(dict_data[key][field_name])) for field_name in field_name_list]
        # compute len data_value
        for i_len_value, len_value in enumerate(len_value_list):
            if len_value > max_len_value_list[i_len_value]:
                max_len_value_list[i_len_value] = len_value
        # compute key len
        if len(str(key)) > key_max_len:
            key_max_len = len(str(key))

        if order_value:
            idx = dict_data[key]['index']
            call_feature_order[idx] = key

    # add max key len to key len value list
    max_len_value_list = [key_max_len] + max_len_value_list

    # add key_field_name to field_name_list
    complete_field_name_list = [key_field_name] + field_name_list

    # create line separator
    # line_separator = '+-'+'-+-'.join(['-' * len_value for len_value in max_len_value_list])+'-+'
    line_separator = print_line_separator(max_len_value_list)

    # create fields name line
    line_field_name = print_line(complete_field_name_list, max_len_value_list)

    # generate table to print
    if table_type == 'RST':
        yield line_separator
    yield line_field_name
    yield print_header_separator(max_len_value_list, table_type=table_type)

    # for i_field, key in enumerate(dict_data):
    for i_feat in call_feature_order:
        field_value_list = [i_feat] + [dict_data[i_feat][field_name] for field_name in field_name_list]
        yield print_line(field_value_list, max_len_value_list)
        if not light:
            yield line_separator

    if table_type == 'RST':
        yield print_line_separator(max_len_value_list)


####
#
# CLAUSE
#
# The CLAUSE functions return a directly a list of i_feat or a dict with a list associates to each key of i_feat
###

def clause_where(geolayer, field_name, predicate, values):
    # transform values to iterate variable
    if not isinstance(values, (list, tuple)):
        if isinstance(values, tuple):
            values = list(values)
        else:
            values = [values]
    # init result list
    i_feat_list = []
    # loop on geolayer
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]
        feature_value = feature['attributes'][field_name]

        # save feature_value in list by default
        if isinstance(feature_value, (list, tuple, set)):
            feature_value_list = feature_value
        else:
            feature_value_list = [feature_value]

        save_i_feat = False
        # loop on feature_value_list
        for feature_value in feature_value_list:
            if '=' in predicate or 'IN' in predicate or predicate == 'LIKE' or predicate == 'BETWEEN':
                if feature_value in values:
                    save_i_feat = True
                    break

            if predicate in '<>' or predicate == 'BETWEEN':
                if predicate == '<>':
                    if feature_value not in values:
                        save_i_feat = True
                else:
                    if (predicate == '>' or predicate == 'BETWEEN') and feature_value > values[0]:
                        save_i_feat = True
                    if (predicate == '<' or predicate == 'BETWEEN') and feature_value < values[-1]:
                        save_i_feat = True

            if 'IS' in predicate:
                if 'NOT' in predicate:
                    if feature_value:
                        save_i_feat = True
                else:
                    if not feature_value:
                        save_i_feat = True

        if save_i_feat:
            i_feat_list.append(i_feat)

    return i_feat_list


def clause_where_combination(geolayer, clause_where_dict):
    """

    example for claus_where_dict :
           claus_where_dict= {'field_predicate': {
                                    'foo_field_name': {
                                        'predicate': '=',
                                        'values': [0, 1, 2]
                                    }
                                }
                            }


    :param geolayer:
    :param clause_where_dict:
    :param field_combination:
    :return:
    """

    def field_predicate(geolayer, field_predicate_dict, field_combination=None):

        i_feat_predicate = {}
        for field_name in field_predicate_dict['field_predicate']:
            field_predicate = field_predicate_dict['field_predicate'][field_name]
            predicate = field_predicate['predicate'].upper()
            if 'values' in field_predicate.keys():
                values = field_predicate['values']
                if not isinstance(values, (list, tuple)):
                    if isinstance(values, tuple):
                        values = list(values)
                    else:
                        values = [field_predicate['values']]

            i_feat_list = []

            for i_feat in geolayer['features']:
                feature = geolayer['features'][i_feat]
                feature_value = feature['attributes'][field_name]

                # save feature_value in list by default
                if isinstance(feature_value, (list, tuple, set)):
                    feature_value_list = feature_value
                else:
                    feature_value_list = [feature_value]

                save_i_feat = False
                # loop on feature_value_list
                for feature_value in feature_value_list:
                    if '=' in predicate or 'IN' in predicate or predicate == 'LIKE' or predicate == 'BETWEEN':
                        if feature_value in values:
                            save_i_feat = True
                            break

                    if predicate in '<>' or predicate == 'BETWEEN':
                        if predicate == '<>':
                            if feature_value not in values:
                                save_i_feat = True
                        else:
                            if (predicate == '>' or predicate == 'BETWEEN') and feature_value > values[0]:
                                save_i_feat = True
                            if (predicate == '<' or predicate == 'BETWEEN') and feature_value < values[-1]:
                                save_i_feat = True

                    if 'IS' in predicate:
                        if 'NOT' in predicate:
                            if feature_value:
                                save_i_feat = True
                        else:
                            if not feature_value:
                                save_i_feat = True

                if save_i_feat:
                    i_feat_list.append(i_feat)

            # save i_feat
            i_feat_predicate[field_name] = i_feat_list

        if field_combination:
            final_i_feat_set = set([])
            for field_name in i_feat_predicate:
                field_name_i_feat_set = set(i_feat_predicate[field_name])
                if field_combination == 'OR':
                    final_i_feat_set.update(field_name_i_feat_set)
                if field_combination == 'AND':
                    if len(final_i_feat_set) == 0:
                        final_i_feat_set = field_name_i_feat_set
                    else:
                        final_i_feat_set.intersection_update(field_name_i_feat_set)

            final_i_feat_list = list(final_i_feat_set)
            return final_i_feat_list
        else:
            return i_feat_list

    if 'field_combination' in clause_where_dict.keys():
        if isinstance(clause_where_dict['field_combination'], str):
            field_combination = clause_where_dict['field_combination']
            i_feat_list = field_predicate(geolayer, clause_where_dict, field_combination)

    # just field_predicate in  clause_where_dict
    else:
        i_feat_list = field_predicate(geolayer, clause_where_dict)

    return i_feat_list


def clause_group_by(geolayer, field_name_list):
    """
    Return a dictionnary with field name list as key and i_feat list from geolayer
    """

    if isinstance(field_name_list, str):
        field_name_list = [field_name_list]

    result_dico = {}
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        field_value_tuple = tuple(
            [feature['attributes'][field_name] if field_name in feature['attributes'] else None for field_name in
             field_name_list])

        # convert list value to tuple (if exists) very rare
        field_value_tuple = tuple([tuple(value) if isinstance(value, list) else value for value in field_value_tuple])

        if field_value_tuple in result_dico:
            result_dico[field_value_tuple].append(i_feat)
        else:
            result_dico[field_value_tuple] = [i_feat]

    return result_dico


def clause_order_by(geolayer, field_name, field_order='ASC'):
    """


    :param geolayer:
    :param field_name:
    :param order:
    :return:

    https://docs.python.org/fr/3/howto/sorting.html
    http://sametmax.com/ordonner-en-python/
    """

    dico_i_feat_value = {}
    for i_feat in geolayer['features']:
        feature_value = [geolayer['features'][i_feat]['attributes'][field_name]]
        dico_i_feat_value[i_feat] = [feature_value]

    tuple_value = tuple([tuple(value) for value in tuple(
        [[i_feat] + [value for value in dico_i_feat_value[i_feat]] for i_feat in dico_i_feat_value])])

    if field_order == 'ASC':
        order_values = sorted(tuple_value, key=lambda data: data[1])
    else:
        order_values = sorted(tuple_value, key=lambda data: data[1], reverse=True)

    i_feat_list = [order[0] for order in order_values]

    return i_feat_list


####
#
# TOOLS
#
###
def sql(path, sql_request):
    data_source = ogr.Open(path)
    return data_source.ExecuteSQL(sql_request)


def field_statistics(geolayer, statistic_field):
    """

    INPUT / OUTPUT field type table :

        SUM : if original field type is real or integer   | output original field type
        MEAN : if original field type is real or integer  | output real
        MIN : if original field type is real or integer   | output original field type
        MAX : if original field type is real or integer   | output original field type
        RANGE : if original field type is real or integer | output original field type
        STD : if original field type is real or integer   | output real
        COUNT :  original field type doesn't matter       | output integer
        FIRST : original field type doesn't matter        | output original field type
        LAST : original field type doesn't matter         | output original field type
    """

    statistic_result = [0] * len(statistic_field)
    field_name_list = [0] * len(statistic_field)

    for fid, i_feat in enumerate(geolayer['features']):
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        for i, (field_name, statistic_type) in enumerate(statistic_field):
            # numeric computation on numeric field only
            if geolayer['metadata']['fields'][field_name]['type'] in set([0, 1, 2, 3, 10, 11, 12, 13]):
                if statistic_type.upper() == 'SUM':
                    statistic_result[i] += feature['attributes'][field_name]
                elif statistic_type.upper() == 'MEAN':
                    if fid == 0:
                        statistic_result[i] = feature['attributes'][field_name]
                    else:
                        statistic_result[i] = (statistic_result[i] * fid + feature['attributes'][field_name]) / (
                                fid + 1)
                elif statistic_type.upper() == 'MIN':
                    if fid == 0:
                        statistic_result[i] = feature['attributes'][field_name]
                    statistic_result[i] = min(statistic_result[i], feature['attributes'][field_name])
                elif statistic_type.upper() == 'MAX':
                    if fid == 0:
                        statistic_result[i] = feature['attributes'][field_name]
                    statistic_result[i] = max(statistic_result[i], feature['attributes'][field_name])
                elif statistic_type.upper() == 'RANGE':
                    if fid == 0:
                        save_min = feature['attributes'][field_name]
                        save_max = feature['attributes'][field_name]
                    save_min = min(save_min, feature['attributes'][field_name])
                    save_max = max(save_max, feature['attributes'][field_name])
                    statistic_result[i] = save_max - save_min
                elif statistic_type.upper() == 'STD':
                    if fid == 0:
                        statistic_result[i] = 0
                        mean_value = feature['attributes'][field_name]
                        save_value = [0] * len(geolayer['features'])
                        save_value[0] = feature['attributes'][field_name]
                    else:
                        save_value[fid] = feature['attributes'][field_name]
                        mean_value = (mean_value * fid + feature['attributes'][field_name]) / (fid + 1)
                    # if last iteration
                    if fid == len(geolayer['features']) - 1:
                        mean_deviation = [(value - mean_value) ** 2 for value in save_value]
                        std_value = (sum(mean_deviation) / len(save_value)) ** 0.5
                        statistic_result[i] = std_value

            # for all field type
            if statistic_type.upper() == 'COUNT':
                statistic_result[i] += 1
            elif statistic_type.upper() == 'FIRST':
                if fid == 0:
                    statistic_result[i] = feature['attributes'][field_name]
            elif statistic_type.upper() == 'LAST':
                statistic_result[i] = feature['attributes'][field_name]

            # formatage des résultats
            field_name_list[i] = statistic_field[i][1] + '_' + statistic_field[i][0]  # [:10]

    statistic_result = {field_name_list[i]: result for i, result in enumerate(statistic_result)}

    return statistic_result


def ogr_geom_type_to_geoformat_geom_type(ogr_geom_type):
    """

    """
    if ogr_geom_type == -2147483647:
        return 'Point25D'
    if ogr_geom_type == -2147483646:
        return 'LineString25D'
    if ogr_geom_type == -2147483645:
        return 'Polygon25D'
    if ogr_geom_type == -2147483644:
        return 'MultiPoint25D'
    if ogr_geom_type == -2147483643:
        return 'MultiLineString25D'
    if ogr_geom_type == -2147483642:
        return 'MultiPolygon25D'
    if ogr_geom_type == 0:
        return 'Geometry'
    if ogr_geom_type == 1:
        return 'Point'
    if ogr_geom_type == 2:
        return 'LineString'
    if ogr_geom_type == 3:
        return 'Polygon'
    if ogr_geom_type == 4:
        return 'MultiPoint'
    if ogr_geom_type == 5:
        return 'MultiLineString'
    if ogr_geom_type == 6:
        return 'MultiPolygon'
    if ogr_geom_type == 7:
        return 'GeometryCollection'
    if ogr_geom_type == 100:
        return 'No Geometry'


def geoformat_geom_type_to_ogr_geom_type(geoformat_geom_type):
    if geoformat_geom_type.upper() == 'POINT25D':  # Point25D
        return -2147483647
    if geoformat_geom_type.upper() == 'LINESTRING25D':  # LineString25D
        return -2147483646
    if geoformat_geom_type.upper() == 'PLYGON25D':  # Polygon25D
        return -2147483645
    if geoformat_geom_type.upper() == 'MULTIPOINT25D':  # MultiPoint25D
        return -2147483644
    if geoformat_geom_type.upper() == 'MULTILINESTRING25D':  # MultiLineString25D
        return -2147483643
    if geoformat_geom_type.upper() == 'MULTIPOLYGON25D':  # MultiPolygon25D
        return -2147483642
    if geoformat_geom_type.upper() == 'GEOMETRY':  # Geometry
        return 0
    if geoformat_geom_type.upper() == 'POINT':  # Point
        return 1
    if geoformat_geom_type.upper() == 'LINESTRING':  # LineString
        return 2
    if geoformat_geom_type.upper() == 'POLYGON':  # Polygon
        return 3
    if geoformat_geom_type.upper() == 'MULTIPOINT':  # MultiPoint
        return 4
    if geoformat_geom_type.upper() == 'MULTILINESTRING':  # MultiLineString
        return 5
    if geoformat_geom_type.upper() == 'MULTIPOLYGON':  # MultiPolygon
        return 6
    if geoformat_geom_type.upper() == 'GEOMETRYCOLLECTION':  # GeometryCollection
        return 7
    if geoformat_geom_type.upper() == 'NO GEOMETRY':  # No Geometry
        return 100


def multi_geom_to_single_geom(geometry):
    """
    Iterator in given geometry and send single geometry (point, linestring, polygon) if geometry is a multigeometry.
    Works with GeometryCollection
    """

    if geometry['type'].upper() == 'GEOMETRYCOLLECTION':  # 'GeometryCollection'
        for inside_geometry in geometry['geometries']:
            for single_geom in multi_geom_to_single_geom(inside_geometry):
                yield single_geom

    elif geometry['type'].upper() in ['MULTIPOINT', 'MULTILINESTRING',
                                      'MULTIPOLGYON']:  # ['MultiPoint', 'MultiLineString', 'MultiPolygon']
        if geometry['type'].upper() == 'MULTIPOINT':  # 'MultiPoint'
            single_geometry_type = 'POINT'  # Point
        elif geometry['type'].upper() == 'MULTILINESTRING':  # 'MultiLineString'
            single_geometry_type = 'LINESTRING'  # 'LineString'
        else:
            single_geometry_type = 'POLYGON'  # 'Polygon'

        multi_coordinates = geometry['coordinates']
        for coordinates in multi_coordinates:
            yield {'type': single_geometry_type, 'coordinates': coordinates}

    else:
        yield geometry


def verify_geom_compatibility(driver_name, metadata_geometry_type):
    """

    OGR Geometry Type List :
        -2147483647: 'Point25D'
        -2147483646: 'LineString25D'
        -2147483645: 'Polygon25D'
        -2147483644: 'MultiPoint25D'
        -2147483643: 'MultiLineString25D'
        -2147483642: 'MultiPolygon25D'
                  0: 'Geometry'
                  1: 'Point'
                  2: 'LineString'
                  3: 'Polygon'
                  4: 'MultiPoint'
                  5: 'MultiLineString'
                  6: 'MultiPolygon'
                  7: 'GeometryCollection'
                100: 'No Geometry'

    [[0],[1], [2, 5], [3, 6], [4], [100]],  # 'Esri Shapefile'
    [[1, 4], [2, 5], [3, 6], [100]],  # TAB 'Mapinfo File'
    [[1, 4], [2, 5], [3, 6], [100]],  # MIF/MID 'Mapinfo File'
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # KML
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # GML
    [[0, 1, 2, 3, 4, 5, 6, 7, 100]],  # GeoJSON
    [[1], [2], [3, 6], [4], [5], [100]],  # Geoconcept
    [[1], [2, 5], [3, 6], [4], [100]],  # FileGDB
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # SQLite
    [[1, 2, 3, 4, 5, 6, 7, 100]],  # POSTGRESQL
    [[1, 2, 3, 4, 5, 6, 7, 100]]   # CSV
    ],

    """

    if isinstance(metadata_geometry_type, str):
        metadata_geometry_type = [metadata_geometry_type]

    set_geometry_type = set(metadata_geometry_type)

    if driver_name.upper() == 'ESRI SHAPEFILE':
        # POLYGON
        set_polygon = set(['No Geometry', 'Polygon', 'MultiPolygon'])
        if len(metadata_geometry_type) <= 3 and len(set_geometry_type.difference(set_polygon)) == 0:
            return 3
        # LINESTRING
        set_linestring = set(['No Geometry', 'LineString', 'MultiLineString'])
        if len(metadata_geometry_type) <= 3 and len(set_geometry_type.difference(set_linestring)) == 0:
            return 2
        # POINT
        set_point = set(['No Geometry', 'Point', 'MultiPoint'])
        if len(metadata_geometry_type) <= 3 and len(set_geometry_type.difference(set_point)) == 0:
            return 1

    if driver_name.upper() == 'POSTGRESQL':
        if len(set_geometry_type) > 1:
            return 0
        else:
            return geoformat_geom_type_to_ogr_geom_type(metadata_geometry_type[0])

    if driver_name.upper() == 'GEOJSON':
        return 0


def multi_to_single_geom(geometry, bbox=True):
    """
        This function explode a given multi part geometry to single part geometry
    """

    # if geometry collection
    if geometry['type'].upper() == 'GEOMETRYCOLLECTION':  # 'GeometryCollection'
        for under_geom in geometry['geometries']:
            for under_geom_in_under_geom in multi_to_single_geom(under_geom, bbox=bbox):
                yield under_geom_in_under_geom
    # for others geometries
    else:
        # if multipart geometry
        if geometry['type'].upper() in ['MULTIPOINT', 'MULTILINESTRING',
                                        'MULTIPOLYGON']:  # ['MultiPoint', 'MultiLineString', 'MultiPolygon']
            if geometry['type'].upper() == 'MULTIPOINT':  # 'MultiPoint'
                new_geometry = {'type': 'Point'}
            elif geometry['type'].upper() == 'MULTILINESTRING':  # 'MultiLineString'
                new_geometry = {'type': 'LineString'}
            elif geometry['type'].upper() == 'MULTIPOLYGON':  # 'MultiPolygon'
                new_geometry = {'type': 'Polygon'}

            coordinates = geometry['coordinates']
            for under_geom in coordinates:
                return_geometry = dict(new_geometry)
                return_geometry['coordinates'] = under_geom
                if bbox:
                    return_geometry['bbox'] = coordinates_to_bbox(under_geom)
                yield return_geometry

        # if yet single geometry
        else:
            yield geometry


def multi_to_single_geom_layer(geolayer):
    # creation de l'output en copiant les metadata de l'input
    geolayer_out = copy.deepcopy(geolayer)

    del geolayer_out['features']
    if geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTIPOINT':  # 'MultiPoint'
        geolayer_out['metadata']['geometry_ref']['type'] = 'Point'
    elif geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTILINESTRING':  # 'MultiLineString'
        geolayer_out['metadata']['geometry_ref']['type'] = 'LineString'
    elif geolayer['metadata']['geometry_ref']['type'].upper() == 'MULTIPOLYGON':  # 'MultiPolygon'
        geolayer_out['metadata']['geometry_ref']['type'] = 'Polygon'

    # boucle et transformation des géométries multi part en single part
    new_i_feat = 0
    geolayer_out['features'] = {}
    for i_feat in geolayer['features']:

        feature = geolayer['features'][i_feat]
        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        geometry = feature['geometry']
        for new_geometry in multi_to_single_geom(geometry):
            new_feature = {'attributes': feature['attributes'],
                           'geometry': new_geometry}

            # if feature is serialized
            if 'feature_serialize' in geolayer['metadata']:
                if geolayer['metadata']['feature_serialize']:
                    new_feature = str(new_feature)

            geolayer_out['features'][new_i_feat] = new_feature
            new_i_feat += 1

    return geolayer_out


def merge_geometries(geom_a, geom_b, bbox=True):
    """
    geom_a
    geom_b
    bbox = True (default) + 5 % time


    Return a merging geometry result of adding two differents geometries
    !! Carfull this function does not "union" two geometry but merge two geometry !!

    Merging Table :

        Single AND Single
            Point + Point = MultiPoint
            LineString + LineString = MultiLineString
            Polygon + Polygon = MultiPolygon

        Single AND Multi
            Point + MultiPoint = MultiPoint
            LineString  + MultiLineString = MultiLineString
            Polygon + MultiPolygon = MultiPolygon

        Mixed Geometries Types and GeometryCollection
            Point + Polygon = GeometryCollection(Point, Polygon)
            GeometryCollection(Polygon + LineString) + LineSting = GeometryCollection(Polygon + MultiLineString)
            GeometryCollection(MultiPolygon, LineString), GeometryCollection(MultiPoint, LineString)
                = GeometryCollection(MultiPolygon, MultiLineString, MultiPoint)



    How does it works ?

        - first if geometry categories are the same

        - if geometry categories are differents or GeometryCollection
            We will have a GeometryCollection

    """
    new_geom = {}

    # if same geometry category (Point, MultiPoint), (LineString, MultiLineString), (Polygon, MultiPolygon)
    if geom_a['type'].replace('Multi', '') == geom_b['type'].replace('Multi', '') and geom_a[
        'type'] != 'GeometryCollection' and geom_b['type'] != 'GeometryCollection':
        new_geom['type'] = str(geom_a['type'])
        new_geom['coordinates'] = list(geom_a['coordinates'])

        if 'Multi' in new_geom['type']:
            if 'Multi' in geom_b['type']:
                for geom_coordinates in geom_b['coordinates']:
                    new_geom['coordinates'].append(geom_coordinates)
            else:
                new_geom['coordinates'].append(geom_b['coordinates'])

        else:
            new_geom['type'] = 'Multi' + new_geom['type']
            if 'Multi' in geom_b['type']:
                geom = [new_geom['coordinates']]
                for geom_coordinates in geom_b['coordinates']:
                    geom.append(geom_coordinates)
                new_geom['coordinates'] = geom
            else:
                new_geom['coordinates'] = [new_geom['coordinates'], geom_b['coordinates']]
    else:
        # new_geom['type'] = 'GeometryCollection'
        if geom_a['type'] == 'GeometryCollection' and geom_b['type'] == 'GeometryCollection':
            # first loop on geom_a geometries
            for i_a, geojson_geometrie_a in enumerate(geom_a['geometries']):
                if i_a == 0:
                    new_geom = geojson_geometrie_a
                else:

                    new_geom = merge_geometries(new_geom, geojson_geometrie_a, bbox=bbox)

            # add geom_ b geometries
            for geojson_geometrie_b in geom_b['geometries']:
                new_geom = merge_geometries(new_geom, geojson_geometrie_b, bbox=bbox)


        elif geom_a['type'] == 'GeometryCollection' or geom_b['type'] == 'GeometryCollection':
            if geom_a['type'] == 'GeometryCollection':
                ori_geom_collect = dict(geom_a)
                ori_geom_simple = dict(geom_b)
            else:
                ori_geom_collect = dict(geom_b)
                ori_geom_simple = dict(geom_a)

            # first loop on ori_geom_collect geometries
            for i_a, geojson_geometrie_a in enumerate(ori_geom_collect['geometries']):
                if i_a == 0:
                    new_geom = geojson_geometrie_a
                else:
                    new_geom = merge_geometries(new_geom, geojson_geometrie_a, bbox=bbox)

            added_geom = False
            # then we see if ori_geom_simple as similar geom type in ori_geom_collect else we had
            for i_geom, geojson_geom in enumerate(new_geom['geometries']):
                if geojson_geom['type'].replace('Multi', '') == ori_geom_simple['type'].replace('Multi', ''):
                    replace_geom = merge_geometries(geojson_geom, ori_geom_simple)
                    new_geom['geometries'][i_geom] = replace_geom
                    added_geom = True
                    # end loop
                    break

            if not added_geom:
                # if not break we had ori_geom_simple to new_geom GEOMETRYCOLLECTION
                new_geom['geometries'] = new_geom['geometries'] + [dict(ori_geom_simple)]

        else:
            new_geom['type'] = 'GeometryCollection'
            new_geom['geometries'] = [dict(geom_a), dict(geom_b)]

    # recompute bbox
    if bbox:
        if new_geom['type'] == 'GeometryCollection':
            for i_geom, geom in enumerate(new_geom['geometries']):
                geom_bbox = coordinates_to_bbox(geom['coordinates'])
                new_geom['geometries'][i_geom]['bbox'] = geom_bbox
                if i_geom == 0:
                    geom_coll_extent = geom_bbox
                else:
                    geom_coll_extent = bbox_union(geom_coll_extent, geom_bbox)

            new_geom['bbox'] = geom_coll_extent

        else:
            new_geom['bbox'] = coordinates_to_bbox(new_geom['coordinates'])
    else:
        if 'bbox' in new_geom:
            del new_geom['bbox']

        if new_geom['type'] == 'GeometryCollection':

            for i_geom, geom in enumerate(new_geom['geometries']):
                if 'bbox' in geom:
                    del new_geom['geometries'][i_geom]['bbox']

    return new_geom


def reproject_geometry(geometry, in_crs, out_crs):
    ogr_geometry = geojson_to_ogr_geom(geometry)

    # Assign spatial ref
    ## Input
    if isinstance(in_crs, int):
        in_proj = osr.SpatialReference()
        in_proj.ImportFromEPSG(in_crs)
    elif isinstance(in_crs, str):
        in_proj = osr.SpatialReference(in_crs)
    else:
        print('crs value must be a ESPG code or a  OGC WKT projection')

    ## Output
    if isinstance(out_crs, int):
        out_proj = osr.SpatialReference()
        out_proj.ImportFromEPSG(out_crs)
    elif isinstance(out_crs, str):
        out_proj = osr.SpatialReference(out_crs)
    else:
        print('crs value must be a ESPG code or a  OGC WKT projection')

    ogr_geometry.AssignSpatialReference(in_proj)
    ogr_geometry.TransformTo(out_proj)

    geometry = ogr_geom_to_geojson(ogr_geometry)

    return geometry


def reproject_geolayer(geolayer, out_crs, in_crs=None):
    if not in_crs:
        in_crs = geolayer['metadata']['geometry_ref']['crs']

    # change metadata
    geolayer['metadata']['geometry_ref']['crs'] = out_crs

    # reproject geometry
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if geometry in feature
        if 'geometry' in feature.keys():
            feature_geometry = feature['geometry']
            new_geometry = reproject_geometry(feature_geometry, in_crs, out_crs)
            # assign new geometry
            feature['geometry'] = new_geometry

    return geolayer


def extent_bbox(bbox, extent):
    (x_min, y_min, x_max, y_max) = bbox
    x_min = x_min - extent
    y_min = y_min - extent
    x_max = x_max + extent
    y_max = y_max + extent

    return x_min, y_min, x_max, y_max


def bbox_union(bbox_a, bbox_b):
    """ realize union between to given bbox"""
    (x_min_a, y_min_a, x_max_a, y_max_a) = bbox_a
    (x_min_b, y_min_b, x_max_b, y_max_b) = bbox_b

    return min(x_min_a, x_min_b), min(y_min_a, y_min_b), max(x_max_a, x_max_b), max(y_max_a, y_max_b)


def bbox_to_polygon_coordinates(bbox):
    """
    This function send polygon coordinates from a give bbox
    :param bbox:
    :return:
    """
    (x_min, y_min, x_max, y_max) = bbox

    return [[(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min), (x_min, y_min)]]


def union_by_split(geometry_list, split_factor=2):
    """
    Union geometry list with split list method (split_factor default 2 by 2)
    * OGR dependencie : Union *
    """

    len_list = len(geometry_list)
    if len_list > split_factor:
        union_geom_list = []
        for i in range(split_factor):
            # first iteration
            if i == 0:
                split_geometry_list = geometry_list[:int(len_list / split_factor)]
            # last iteration
            elif i == split_factor - 1:
                begin = int(len_list / split_factor) * i
                split_geometry_list = geometry_list[begin:]
            # others iterations
            else:
                begin = int(len_list / split_factor) * i
                end = (int(len_list / split_factor)) * (i + 1)
                split_geometry_list = geometry_list[begin:end]

            # adding union to geom list
            union_geom_list.append(union_by_split(split_geometry_list, split_factor))

        for i, union_geom in enumerate(union_geom_list):
            if i == 0:
                ogr_geom_unioned = geojson_to_ogr_geom(union_geom)
            else:
                temp_geom = geojson_to_ogr_geom(union_geom)
                ogr_geom_unioned = ogr_geom_unioned.Union(temp_geom)

        geojson_unioned = ogr_geom_to_geojson(ogr_geom_unioned)

        return geojson_unioned

    else:
        if len(geometry_list) > 1:

            for i, union_geom in enumerate(geometry_list):
                if i == 0:
                    ogr_geom_unioned = geojson_to_ogr_geom(union_geom)
                else:
                    temp_geom = geojson_to_ogr_geom(union_geom)
                    ogr_geom_unioned = ogr_geom_unioned.Union(temp_geom)

            geojson_unioned = ogr_geom_to_geojson(ogr_geom_unioned)

            return geojson_unioned

        else:
            return geometry_list[0]


def bbox_intersects_bbox(bbox_a, bbox_b):
    """
    This function return a Truth Value Testing (True False) that qualifies the rectangle intersection


    True : bbox intersects
    False : bbox doesn't intersects

    The algorithm is inspired from : http://stackoverflow.com/questions/13390333/two-rectangles-intersection
                                    IA  : https://web.archive.org/web/*/http://stackoverflow.com/questions/13390333/two-rectangles-intersection

        Input :
            bbox_a : first boundary box
            bbox_b : second boundary box

        Output :
            result (boolean) : True or False

    """
    (x_min_a, y_min_a, x_max_a, y_max_a) = bbox_a
    (x_min_b, y_min_b, x_max_b, y_max_b) = bbox_b

    return x_min_a <= x_max_b and x_max_a >= x_min_b and y_min_a <= y_max_b and y_max_a >= y_min_b


def ogr_geom_to_geojson(ogr_geometry, bbox=True):
    def coordinates_loop(geom, bbox_launch):

        bbox = ()

        # if geometry collection
        if geom.GetGeometryType() == 7:
            geom_collection_list = []
            for i, under_geom in enumerate(geom):
                geom_geojson = ogr_geom_to_geojson(under_geom, bbox_launch)
                geom_collection_list.append(geom_geojson)

                if bbox_launch:
                    if i == 0:
                        bbox = geom_geojson['bbox']
                    else:
                        bbox = bbox_union(bbox, geom_geojson['bbox'])

            return geom_collection_list, tuple(bbox)

        # if point
        elif geom.GetGeometryType() == 1:
            return [geom.GetX(), geom.GetY()], (geom.GetX(), geom.GetY(), geom.GetX(), geom.GetY())

        # for linestring, polygon, multipoint, multilinestring, multipolygon
        else:
            # iterate over geometries
            if geom.GetGeometryCount() > 0:
                coordinates_list = [0] * geom.GetGeometryCount()
                for j, under_geom in enumerate(geom):
                    # linearring compose polygon if j > 0 then j is a hole.
                    # Hole is inside polygon so we do not need to loop on this coordinate
                    if under_geom.GetGeometryName() == 'LINEARRING' and j > 0:
                        bbox_launch = False
                    else:
                        bbox_launch = True

                    coordinates_list[j], under_bbox = coordinates_loop(under_geom, bbox_launch)
                    if bbox_launch:
                        # bbox
                        if j == 0:
                            bbox = under_bbox
                        else:
                            bbox = bbox_union(bbox, under_bbox)

                return coordinates_list, tuple(bbox)

            # iterate over points
            if geom.GetPointCount() > 0:
                coordinates_list = [0] * geom.GetPointCount()
                for i in range(geom.GetPointCount()):
                    # coordinates
                    point = geom.GetPoint(i)
                    coordinates_list[i] = [point[0], point[1]]
                    # bbox
                    if bbox_launch:
                        if i == 0:
                            bbox = [point[0], point[1], point[0], point[1]]
                        else:
                            if point[0] < bbox[0]:
                                bbox[0] = point[0]
                            if point[0] > bbox[2]:
                                bbox[2] = point[0]
                            if point[1] < bbox[1]:
                                bbox[1] = point[1]
                            if point[1] > bbox[3]:
                                bbox[3] = point[1]

                return coordinates_list, tuple(bbox)

    dico = {}
    ogr_geom_type = ogr_geometry.GetGeometryType()
    dico['type'] = ogr_geom_type_to_geoformat_geom_type(ogr_geom_type)

    # adding bbox
    if bbox == True:
        coordinates, bbox = coordinates_loop(ogr_geometry, True)
        dico['bbox'] = bbox
    else:
        coordinates, bbox = coordinates_loop(ogr_geometry, False)

    # adding coordinates for geometries
    # if GeometryCollection
    if ogr_geom_type != 7:
        dico['coordinates'] = coordinates
    # for others geometries
    else:
        dico['geometries'] = coordinates

    return dico


def geojson_to_ogr_geom(geojson):
    def coordinates_loop(coordinates, ogr_geom):
        """
        2D ONLY -- if 3D change AddPoint_2D by AddPoint and add 3D type in GetGeometryType test.
        """

        # if geometry collection
        if ogr_geom.GetGeometryType() == 7:
            for geojson_geom in coordinates:
                new_ogr_geom = geojson_to_ogr_geom(geojson_geom)
                ogr_geom.AddGeometry(new_ogr_geom)

            return ogr_geom

        # if point
        elif ogr_geom.GetGeometryType() == 1:
            ogr_geom.AddPoint_2D(coordinates[0], coordinates[1])
            return ogr_geom

        # for linestring, polygon, multipoint, multilinestring, multipolygon
        else:
            if ogr_geom.GetGeometryType() == 4:
                under_ogr_geom = ogr.Geometry(ogr.wkbPoint)
            elif ogr_geom.GetGeometryType() == 6:
                under_ogr_geom = ogr.Geometry(ogr.wkbPolygon)
            elif ogr_geom.GetGeometryType() == 3:
                under_ogr_geom = ogr.Geometry(ogr.wkbLinearRing)
            elif ogr_geom.GetGeometryType() == 5:
                under_ogr_geom = ogr.Geometry(ogr.wkbLineString)

            for i, coordinates_list in enumerate(coordinates):
                if ogr_geom.GetGeometryType() == 2:
                    if i == 0:
                        if ogr_geom.GetGeometryName() == 'LINESTRING':
                            ogr_geom = ogr.Geometry(ogr.wkbLineString)
                        else:
                            ogr_geom = ogr.Geometry(ogr.wkbLinearRing)
                    ogr_geom.AddPoint_2D(coordinates_list[0], coordinates_list[1])

                else:
                    if i == 0 and ogr_geom.GetGeometryType() == 3:
                        ogr_geom = ogr.Geometry(ogr.wkbPolygon)
                    new_geom = coordinates_loop(coordinates_list, under_ogr_geom)
                    ogr_geom.AddGeometry(new_geom)

            return ogr_geom

    geo_type = geojson['type']
    if geo_type.upper() == 'POINT':
        ogr_geom = ogr.Geometry(ogr.wkbPoint)
    elif geo_type.upper() == 'LINESTRING':
        ogr_geom = ogr.Geometry(ogr.wkbLineString)
    elif geo_type.upper() == 'POLYGON':
        ogr_geom = ogr.Geometry(ogr.wkbPolygon)
    elif geo_type.upper() == 'MULTIPOINT':
        ogr_geom = ogr.Geometry(ogr.wkbMultiPoint)
    elif geo_type.upper() == 'MULTILINESTRING':
        ogr_geom = ogr.Geometry(ogr.wkbMultiLineString)
    elif geo_type.upper() == 'MULTIPOLYGON':
        ogr_geom = ogr.Geometry(ogr.wkbMultiPolygon)
    elif geo_type.upper() == 'GEOMETRYCOLLECTION':
        ogr_geom = ogr.Geometry(ogr.wkbGeometryCollection)
    elif geo_type.upper() == 'NO GEOMETRY':
        ogr_geom = ogr.Geometry(ogr.wkbNone)
    elif geo_type.upper() == 'GEOMETRY':
        ogr_geom = ogr.Geometry(ogr.wkbUnknown)

    if geo_type != 'NO GEOMETRY':
        if geo_type != 'GEOMETRYCOLLECTION':
            ogr_geom = coordinates_loop(geojson['coordinates'], ogr_geom)
        else:
            ogr_geom = coordinates_loop(geojson['geometries'], ogr_geom)

    return ogr_geom


def ogr_layer_to_geolayer(path, layer_id=None, field_name_filter=None, driver_name=None, bbox_extent=True,
                          bbox_filter=None, feature_serialize=False, feature_limit=None, feature_offset=None):
    """
    'ogr_layer_to_geolayer' permet d'ouvrier un fichier sig externe (attributaire ou géométrique), de le lire et de
    stocker des informations filtrées. Il faut lui renseigner un chemin vers le fichier (obligatoirement).

    :param path: chemin d'accès au fichier + nom fichier ; Format : string ; ex : "C:\dataPython\com.shp"
    :param layer_id: identifiant ou nom table concernée ; Format : string ou integer ou none
    :param field_name_filter: liste noms des champs filtrant ; Format : StringList  ou none
    :param driver_name: format du fichier en lecture, le script peu le déterminer ; Format : string (majuscule) ou none
    :param bbox_extent: if you want to add bbox for each geometry and extent in metadata
    :param bbox_filter if wout want make a bbox filter when you import data


    :return: geolayer : layer au format geoformat basé sur le fichier path renseigné en entrée filtrées par field_name_filter
    """

    # création de la layer geolayer (conteneur de base)
    geolayer = {}

    # ouvert la data source avec ou sans driver défini
    if driver_name:
        driver = ogr.GetDriverByName(driver_name)
        data_source = driver.Open(path)
    else:
        # détection du driver compris dans la fonction ogr.Open()
        data_source = ogr.Open(path)

    # open layer (table) - condition valable pour les databases notamment
    if not layer_id:
        # si pas d'identifiant de layer
        layer = data_source.GetLayer()
    else:
        if isinstance(layer_id, str):
            # si l'identifiant est un string : le nom de la layer
            layer = data_source.GetLayerByName(layer_id)
        elif isinstance(layer_id, int):
            # si l'identifiant est un nombre
            layer = data_source.GetLayer(layer_id)

    # récupération de la LayerDefn() via la fonction ogr
    layer_defn = layer.GetLayerDefn()

    # creation du dictionnaire des métadonnées des champs et ajout du nombre de champ dans la layer
    metadata = {'fields': {}}
    # boucle sur la structure des champs de la layer en entree
    if field_name_filter:
        # gestion de la correspondance de la case champs/field_name_filtres
        field_name_filter_up = [field_name.upper() for field_name in field_name_filter]
        # création liste vide pour stocker après le nom de champ initiaux de la table en entrée
        field_name_ori = []
        # récupération éléments pour chaque champ compris dans la layer definition

    if field_name_filter:
        # si field_name_filter on réinitialize l'ordre d'apparition des champs à 0
        i_field_filter = 0
    for i_field in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i_field)
        field_name = field_defn.GetName()
        field_type = field_defn.GetType()
        field_width = field_defn.GetWidth()
        field_precision = field_defn.GetPrecision()

        # ecriture de la metadata des champs du filtre dans les metadonnees des champs
        write_metadata = True
        # vérification si field_name_filter renseigné
        if field_name_filter:
            # si field_name est dans field_name_filter (gestion de la case)
            if field_name.upper() not in field_name_filter_up:
                write_metadata = False
            else:
                field_name_ori.append(field_name)
        if write_metadata:
            # si oui : écriture chaque informatation dans la métadonnée
            if field_name_filter:
                # on écrit les caractéristiques des champs et on remets à jour la variable index
                metadata['fields'][field_name] = {'type': field_type, 'width': field_width,
                                                  'precision': field_precision, 'index': i_field_filter}
                i_field_filter += 1
            else:
                # on écrit les caractéristiques des champs
                metadata['fields'][field_name] = {'type': field_type, 'width': field_width,
                                                  'precision': field_precision, 'index': i_field}

    # if geometry
    if layer.GetGeomType() != 100:
        # add geometry metadata
        metadata['geometry_ref'] = {'type': ogr_geom_type_to_geoformat_geom_type(layer.GetGeomType())}
        if layer.GetSpatialRef():
            metadata['geometry_ref']['crs'] = layer.GetSpatialRef().ExportToWkt()
        else:
            metadata['geometry_ref']['crs'] = None

        if bbox_extent:
            metadata['geometry_ref']['extent'] = None

    # nom de la layer
    metadata['name'] = layer.GetName()

    if feature_serialize:
        metadata['feature_serialize'] = True

    # ajout des metadadonnees dans geolayer
    geolayer['metadata'] = metadata

    # creation des features indépendamment les unes des autres, création structure attributaire pour chaque feature
    geolayer['features'] = {}

    #
    # i_feat : feature_id in input layer
    # i_feat_writed : feature_id in output layer
    # write_feature : True|False say if a feature can or cannot be written this depending on
    # filters option setting :
    #                           bbox_filter
    #                           feature_limit
    #                           feature_offset
    i_feat_writed = 0
    # set who list unique geometry type in layer
    geom_type_set = set([])
    for i_feat, feature in enumerate(layer):
        # init
        write_feature = True
        # test feature offset and limit
        if feature_offset:
            if i_feat < feature_offset:
                write_feature = False

        if feature_limit:
            # stop loop if feature_limit is reached
            if i_feat_writed == feature_limit:
                break

        if write_feature:
            # creation d'un dictionnaire vide pour chaque entité
            new_feature = {}

            ################################################################################################################
            #
            #   geometry
            #
            ################################################################################################################

            # test if geom in feature
            geom = feature.GetGeometryRef()
            if geom:
                # get geometry type
                if geom.GetGeometryType() != geoformat_geom_type_to_ogr_geom_type(
                        metadata['geometry_ref']['type']) or ogr_geom_type_to_geoformat_geom_type(
                        geom.GetGeometryType()) not in geom_type_set:
                    geom_type_set = set(
                        [ogr_geom_type_to_geoformat_geom_type(geom.GetGeometryType())] + list(geom_type_set))

                # recuperation des geometries / ajout dans le dictionnaire des features
                temp_bbox_extent = False
                if bbox_filter is not None:
                    temp_bbox_extent = True

                # bbox and extent must be computed
                if bbox_extent or temp_bbox_extent:
                    geom_json = ogr_geom_to_geojson(geom, True)
                    if bbox_extent:
                        # modify extent in metadata
                        if geolayer['metadata']['geometry_ref']['extent'] is None:
                            geolayer['metadata']['geometry_ref']['extent'] = geom_json['bbox']
                        else:
                            extent_bbox = geolayer['metadata']['geometry_ref']['extent']
                            extent_bbox = bbox_union(extent_bbox, geom_json['bbox'])
                            geolayer['metadata']['geometry_ref']['extent'] = extent_bbox
                else:
                    geom_json = ogr_geom_to_geojson(geom, False)

                if bbox_filter:
                    feat_bbox = geom_json['bbox']
                    if bbox_intersects_bbox(bbox_filter, feat_bbox):
                        if bbox_extent:
                            new_feature['geometry'] = geom_json
                        else:
                            del geom_json['bbox']
                            new_feature['geometry'] = geom_json
                    else:
                        write_feature = False
                else:
                    new_feature['geometry'] = geom_json

        ################################################################################################################
        #
        #   attributes
        #
        ################################################################################################################
        if write_feature:
            # ajout des données attributaires
            new_feature['attributes'] = {}
            # recuperation des informations attributaires pour les features
            # si option filtre sur champ
            if field_name_filter:
                for field_name in field_name_ori:
                    new_feature['attributes'][field_name] = feature.GetField(field_name)

            else:
                # récupérer la valeur du nom des champs
                for field_name in geolayer['metadata']['fields']:
                    new_feature['attributes'][field_name] = feature.GetField(field_name)

            if feature_serialize:
                # new_feature = zlib.compress(cPickle.dumps(new_feature))
                # new_feature = zlib.compress(str(new_feature))
                new_feature = str(new_feature)

            geolayer['features'][i_feat_writed] = new_feature
            i_feat_writed += 1

    ## Check layer metadata

    # GEOMETRY METADATA
    # if there is a difference between layer metadata geom type and scan
    if 'geometry_ref' in metadata:
        if geom_type_set != set(metadata['geometry_ref']['type']):
            if len(geom_type_set) == 0:
                metadata['geometry_ref']['type'] = 'No Geometry'
            elif len(geom_type_set) == 1:
                metadata['geometry_ref']['type'] = list(geom_type_set)[0]
            else:
                metadata['geometry_ref']['type'] = list(geom_type_set)

    return geolayer


# -----------------------------------------------------------------------------------------------------------------------

def ogr_layers_to_geocontainer(path, field_name_filter=None, driver_name=None, bbox_extent=True, bbox_filter=None,
                               feature_limit=None, feature_serialize=False):
    """
    'ogr_layers_to_geocontainer' crée une géodatasource comprenant des géolayers (format geoformat). Elle requiere
    la fonction layer_to_geoformat car elle boucle sur la fonction layer_to_geoformat, ce qui permet de récupérer les
    différentes géolayer et de les encapsuler dans une datasource.

    :param path: chemin d'accès au fichier + nom fichier ; Format : string ou list
    :param field_name_filter: liste noms des champs filtrant, même filtre pour tous; Format : StringList  ou none
    :param driver_name: format(s) fichier en lecture, script peu le déterminer ; Format : string (majuscule) ou liste ou none
    :param bbox_extent: if you want to add bbox for each geometry and extent in metadata
    :param bbox_filter: if you want filter input feature with a given bbox


    :return: géodatasource : un conteneur de layer au geoformat, filtrées par le fiel_name_filter
    """

    # fonction qui permet de boucler sur la 'layer_to_geoformat'
    def loop_list_layer(path, field_name_filter=None, driver_name=None, bbox_extent=None, bbox_filter=None,
                        feature_serialize=False):
        """
        'loop_list_layer' permet de lancer en boucle la fonction ogr_layer_to_geolayer.

        :param path: chemin d'un fichier
        :param field_name_filter: liste noms des champs filtrant
        :param driver_name: format fichier en lecture
        :return: yield de géolayer
        """

        if driver_name:
            # si driver_name renseigné
            driver = ogr.GetDriverByName(driver_name)
            data_source = driver.Open(path)


        else:
            # détection interne du driver via la fonction ogr.open()
            data_source = ogr.Open(path)

        # lancement de la fonction ogr_layer_to_geolayer() et récupération des layers au fur et à mesure
        for layer_id, layer in enumerate(data_source):
            geolayer = ogr_layer_to_geolayer(path, layer_id, field_name_filter=field_name_filter,
                                             driver_name=driver_name, bbox_extent=bbox_extent, bbox_filter=bbox_filter,
                                             feature_limit=feature_limit, feature_serialize=feature_serialize)
            yield geolayer

    # création du conteneur de layers
    geocontainer = {'layers': {}, 'metadata': {}}

    # init parameters
    temp_layer_path, temp_field_name_filter, temp_driver_name, temp_bbox_extent, temp_bbox_filter = None, None, None, None, None

    # test si le path est une liste, si oui : boucle pour chaque élément de la liste
    if isinstance(path, str):
        path = [path]

    for i_path, temp_layer_path in enumerate(path):

        if not isinstance(temp_layer_path, str):
            sys.exit('path must be a string')

        temp_field_name_filter = None
        # test si field_name_filter renseigné
        if field_name_filter:
            if isinstance(field_name_filter[i_path], str):
                temp_field_name_filter = field_name_filter
            else:
                temp_field_name_filter = field_name_filter[i_path]
        temp_driver_name = None

        # test driver_name
        if driver_name:
            temp_driver_name = driver_name[i_path]
            if isinstance(driver_name, list):
                temp_driver_name = driver_name[i_path]
            else:
                temp_driver_name = driver_name

        # test bbox extent
        if bbox_extent:
            if isinstance(bbox_extent, list):
                temp_bbox_extent = bbox_extent[i_path]
            else:
                temp_bbox_extent = bbox_extent

        # si bbox filter
        if bbox_filter:
            if isinstance(bbox_extent, list):
                temp_bbox_filter = bbox_extent[i_path]
            else:
                temp_bbox_filter = bbox_filter

        # lancement de la fonction loop_list_layer
        for i_geolayer, geolayer in enumerate(
                loop_list_layer(temp_layer_path, temp_field_name_filter, temp_driver_name, temp_bbox_extent,
                                temp_bbox_filter, feature_serialize)):
            # stockage des returns yield de la fonction loop
            geolayer_name = geolayer['metadata']['name']
            geocontainer['layers'][geolayer_name] = geolayer
            if temp_bbox_extent:
                geolayer_extent = geolayer['metadata']['geometry_ref']['extent']
                if i_geolayer == 0:
                    geocontainer_extent = geolayer_extent
                else:
                    geocontainer_extent = bbox_union(geocontainer_extent, geolayer_extent)
                geocontainer['metadata']['extent'] = geocontainer_extent

    # # test si path est en string, on lance le loop mais elle tournera qu'une fois
    # elif isinstance(path, str):
    #     for geolayer in loop_list_layer(path, field_name_filter, driver_name, bbox_extent, bbox_filter, feature_serialize):
    #         # stockage du return yield de la fonction loop
    #         geolayer_name = geolayer['metadata']['name']
    #         geocontainer['layers'][geolayer_name] = geolayer

    # # message d'erreur
    # else:
    #     sys.exit('erreur format path non valide')

    return geocontainer


# -----------------------------------------------------------------------------------------------------------------------

def geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=None, field_order=False, feature_serialize=False):
    """
    'geolayer_to_ogr_layer' est une procedure qui permet d'exporter une géolayer dans plusieurs format : esri shapefile,
    kml, xlsx, postegresql. La layer peut être attributaire et/ou géométrique

    Example ogr_options : ogr_options=['OVERWRITE=YES']

    :param geolayer: layer au géoformat
    :param path: le chemin où aller l'exporter
    :param driver_name: le format dans laquelle l'exporter

    """

    # création de l'ensemble des informations pour créer un fichier au format SIG
    # création d'un driver
    driver = ogr.GetDriverByName(driver_name)

    # récupération du path en 2 parties : la racine et l'extension
    (root, ext) = os.path.splitext(path)

    # test si il y a pas une extension
    if ext == '':
        # alors c'est un dossier ou un l'adresse d'une base de données
        # recupération du nom de la layer
        layer_name = geolayer['metadata']['name']
        # si le chemin est bien un dossier existant
        if os.path.isdir(root):
            # récupération de l'extension suivant le driver_name
            # attention rajouter d'autres driver name
            if driver_name.upper() == 'ESRI SHAPEFILE':
                new_ext = '.shp'
            elif driver_name.upper() == 'KML':
                new_ext = '.kml'
            elif driver_name.upper() == 'XLSX':
                new_ext = '.xlsx'
            elif driver_name.upper() == 'CSV':
                new_ext = '.csv'
            elif driver_name.upper() == 'GEOJSON':
                new_ext = '.geojson'
            else:
                sys.exit('format non pris en compte')
            new_path = root + layer_name + new_ext
        else:
            # Then we suppose that is a datasource
            if ogr.Open(root) is not None:
                if driver_name.upper() == 'POSTGRESQL':
                    new_path = path
            else:
                sys.exit("your path does not exists or is invalid")
        data_source = driver.CreateDataSource(new_path)
    else:
        if driver_name == 'XLSX':
            # on test s'il existe
            data_source = driver.Open(path, 1)
            if not data_source:
                print('create')
                data_source = driver.CreateDataSource(path)
            else:
                print('exist')
        else:
            # alors c'est un fichier
            data_source = driver.CreateDataSource(path)

    # récupération dans geolayer des informations nécessaire à la création d'une layer : nom, projection, geometry_type
    layer_name = geolayer['metadata']['name']
    layer_crs = None
    layer_ogr_geom_type = 100

    if 'geometry_ref' in geolayer['metadata']:
        if 'crs' in geolayer['metadata']['geometry_ref']:
            crs_data = geolayer['metadata']['geometry_ref']['crs']
            # from EPSG
            if isinstance(crs_data, int):
                layer_crs = osr.SpatialReference()
                layer_crs.ImportFromEPSG(crs_data)
            # from OGC WKT
            elif isinstance(crs_data, str):
                try:
                    layer_crs = osr.SpatialReference(crs_data)
                except:
                    # si le format n'est pas reconnu tant pis pas de ref spatiale
                    print('warning projection not recognize')
            else:
                print('crs value must be a ESPG code or a  OGC WKT projection')

        if 'type' in geolayer['metadata']['geometry_ref']:
            layer_ogr_geom_type = verify_geom_compatibility(driver_name, geolayer['metadata']['geometry_ref']['type'])

    if 'feature_serialize' in geolayer['metadata'].keys():
        feature_serialize = geolayer['metadata']['feature_serialize']

    # création réelle de la layer
    if ogr_options:
        layer = data_source.CreateLayer(layer_name, srs=layer_crs, geom_type=layer_ogr_geom_type, options=ogr_options)
    else:
        layer = data_source.CreateLayer(layer_name, srs=layer_crs, geom_type=layer_ogr_geom_type)

    # création des fields (structure du fichier)
    # si l'on souhaite que l'ordre d'apparition des champs soit conservée
    if 'fields' in geolayer['metadata']:
        if field_order:
            field_name_list = [0] * len(geolayer['metadata']['fields'])
            for field_name in geolayer['metadata']['fields']:
                field_name_list[geolayer['metadata']['fields'][field_name]['index']] = field_name
        else:
            field_name_list = geolayer['metadata']['fields'].keys()

        for field_name in field_name_list:
            # récupération des informations nécessaire à la création des champs
            field_type = geolayer['metadata']['fields'][field_name]['type']
            field_width = geolayer['metadata']['fields'][field_name]['width']
            field_precision = geolayer['metadata']['fields'][field_name]['precision']

            # création de la définition du champ (type, longueur, precision)
            field = ogr.FieldDefn(field_name, field_type)
            field.SetWidth(field_width)
            field.SetPrecision(field_precision)

            # création du champ
            layer.CreateField(field)

        # creation table de correspondance [au cas où la taille des champs est réduite lors de la création de la layer]
        # example DBF = 10 char maximum
        # if layerDefn() is define
        try:
            ct_field_name = {}
            for i in range(layer.GetLayerDefn().GetFieldCount()):
                ct_field_name[field_name_list[i]] = layer.GetLayerDefn().GetFieldDefn(i).GetName()
        except:
            ct_field_name = {field_name: field_name for field_name in field_name_list}

    # création des features
    for i_feat in geolayer['features']:

        # if layerDefn() is define
        try:
            feature_ogr = ogr.Feature(layer.GetLayerDefn())
        except:
            feature_ogr = ogr.Feature()

        feature_geoformat = geolayer['features'][i_feat]
        if feature_serialize:
            feature_geoformat = eval(feature_geoformat)

        # if geometry in feature
        if 'geometry' in feature_geoformat:
            # get geometry in geojson format like
            geom_json = feature_geoformat['geometry']
            # transform geometry to ogr geometry
            geom_ogr = geojson_to_ogr_geom(geom_json)
            # add geometry in ogr feature object
            feature_ogr.SetGeometry(geom_ogr)

        # test if attributes data in feature
        if 'attributes' in feature_geoformat:
            # loop on each layer [metadata] fields
            for field_name in geolayer['metadata']['fields']:
                # we recuperate true field name [in case it has been truncated]
                true_field_name = ct_field_name[field_name]
                if field_name in feature_geoformat['attributes']:
                    value_field = feature_geoformat['attributes'][field_name]
                    # if field value is not NULL
                    if value_field is not None:
                        # write data if error change field_value to string
                        try:
                            feature_ogr.SetField(true_field_name, value_field)
                        except NotImplementedError:
                            feature_ogr.SetField(true_field_name, str(value_field))

        layer.CreateFeature(feature_ogr)

    data_source.Destroy()


# -----------------------------------------------------------------------------------------------------------------------

def geocontainer_to_ogr_format(geocontainer, path, driver_name, export_layer_list=None, ogr_options=None,
                               field_order=False, feature_serialize=False):
    """
    'geocontainer_to_ogr_format' est une procedure qui permet d'exporter une sélection ou l'ensemble des layers d'une
    datasource aux formats voulus. Le path renseignée peut être un dossier, une datasource, ou un fichier. On peut
    renseigner une liste ou un nom de layer pour filtrer l'export.

    :param geocontainer: la géodatasource complete
    :param path: chemin où aller sauvegarder (il peut être une liste ou un str)
    :param driver_name: le nom du drive peut etre une liste ou un seul qu'on applique à tous
    :param export_layer_list: liste des layers de la datasource a exporter, peut être list ou str. Si export_layer_list
    non rempli alors on exporte toutes les layers, si export layer_list rempli = on exporte que ces layers là.
    Variable possible pour cette list : 'tc', 'ref_a', 'ref_b' (seulement)
    """

    if export_layer_list:
        # test si il y a une liste des layers à exporter
        if isinstance(export_layer_list, list):
            for i_layer, export_layer_name in enumerate(export_layer_list):
                # test si la layer fait partie de la liste des layers à sauvegarder
                if export_layer_name in geocontainer['layers'].keys():
                    geolayer = geocontainer['layers'][export_layer_name]
                    if isinstance(path, list):
                        # path = fichier en dur
                        if isinstance(driver_name, list):
                            geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name[i_layer],
                                                  ogr_options=ogr_options[i_layer], field_order=field_order,
                                                  feature_serialize=feature_serialize)
                        else:
                            geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name, ogr_options=ogr_options,
                                                  field_order=field_order, feature_serialize=feature_serialize)
                    else:
                        # path = dossier ou database
                        if isinstance(driver_name, list):
                            geolayer_to_ogr_layer(geolayer, path, driver_name[i_layer],
                                                  ogr_options=ogr_options[i_layer], field_order=field_order,
                                                  feature_serialize=feature_serialize)
                        else:
                            geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=ogr_options,
                                                  field_order=field_order, feature_serialize=feature_serialize)

        # si export_layer_list n'est pas une liste, elle contient qu'une valeur
        elif isinstance(export_layer_list, str):
            geolayer = geocontainer['layers'][export_layer_list]
            geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=ogr_options, field_order=field_order,
                                  feature_serialize=feature_serialize)  # il y aura alors que 1 path et 1 driver name


    # si export_layer_list=None alors on exporte l'ensemble des layers de la geocontainer
    else:
        for i_layer, layer_name in enumerate(geocontainer['layers']):
            geolayer = geocontainer['layers'][layer_name]
            # si le path est une liste :
            if isinstance(path, list):
                # et si le driver_name est une liste
                if isinstance(driver_name, list):
                    geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name[i_layer],
                                          ogr_options=ogr_options[i_layer], field_order=field_order,
                                          feature_serialize=feature_serialize)
                # si non utiliser toujours le même driver
                else:
                    geolayer_to_ogr_layer(geolayer, path[i_layer], driver_name, ogr_options=ogr_options,
                                          field_order=field_order, feature_serialize=feature_serialize)
            # sinon utiliser le même dossier
            else:
                # test sur le driver_name pour voir lequel on donne
                if isinstance(driver_name, list):
                    geolayer_to_ogr_layer(geolayer, path, driver_name[i_layer], ogr_options=ogr_options[i_layer],
                                          field_order=field_order, feature_serialize=feature_serialize)
                else:
                    geolayer_to_ogr_layer(geolayer, path, driver_name, ogr_options=ogr_options, field_order=field_order,
                                          feature_serialize=feature_serialize)


# -----------------------------------------------------------------------------------------------------------------------

def create_pk(geolayer, pk_field_name):
    """
    'create_pk' est un dictionnaire qui permet de faire le lien entre les itérateurs features et la valeur d'un champ.

    :param geolayer: la layer au géoformat
    :param pk_field_name: le nom du champs à "indexer"
    :return: géolayer avec une contrainte de pk avce la clé du champs rajouté
    """
    # création du dictionnaire vide
    pk_dico = {}

    # récupération de la value du champs à indexer
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        pk_field_value = feature['attributes'][pk_field_name]
        # vérification que les valeurs sont uniques
        if pk_field_value in pk_dico:
            sys.exit('le champ indiqué contient des valeurs non unique')
        else:
            # récupération de la valeur de l'itérateur
            pk_dico[pk_field_value] = i_feat

    # affectation du dictionnaire dans les métadonnées de la géolayer
    # geolayer['metadata']['constraints'] = {'pk': {}}
    # geolayer['metadata']['constraints']['pk'][pk_field_name] = pk_dico

    return pk_dico


def create_attribute_index(geolayer, field_name):
    index_dico = {'type': 'hashtable', 'index': {}}

    # récupération de la valeur du champs à indexer
    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        field_value = feature['attributes'][field_name]

        try:
            index_dico['index'][field_value].append(i_feat)
        except:
            index_dico['index'][field_value] = [i_feat]

    return index_dico


def coordinates_to_point(coordinates):
    """
    With geometry coordinates this function return each point individually in iterator
    :param coordinates
    :yield point coordinate
    """

    if isinstance(coordinates[0], (int, float)):
        yield coordinates
    else:
        for inner_coordinates in coordinates:
            for point in coordinates_to_point(inner_coordinates):
                yield point


def coordinates_to_bbox(coordinates):
    """
    This function return boundaries box (bbox) from geometry coordinates.
    It's works with 2 to n-dimentional data.
    (x_min, y_min, n_min, x_max, y_max, n_max)

    """

    # loop on each coordinates
    for i_pt, point in enumerate(coordinates_to_point(coordinates)):
        # create empty bbox at first iteration
        if i_pt == 0:
            bbox = [None] * (len(point) * 2)
        # loop on dimension of coordinate
        for i_coord, pt_coord in enumerate(point):
            # add data at firt iteration
            if i_pt == 0:
                bbox[i_coord] = pt_coord

            test_value_min_tuple = (bbox[i_coord], pt_coord)
            bbox[i_coord] = min(value for value in test_value_min_tuple if value is not None)
            # print(1, bbox)
            # print(2, i_coord,  len(point), bbox[i_coord + len(point)], pt_coord)
            # print(3, bbox[i_coord + len(point)])
            # print(4, max(bbox[i_coord + len(point)], pt_coord))
            test_value_max_tuple = (bbox[i_coord + len(point)], pt_coord)
            bbox[i_coord + len(point)] = max(value for value in test_value_max_tuple if value is not None)

    return tuple(bbox)


def get_geocontainer_extent(geocontainer):
    if 'metadata' in geocontainer.keys():
        if 'extent' in geocontainer['metadata']:
            return geocontainer['metadata']['extent']
    else:
        for i_layer, geolayer in enumerate(geocontainer['layers']):
            geolayer_bbox = None
            if 'geometry_ref' in geolayer['metadata']:
                if 'extent' in geolayer['metadata']['geometry_ref']:
                    geolayer_bbox = geolayer['metadata']['geometry_ref']['extent']
            else:
                # no geometry in geolayer
                return None

            if not geolayer_bbox:
                for i_feat in geolayer['features']:
                    feature_bbox = None
                    if 'geometry' in geolayer['features'][i_feat].keys():
                        if 'bbox' in geolayer['features'][i_feat]['geometry']:
                            feature_bbox = geolayer['features'][i_feat]['geometry']['bbox']

                        else:
                            feature_bbox = coordinates_to_bbox(geolayer['features'][i_feat]['geometry'])
                    else:
                        # no geometry in geolayer
                        return None

                    if i_feat == 0:
                        geolayer_bbox = feature_bbox
                    else:
                        geolayer_bbox = bbox_union(geolayer_bbox, feature_bbox)

            if i_layer == 0:
                geocontainer_extent = geolayer_bbox
            else:
                geocontainer_extent = bbox_union(geocontainer_extent, geolayer_bbox)

    return geocontainer_extent


def envelope_to_g_id(envelope, mesh_size):
    """
    Cette fonction permet de trouver au moyen de coordonnées d'une enveloppe d'une géométrie, l'index de la maille de grille
    à laquelle la géométrie appartient
    :param envelope [list or tuple]: enveloppe du feature d'un polygone
    :param mesh_size [int]: taille de la maille choisie
    :return: g_id_list [str] : Index de la maille dans laquelle se trouve le polygone
    """
    x_min, y_min, x_max, y_max = envelope[0], envelope[2], envelope[1], envelope[3]

    id_x_min = int(x_min / mesh_size)
    id_x_max = int(x_max / mesh_size)
    id_y_min = int(y_min / mesh_size)
    id_y_max = int(y_max / mesh_size)

    for xStep in range(id_x_min, id_x_max + 1):
        for yStep in range(id_y_min, id_y_max + 1):
            yield str(xStep) + "_" + str(yStep)


def point_bbox_position(point, bbox):
    """
    Renvoie la position d'un point par rapport à une bbox

       NW  |   N  |  NE
    -------+------+-------
        W  | bbox |   E
    -------+------+-------
       SW  |   S  |  SE

    """

    (pt_x, pt_y) = point
    (x_min, y_min, x_max, y_max) = bbox

    # Nord
    if (pt_x > x_min and pt_x < x_max) and (pt_y >= y_max):
        if pt_y == y_max:
            position = ('Boundary', 'N')
        else:
            position = ('Exterior', 'N')
    # Sud
    elif (pt_x > x_min and pt_x < x_max) and (pt_y <= y_min):
        if pt_y == y_min:
            position = ('Boundary', 'S')
        else:
            position = ('Exterior', 'S')
    # Est
    elif pt_x >= x_max and (pt_y > y_min and pt_y < y_max):
        if pt_x == x_max:
            position = ('Boundary', 'E')
        else:
            position = ('Exterior', 'E')
    # Ouest
    elif pt_x <= x_min and (pt_y > y_min and pt_y < y_max):
        if pt_x == x_min:
            position = ('Boundary', 'W')
        else:
            position = ('Exterior', 'W')
    # Nord-Ouest
    elif pt_x <= x_min and pt_y >= y_max:
        if pt_x == x_min and pt_y == y_max:
            position = ('Boundary', 'NW')
        else:
            position = ('Exterior', 'NW')
    # Nord-Est
    elif pt_x >= x_max and pt_y >= y_max:
        if pt_x == x_max and pt_y == y_max:
            position = ('Boundary', 'NE')
        else:
            position = ('Exterior', 'NE')
    # Sud-Est
    elif pt_x >= x_max and pt_y <= y_min:
        if pt_x == x_max and pt_y == y_min:
            position = ('Boundary', 'SE')
        else:
            position = ('Exterior', 'SE')
    # Sud-Ouest
    elif pt_x <= x_min and pt_y <= y_min:
        if pt_x == x_min and pt_y == y_min:
            position = ('Boundary', 'SW')
        else:
            position = ('Exterior', 'SW')
    # Point in bbox
    else:
        position = ('Interior', None)

    return position


def bbox_to_g_id(bbox, mesh_size, x_grid_origin=0., y_grid_origin=0.):
    """
    Cette fonction permet de trouver au moyen de coordonnées d'une enveloppe, l'index de la maille de grille
    à laquelle la bbox appartient

    :param bbox [list]: enveloppe du feature d'un polygone
    :param mesh_size [int]: taille de la maille choisie
    :param x_grid_origin: coordoonée en x du point originel a partir duquel est construit l'index
    :param y_grid_origin: coordoonée en y du point originel a partir duquel est construit l'index

    :return: g_id [str] : identifiant de la maille intersecté par la bbox
    """

    (x_min, y_min, x_max, y_max) = bbox
    # give x_g_id, y_g_id for bbox extremity
    id_x_min = int((x_min - x_grid_origin) / mesh_size)
    id_x_max = int((x_max - x_grid_origin) / mesh_size)
    id_y_min = int((y_min - y_grid_origin) / mesh_size)
    id_y_max = int((y_max - y_grid_origin) / mesh_size)

    # recuperate g_id and bbox associate
    g_id_min = str(id_x_min) + '_' + str(id_y_min)
    g_id_max = str(id_x_max) + '_' + str(id_y_max)

    bbox_g_id_min = g_id_to_bbox(g_id_min, mesh_size, x_grid_origin=x_grid_origin, y_grid_origin=y_grid_origin)
    bbox_g_id_max = g_id_to_bbox(g_id_max, mesh_size, x_grid_origin=x_grid_origin, y_grid_origin=y_grid_origin)

    # test point position for x_min, y_min if point touch boundary we must change id_x_min and/or id_y_min
    point_position, point_direction = point_bbox_position((x_min, y_min), bbox_g_id_min)

    if point_position == 'Boundary':
        if point_direction == 'S':
            id_y_min += - 1
        if point_direction == 'W':
            id_x_min += - 1
        if point_direction == "NW":
            id_x_min += - 1
        if point_direction == "SW":
            id_x_min += - 1
            id_y_min += - 1
        if point_direction == "SE":
            id_y_min += - 1

    # test point position for x_max, y_max if point touch boundary we must change id_x_max and/or id_y_max
    point_position, point_direction = point_bbox_position((x_max, y_max), bbox_g_id_max)

    if point_position == 'Boundary':
        if point_direction == 'N':
            id_y_max += 1
        if point_direction == 'E':
            id_x_max += 1
        if point_direction == "NE":
            id_x_max += 1
            id_y_max += 1
        if point_direction == "NW":
            id_y_max += 1
        if point_direction == "SE":
            id_x_max += 1

    # double loop sendind all g_id intersecting bbox
    for x_step in range(id_x_min, id_x_max + 1):
        for y_step in range(id_y_min, id_y_max + 1):
            yield str(x_step) + "_" + str(y_step)


def point_to_g_id(point_coordinates, mesh_size, x_grid_origin=0., y_grid_origin=0.):
    bbox = point_coordinates + point_coordinates

    for g_id in bbox_to_g_id(bbox, mesh_size, x_grid_origin, y_grid_origin):
        yield g_id


def g_id_to_point(g_id, mesh_size, position='center', x_grid_origin=0., y_grid_origin=0.):
    """
    This function return a coordinates point to given g_id (g_id). Obviously since it is a grid, the position of the
    point can be specified between this values ('center', 'NE', 'NW', 'SE',  'SW').

    If the grid origin is different to 0. you have to indicate the origin's coordinates (x_grid_origin or y_grid_origin)
    """

    x_min, y_min, x_max, y_max = g_id_to_bbox(g_id, mesh_size)

    if position == 'center':
        x, y = (x_min + x_max) / 2., (y_min + y_max) / 2.
    if position == 'NE':
        x, y = x_max, y_max
    if position == 'NW':
        x, y = x_min, y_max
    if position == 'SE':
        x, y = x_max, y_min
    if position == 'SW':
        x, y = x_min, y_min

    if x_grid_origin != 0.0 or y_grid_origin != 0.:
        x += x_grid_origin
        y += y_grid_origin

    return x, y


def g_id_to_bbox(g_id, mesh_size, x_grid_origin=0., y_grid_origin=0.):
    """
    This fucntion return the bbox associate to a given g_id (grid id).
    If the grid origin is different to 0. you have to indicate the origin's coordinates (x_grid_origin or y_grid_origin)

    """
    x_id, y_id = g_id.split('_')
    x_id, y_id = float(x_id), float(y_id)
    bbox_x_min = x_id * mesh_size
    bbox_x_max = (x_id + 1) * mesh_size
    bbox_y_min = y_id * mesh_size
    bbox_y_max = (y_id + 1) * mesh_size

    if x_grid_origin != 0. or y_grid_origin != 0.:
        bbox_x_min = x_grid_origin + bbox_x_min
        bbox_x_max = x_grid_origin + bbox_x_max
        bbox_y_min = y_grid_origin + bbox_y_min
        bbox_y_max = y_grid_origin + bbox_y_max

    return bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max


def create_grid_index(geo_layer, mesh_size=None, x_grid_origin=0, y_grid_origin=0):
    # first define mesh size if not yet define
    if not mesh_size:
        # création d'un index avec une maille à définir
        ## on calcul la hauteur et la largeur de base moyenne des entités pour déduire la taille de l'index
        size_x, size_y = 0, 0
        first_point = False
        for i, i_feat in enumerate(geo_layer['features']):
            feature = geo_layer['features'][i_feat]

            # if feature is serialized
            if 'feature_serialize' in geo_layer['metadata']:
                if geo_layer['metadata']['feature_serialize']:
                    feature = eval(feature)

            try:
                bbox = feature['geometry']['bbox']
            except:
                bbox = coordinates_to_bbox(feature['geometry']['coordinates'])
                feature['geometry']['bbox'] = bbox

            # if geometry type is point there is no dimension in same bbox (no lenght / no width) we have to compare
            #  with others points bbox
            if feature['geometry']['type'] == 'Point':
                if not first_point:
                    old_point_bbox = bbox
                    first_point = True
                else:
                    size_x += abs(bbox[2] - old_point_bbox[2])
                    size_y += abs(bbox[3] - old_point_bbox[3])
                    old_point_bbox = bbox

            else:
                size_x += bbox[2] - bbox[0]
                size_y += bbox[3] - bbox[1]

        mesh_size = max(size_x / len(geo_layer['features']), size_y / len(geo_layer['features']))

    index_dico = {}
    index_dico['metadata'] = {'type': 'grid', 'mesh_size': mesh_size, 'x_grid_origin': x_grid_origin,
                              'y_grid_origin': y_grid_origin}
    index_dico['index'] = {}

    for i_feat in geo_layer['features']:

        feature = geo_layer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geo_layer['metadata']:
            if geo_layer['metadata']['feature_serialize']:
                feature = eval(feature)

        # transform json to ogr
        geom = feature['geometry']

        now_now = time.time()
        if 'bbox' in geom.keys():
            bbox_geom = geom['bbox']
        else:
            coordinates = geom['coordinates']
            bbox_geom = coordinates_to_bbox(coordinates)

        # Pour chaque identifiant de maille on intègre dans grid_idx_dico la clef primaire de l'entité
        for g_id in bbox_to_g_id(bbox_geom, mesh_size, x_grid_origin=x_grid_origin, y_grid_origin=y_grid_origin):
            try:
                index_dico['index'][g_id].append(i_feat)
            except:
                index_dico['index'][g_id] = [i_feat]

    return index_dico


def i_feat_to_adjacency_neighbor(i_feat, matrix_adjacency, neighbor_set=None):
    """
    Use adjacency matrix to find all i_feat neighbor's
    """

    if not neighbor_set:
        neighbor_set = set([i_feat])

    # set store i_feat neighbor's
    i_feat_neighbor_set = set(matrix_adjacency[i_feat])
    # difference result between the list of neighbors already scanned and i_feat neighbors
    # Anyway, it's the list of new neighbors we haven't scanned yet.
    new_neighbor_set = set(i_feat_neighbor_set.difference(neighbor_set))
    # copy previous set
    new_neighbor_set_copy = set(new_neighbor_set)

    i = 0
    while new_neighbor_set_copy:
        # Loop scan every new neighbor
        for neighbor in new_neighbor_set:
            # set store i_feat neighbor's
            i_feat_neighbor_set = set(matrix_adjacency[neighbor])
            # new set of neighbors who have never been scanned before
            new_new_neighbor_set = i_feat_neighbor_set.difference(neighbor_set)
            # add the neighbor to the result list
            neighbor_set.update(set([neighbor]))
            # we add the new neighbors never scanned before
            new_neighbor_set_copy.update(new_new_neighbor_set)

            # we delete the scanned neighbor
            new_neighbor_set_copy = new_neighbor_set_copy.difference(set([neighbor]))

            i += 1
        # adding to new_neighbor_set ew neighbors that have never been scanned before
        new_neighbor_set = set(new_neighbor_set_copy)

    return list(neighbor_set)


def matrix_adjacency(geolayer, mesh_size=None):
    """
        Creation d'une matrice de proximité

    * OGR dependencie : Intersects *
    """
    matrix_dict = {}

    try:
        input_grid_idx = geolayer['metadata']['constraints']['index']['geometry']
    except:
        input_grid_idx = create_grid_index(geolayer, mesh_size=mesh_size)

    mesh_size = input_grid_idx['metadata']['mesh_size']

    # Création de la clé unique du dictionnaire de résultat (préparation du stockage des résultats)
    matrix_dict['matrix'] = {i_feat: [] for i_feat in geolayer['features']}

    for i_feat in geolayer['features']:
        feature_a = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature_a = eval(feature_a)

        # get bbox
        try:
            feature_a_bbox = feature_a['geometry']['bbox']
        except:
            feature_a_bbox = coordinates_to_bbox(feature_a['geometry']['coordinates'])
            feature_a['geometry']['bbox'] = feature_a_bbox

        # Récupération des identifiants de mailles présent dans l'index
        g_id_list = list(bbox_to_g_id(feature_a_bbox, mesh_size))

        # Pour chaque identifiant de maille de l'index on récupère l'identifant des autres polygones voisins de l'entité
        # en cours (s'ils existent)
        neighbour_i_feat_list = []
        for g_id in g_id_list:
            # récupération de la liste des clefs primaires des entités présentes dans la maille de l'index
            neighbour_i_feat_list += input_grid_idx['index'][g_id]

        # suppression de la clef primaire du polyone en cours et d'éventuels doublons
        neighbour_i_feat_list = [value for value in list(set(neighbour_i_feat_list)) if value != i_feat]

        # création  de la géométrie du feature A
        feature_a_ogr_geom = geojson_to_ogr_geom(feature_a['geometry'])
        # Même procédé que précédemment pour l'objet B
        for neighbour_i_feat in neighbour_i_feat_list:
            # si le i_feat n'est pas déjà compris dans la matrice de proximité du voisin :
            #  si c'est le cas alors cela veut dire que l'on a déjà fait un test d'intersection enrte les deux
            #  géométries auparavant (car pour avoir un voisin il faut etre deux)

            if i_feat not in matrix_dict['matrix'][neighbour_i_feat]:
                feature_b = geolayer['features'][neighbour_i_feat]

                # if feature is serialized
                if 'feature_serialize' in geolayer['metadata']:
                    if geolayer['metadata']['feature_serialize']:
                        feature_b = eval(feature_b)

                feature_b_ogr_geom = geojson_to_ogr_geom(feature_b['geometry'])

                if feature_a_ogr_geom.Intersects(feature_b_ogr_geom):
                    matrix_dict['matrix'][i_feat].append(neighbour_i_feat)
                    matrix_dict['matrix'][neighbour_i_feat].append(i_feat)

    matrix_dict['metadata'] = {'type': 'adjacency'}

    return matrix_dict


def create_layer_from_i_feat_list(geolayer, i_feat_list, feature_serialize=False, reset_i_feat=True):
    """
    Create a new layer with i_feat_list from an input layer
    """
    new_layer = {
        'metadata': dict(geolayer['metadata'])
    }

    if feature_serialize:
        geolayer['metadata']['feature_serialize'] = True

    new_layer['features'] = {}
    for new_i_feat, i_feat in enumerate(i_feat_list):
        if i_feat in geolayer['features']:
            if feature_serialize:
                new_feature = str(geolayer['features'][i_feat])
            else:
                new_feature = geolayer['features'][i_feat]

        if reset_i_feat:
            new_layer['features'][new_i_feat] = new_feature
        else:
            new_layer['feaures'][i_feat] = new_feature

    return new_layer


# -----------------------------------------------------------------------------------------------------------------------

# def export_geolayer_to_csv(save_path, geocontainer):
#     """
#     'export_geolayer_to_csv' permet d'exporter la table de correspondance dans un fichier au format csv.
#     Elle exporte que la tc de la geocontainer mais on pourrait rajouter aussi l'export dans autres layers.
#     On peut donner l'ordre des champs pour écrire dans le fichier en sortie.
#     'wb' et pas 'w' pour supprimer l'interligne vide entre chaque feature.
#     extrasaction='ignore' : permet d'ignorer si certains champs de la layer ne sont pas compris dans la sélection des
#     field_name renseigné.
#     field_name : permet de donner les champs et leur ordre d'écriture dans la layer_out
#
#     :param save_path: chemin + nom du fichier + extension du fichier en sortie
#     :param geocontainer: datasource de référence
#     """
#
#     layer_tc = geocontainer['layers']['tc']
#
#     with open(save_path, 'wb') as csvfile:
#         field_name = ('CODE_REF', 'EXIST_A', 'EXIST_B', 'ETAT_TC', 'REF_A', 'REF_B')
#         writer = csv.DictWriter(csvfile, fieldnames=field_name, extrasaction='ignore')
#         writer.writeheader()
#         for i_feat in layer_tc['features']:
#             writer.writerow(layer_tc['features'][i_feat]['attributes'])

# -----------------------------------------------------------------------------------------------------------------------

def save(geolayer, path, output_type='TXT'):
    """
    'save' est une procedure de sauvegarde des layers au geoformat. Elle prend en compte plusieurs formats (txt, bin ou
    zip). Pour autant, le binaire proposé ici n'est pas exactement du binaire, cela reste à vérifier.

    :param geolayer: nom du directionnaire / géolayer à enregistrer
    :param path: chemin d'enregistrement + le nom du fichier qu'on veut en sortie + l'extension
    :param output_type: format de sauvegarde : texte, binaire, ou compressé
    """
    # save au format txt
    if output_type == 'TXT':
        with open(path, 'w') as geolayer_txt:
            geolayer_txt.write(str(geolayer))

    # save au format binaire
    # attention wb permet pas d'enregistré en binaire
    elif output_type == 'BIN':
        with open(path, 'wb') as geolayer_bin:
            geolayer_bin.write(str(geolayer))

    # save au format binaire compressé
    elif output_type == 'ZIP':
        save_zip = zlib.compress(str(geolayer))
        with open(path, 'wb') as geolayer_zip:
            geolayer_zip.write(save_zip)

    # message error si format de save pas reconnu
    else:
        sys.exit("error output_type not recognize")


# -----------------------------------------------------------------------------------------------------------------------

def load(path, input_type='TXT'):
    """
    'load' est une fonction de téléchargement de layers au geoformat. Elle permet de lire plusieurs formats (txt, bin ou
    zip). Pour autant, le binaire proposé ici n'est pas exactement du binaire, cela reste à vérifier.

    :param load_path: chemin du fichier à télécharger
    :param input_type: format du fichier à télécahrger
    """

    try:
        # load format txt
        if input_type == 'TXT':
            with open(path, 'r') as load_txt:
                file_load = load_txt.read()

        # load format bin
        elif input_type == 'BIN':
            with open(path, 'rb') as load_bin:
                file_load = load_bin.read()

        # load format zip
        elif input_type == 'ZIP':
            with open(path, 'rb') as load_txt_compress:
                file_load = zlib.decompress(load_txt_compress.read())

    # message d'erreur
    except:
        print('Error : savefile_type and input are not same')

    return eval(file_load)

# -----------------------------------------------------------------------------------------------------------------------