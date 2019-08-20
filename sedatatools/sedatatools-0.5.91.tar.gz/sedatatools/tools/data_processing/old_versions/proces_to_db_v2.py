"""
This script will take .csv data from provided folder in Config file.
1. It will create _FIPS, _NAME, QNAME columns
2. Create empty rows for missing geographies
3. Split tables if they have more than specified numbers of columns (define column numbers in config file!)
4. Create table_names table in db with proper names
"""
import cProfile
import datetime
import io
import multiprocessing as mp
import os
import pstats

import numpy as np
import pandas as pd
import sqlalchemy as sqla
import yaml
from sqlalchemy import create_engine
pd.options.mode.chained_assignment = None
import time
import logging
from sedatatools.tools.connectors import prime
import math
from multiprocessing.dummy import Pool as ThreadPool

start_time = time.time()


def get_sl_from_tableid(sl):
    return sl[:sl.index('_')]


def create_db(config):
    engine = create_engine_for_db('master')
    connection = engine.connect()
    try:
        query = 'CREATE DATABASE {} ON ( NAME = Sales_dat, FILENAME="X:\MSSQL_Data\{}.mdf") LOG ON ( NAME = Sales_log, FILENAME="X:\MSSQL_Data\{}_log.mdf");'
        query = query.format(
            config['dbname'], config['dbname'], config['dbname'],
        )
        connection.execute(query)

    except ConnectionError as ce:
        logging.warning(ce)

    except sqla.exc.ProgrammingError:
        logging.info('Database already exists')


def create_engine_for_db(db_name):
    prime_conf = prime.Prime()
    user_name = prime_conf.user_name
    password = prime_conf.password

    engine = create_engine(
        f'mssql+pyodbc://{user_name}:{password}@PRIME/{db_name}?driver=ODBC+Driver+11+for+SQL+Server', connect_args={'autocommit': True},
    )

    return engine


def parse_args():
    pass


def load_config_file(config_file_path):
    config_file_path = "config.yml"
    with open(config_file_path, 'r') as f:
        try:
            config = yaml.load(f)
        except yaml.YAMLError as ex:
            logging.warning(ex)
    return config


def verify_config_file(config_file_path):
    errors = []
    warnings = []

    if not os.path.isfile(config_file_path):
        logging.warning(
            "Error: Config file doesn't exist on selected location: " + config_file_path + " !",
        )
        return False

    config = load_config_file(config_file_path)
    if len(config['connectionString']) == 0 or 'connectionString' not in config.keys():
        errors.append(
            'Error: Connection string not set properly in config file!',
        )
    if len(config['projectName']) == 0 or 'projectName' not in config.keys():
        errors.append('Error: Project name not set properly in config file!')
    if len(config['projectId']) == 0 or 'projectId' not in config.keys():
        errors.append('Error: Project id not set properly in config file!')
    if type(config['projectDate']) is not datetime.date or 'projectDate' not in config.keys():
        errors.append('Error: Project date not set properly in config file!')
    if len(config['dbname']) == 0 or 'dbname' not in config.keys():
        errors.append('Error: Database name not set properly in config file!')
    if len(config['server']) == 0 or 'server' not in config.keys():
        errors.append('Error: Server name not set properly in config file!')
    if len(config['user']) == 0 or 'user' not in config.keys():
        errors.append('Error: User name not set properly in config file!')
    if len(str(config['projectYear'])) != 4 or 'projectYear' not in config.keys():
        errors.append('Error: Project year not set properly in config file!')
    if config['projectYear'] > datetime.datetime.now().year:
        warnings.append('Warning: Project year is set in future.')
    if (not (
        os.path.isfile(config['variableDescriptionLocation']) or os.path.isdir(
            config['variableDescriptionLocation'],
        )
    )):
        errors.append('Error: Something is wrong with variable info location!')

    for warn in warnings:
        logging.warning(warn)

    if len(errors) == 0:
        return True

    else:
        for err in errors:
            logging.warning(err)
        return False


def get_file_names_list(config):
    """
    This function will check if there is files list (fl.txt) file with defined order for table input.
    If there is no defined order, read data from source file by regular order
    :param config: Configuration file
    :return:
    """

    if os.path.basename(config['fileNamesList']) == '':
        logging.warning(
            'There is no files list defined, reading files from Source directory',
        )

        if not os.path.isdir(config['sourceDirectory']):
            logging.warning(
                "Error: Source file doesn't exist on selected location: " + config['sourceDirectory'] + " !",
            )
            return False

        items = os.listdir(config['sourceDirectory'])
        files_list = []

        for item in items:
            if item.endswith('csv'):
                files_list.append(os.path.join(
                    config['sourceDirectory'], item,
                ))

        if not files_list:
            logging.warning('Folder is empty!')
        else:
            return files_list

    else:
        with open(config['fileNamesList'], 'r') as filter:
            list = filter.readlines()
            file_names_list = [line.rstrip('\n') for line in list]

        if not os.path.isdir(config['sourceDirectory']):
            logging.warning(
                "Error: Source file doesn't exist on selected location: " + config['sourceDirectory'] + " !",
            )
            return False

        files_list = []

        for item in file_names_list:
            if item.endswith('csv'):
                files_list.append(os.path.join(
                    config['sourceDirectory'], item,
                ))

        if not files_list:
            logging.warning('Folder is empty!')
        else:
            return files_list


def capitalize_level_names(geo_level):
    """
    This function returns list of geo names capitalized (NATION, COUNTY...)
    :param geo_level:
    :return: List of geo level names capitalized
    """
    geo_names_cap = []
    chars_for_removal = [
        '(', ')', '&', '/', ',', '.',
        '\\', '\'', '&', '%', '#',
    ]

    for gl in geo_level:
        for ch in chars_for_removal:
            if ch in gl:
                gl = gl.replace(ch, ' ')
        gl = gl.strip()
        while '  ' in gl:
            gl = gl.replace('  ', '')
        if ' ' in gl:
            blank_pos = [i for i, letter in enumerate(gl) if letter == ' ']
            geo_names_cap.append(
                gl[0].upper() + ''.join([gl[i + 1] for i in blank_pos]).upper(),
            )
        else:
            geo_names_cap.append(gl.upper())

    return geo_names_cap


def create_system_columns_fips(table_id, table, config, level_names):
    """
    :param table_id: It is a key from Table holder dictionary... it contains information about sl levels
    :param table: Table contains values from Table holder dictionary.. if key is SL010(sl_level) then table contains
    all data about that level (all geo info and table content to be writen into a db)
    :param config: configuration file
    :param level_names: level names to be capitalized (NATION, STATE...)
    :return: Table that contains all system variables (SL010_FIPS, SL010_NAME, NATION, STATE...)
    """

    geo_level_info = config['geoLevelInfo']
    names = capitalize_level_names(level_names)
    sl_level = get_sl_from_tableid(table_id)
    for ind, geo_level in enumerate(geo_level_info):
        if (sl_level == 'SL010') & (sl_level == geo_level[0]):
            table[geo_level[0] + '_FIPS'] = '00'
            table[geo_level[0] + '_NAME'] = 'United States'
            table[geo_level[0] + '_FULL_FIPS'] = '00'
            if names[ind] == capitalize_level_names(geo_level_info[ind])[1]:
                table[names[ind]] = '00'
        else:
            if sl_level == geo_level[0]:
                temp_ind = ind
                cut_cum = 0
                for level_index in reversed(range(temp_ind+1)):
                    if level_index+1 <= int(geo_level_info[level_index][4]):
                        continue
                    elif geo_level_info[level_index][0] == 'SL010':
                        table[geo_level_info[level_index][0] + '_FIPS'] = '00'
                        table[
                            geo_level_info[level_index]
                            [0] + '_NAME'
                        ] = 'United States'
                        table[
                            geo_level_info[level_index]
                            [0] + '_FULL_FIPS'
                        ] = '00'
                        table[names[level_index]] = '00'
                    else:
                        if cut_cum == 0:
                            table[
                                geo_level_info[level_index][0] +
                                '_FIPS'
                            ] = table['Geo'].str[-int(geo_level_info[level_index][3]):]
                            table[
                                names[level_index]
                            ] = table['Geo'].str[-int(geo_level_info[level_index][3]):]
                            cut_cum = int(geo_level_info[level_index][3])
                            table[geo_level_info[level_index][0] + '_FULL_FIPS'] = table['Geo'].str[
                                -int(
                                geo_level_info[level_index][2],
                                ):
                            ]
                        else:
                            table[geo_level_info[level_index][0] + '_FIPS'] = table['Geo'].str[
                                -int(
                                geo_level_info[level_index][3],
                                ) - cut_cum:-cut_cum
                            ]
                            table[names[level_index]] = table['Geo'].str[
                                -int(
                                geo_level_info[level_index][3],
                                ) - cut_cum:-cut_cum
                            ]
                            table[
                                geo_level_info[level_index][0] +
                                '_FULL_FIPS'
                            ] = table['Geo'].str[:-cut_cum]
                            cut_cum += int(geo_level_info[level_index][3])
    return table


def create_system_columns_names(table, all_geotypes_and_sumlev, sl_levels):
    """
    Add geo names for sum levels and crate QNames ... SL010_NAME, SL040_NAME.....
    :param table:
    :param all_geotypes_and_sumlev:
    :param sl_levels: list of dictionary keys
    :return:
    """

    sl_levels = [get_sl_from_tableid(sl) for sl in sl_levels]
    for level in sl_levels:
        try:
            table = pd.merge(
                table, all_geotypes_and_sumlev[all_geotypes_and_sumlev['SUMLEV'] == level]
                .drop(['TYPE', 'SUMLEV'], axis=1),
                how='left',
                left_on=[level + '_FULL_FIPS'],
                right_on=['Geo'],
            )
            table.drop(level + '_NAME', axis=1, inplace=True)
            table.rename(
                index=str, columns={'NAME_y': level+'_NAME', 'NAME_x': 'NAME', 'Geo_x': 'Geo'},
                inplace=True,
            )
        except KeyError:
            continue

    cols_to_join = [
        tn for tn in table.columns if '_NAME' in tn and tn != 'SL010_NAME'
    ]

    for col in reversed(cols_to_join):
        if table[col].isnull().any():
            continue
        else:
            table['QName'] = table['QName'] + ', ' + table[col]

    table['QName'] = table['QName'].str[2:]
    return table


def write_table_names(table_info, config, engine):

    connection = engine.connect()

    table_names_content = []

    for name in table_info:
        code_name = [n[6:] for n in list(name[1])]
        unique_names = np.unique(code_name)
        for cn in unique_names:
            table_names_content.append(
                [os.path.basename(name[0]), cn, config['projectYear']],
            )
        table_names = pd.DataFrame(
            table_names_content, columns=[
            'descName', 'code_Name', 'projectYear',
            ],
        )
    try:
        table_names.to_sql('table_names', connection, index=False)
    except:
        logging.warning("table_names table already exists.")


def create_table_id(sumlev, suffix_width, sub_counter, table_counter):
    """
    This function is used while splitting table if table is larger than defined, and returns suffix of tables as str.  SL010_001...SL010_001001
    :param sumlev: Summary level
    :param suffix_width: defined suffix width, in this example 3 characters
    :param sub_counter: counter if table was splitted into smaller tables
    :param table_counter: counter if table is not splitted
    :return:
    """

    if sub_counter == 0:
        additional_nulls = ''.join(
            ['0' for _ in range(suffix_width - len(str(table_counter)))],
        )
        return sumlev + '_' + additional_nulls + str(table_counter)
    else:
        additional_nulls_sub = ''.join(
            ['0' for _ in range(suffix_width - len(str(sub_counter)))],
        )
        additional_nulls = ''.join(
            ['0' for _ in range(suffix_width - len(str(table_counter)))],
        )
        return sumlev + '_' + additional_nulls + str(table_counter) + additional_nulls_sub + str(sub_counter)


def check_last_table_name_if_exists(engine, config):

    db_table_names = engine.table_names()
    unique_tables = []
    for table in db_table_names:
        table = table.split("_")[-1]
        if table != "geo" and table != "table_names":
            unique_tables.append(table)
    if len(unique_tables) > 0:
        unique_tables = list(set(unique_tables))
        unique_tables.sort()
        table_name = str(unique_tables[-1])
    else:
        table_name = config['tableNumberingStartsFrom']

    return table_name


def merge_geo_data_tables(file_path, config_files):
    """
    The function processes only one file at a time..
    :param file_path: File path to file
    :param config_files: Config file
    :param file_counter: the regular file number to be entered into the database
    :param engine: Connection to database
    :return:
    """
    # Load data
    # Read original tables and all geo types
    # Merge all geo types and tables
    try:
        original_table = pd.read_csv(file_path, dtype={'Geo': 'str'})
        logging.info('Writing table - ' + os.path.basename(file_path))
    except Exception:
        logging.warning('File - ' + file_path + ' - does not exist!')

    all_geotypes_and_sumlev = pd.read_csv(
        os.path.join(
        config_files['configDirectory'], 'all_geotypes_and_sumlev.csv',
        ), dtype={'FIPS': 'str'},
    )
    all_geotypes_and_sumlev = all_geotypes_and_sumlev.rename(columns={
                                                             "FIPS": "Geo",
    })

    if "SUMLEV" in original_table.columns:
        geotypes_org_tables_merged = pd.merge(
            all_geotypes_and_sumlev, original_table, how='left', on=['SUMLEV', 'Geo'],
        )
    else:
        geotypes_org_tables_merged = pd.merge(
            all_geotypes_and_sumlev, original_table, how='left', on='Geo',
        )

    # TODO: add test to check if merge is done properly

    return all_geotypes_and_sumlev, geotypes_org_tables_merged


def create_table(file_path, config_files, file_counter, engine):
    # Select list of geo levels from config file
    geo_level_info = config_files['geoLevelInfo']

    all_geotypes_and_sumlev, geotypes_org_tables_merged = merge_geo_data_tables(
        file_path, config_files,
    )
    # Create list of sumlevs
    sumlev_ids = [k[0] for k in geo_level_info]

    # Place holder for system column names, this will be populated later
    for k in sumlev_ids:
        geotypes_org_tables_merged[k + "_FIPS"] = None
        geotypes_org_tables_merged[k + "_NAME"] = None
        geotypes_org_tables_merged['QName'] = ''

    # Capitalize sum level names
    geo_level_names = [k[1] for k in geo_level_info]
    geo_names_cap = capitalize_level_names(geo_level_names)
    for name in geo_names_cap:
        geotypes_org_tables_merged[name] = None

       # Check if table size is larger than defined number of columns, and split it if required
    table_holder = {}
    table_counter = file_counter

    # ToDo: For table size larger than defined, split columns proprerly - at this time this function doesn't split tables properly... check function again and speed it up!

    for sumlev in sumlev_ids:
        loaded_table = geotypes_org_tables_merged[geotypes_org_tables_merged['SUMLEV'] == sumlev]

        system_columns = ['Geo', 'SUMLEV', 'TYPE', 'NAME', 'QName'] + [
            sl +
            '_FIPS' for sl in sumlev_ids
        ] + [sl + '_NAME' for sl in sumlev_ids] + geo_names_cap
        column_prefix = config_files['projectId'] + '_' + str(table_counter).zfill(
            3,
        ) + '_' if config_files['projectId'] != '' else ''
        data_columns = [
            column_prefix + c for c in loaded_table.columns if c not in system_columns
        ]

        if len(data_columns) > config_files['maxTableWidth']:
            splitted_columns = []
            sub_table_counter = 1

            for ind, column in enumerate(data_columns, 1):
                if (len(data_columns)-ind) < config_files['maxTableWidth']:
                    if (len(splitted_columns) < config_files['maxTableWidth']) & (len(data_columns)-ind == 0):
                        splitted_columns.append(column)
                        table_holder[create_table_id(
                            sumlev, 3, sub_table_counter, table_counter,
                        )] = loaded_table[system_columns + splitted_columns]
                        break
                    elif len(splitted_columns) < config_files['maxTableWidth']:
                        splitted_columns.append(column)
                    elif len(splitted_columns) == config_files['maxTableWidth']:
                        table_holder[create_table_id(
                            sumlev, 3, sub_table_counter, table_counter,
                        )] = loaded_table[system_columns + splitted_columns]
                        splitted_columns = []
                        sub_table_counter += 1
                        splitted_columns.append(column)
                    else:
                        table_holder[create_table_id(
                            sumlev, 3, sub_table_counter, table_counter,
                        )] = loaded_table[system_columns + splitted_columns]
                        splitted_columns = []
                        sub_table_counter += 1

                elif ind % config_files['maxTableWidth'] != 0:
                    splitted_columns.append(column)
                else:
                    splitted_columns.append(column)
                    table_holder[create_table_id(
                        sumlev, 3, sub_table_counter, table_counter,
                    )] = loaded_table[system_columns + splitted_columns]
                    splitted_columns = []
                    sub_table_counter += 1
        else:
            table_holder[create_table_id(
                sumlev, 3, 0, table_counter,
            )] = loaded_table

    # for each sum level create table with system columns - _FIPS & _NAMES
    connection = engine.connect()

    for table_id, table in table_holder.items():
        try:
            table.columns = [
                column_prefix+c if c not in system_columns else c for c in table.columns
            ]
            table_holder[table_id] = create_system_columns_fips(
                table_id, table, config_files, geo_level_names,
            )
            table_holder[table_id] = create_system_columns_names(
                table, all_geotypes_and_sumlev, table_holder.keys(),
            )
            table_holder[table_id].drop(
                list(table_holder[table_id].filter(regex='_FULL_FIPS')), axis=1, inplace=True,
            )
            table_holder[table_id].drop(['Geo_y'], axis=1, inplace=True)
            if (table_holder[table_id]['QName'] == '').all():
                table_holder[table_id]['QName'] = 'United States'
            prefix_to_table = config_files['projectId'] + \
                '_' if config_files['projectId'] != '' else ''
            table_holder[table_id].to_sql(
                prefix_to_table + table_id, connection, index=False,
            )
            logging.info(prefix_to_table + table_id+' written to sql.')
        except ValueError:
            connection.execute("DROP TABLE " + prefix_to_table + table_id)
            table_holder[table_id].to_sql(
                prefix_to_table+table_id, connection, index=False,
            )
            logging.info(prefix_to_table+table_id+' written to sql.')

    logging.info("--- %s seconds ---" % (time.time() - start_time),)
    return [file_path, table_holder.keys()]


def process_data(configuration):
    files_list = get_file_names_list(configuration)

    table_names_info = []
    # create_db(configuration)
    engine = create_engine_for_db(configuration['dbname'])

    file_counter = 1

    for file_path in files_list:
        table_names_info.append(create_table(
            file_path, configuration, file_counter, engine,
        ))
        file_counter += 1

    write_table_names(table_names_info, configuration, engine)


def get_primary_keys_dict(config):

    geo_level_info = config['geoLevelInfo']
    primarykeys = {}

    for geo_info in reversed(geo_level_info):
        lower_levels = []
        index = geo_level_info.index(geo_info)
        max_ind = geo_info[4]
        for ind in reversed(range(index)):
            if geo_level_info[ind][4] < max_ind:
                lower_levels.append(geo_level_info[ind][0])
                max_ind = geo_level_info[ind][4]
                if len(lower_levels) > 0 and 'SL010' in lower_levels:
                    lower_levels.remove('SL010')
            else:
                continue
        if len(lower_levels) == 0:
            primarykeys[geo_info[0]] = geo_info[0] + '_FIPS'
        else:
            primarykeys[geo_info[0]] = geo_info[0] + '_FIPS'+',' + \
                ",".join(str(x) + '_FIPS' for x in lower_levels)

    return primarykeys


def set_primary_keys(config):

    engine = create_engine_for_db(config['dbname'])
    connection = engine.connect()
    primarykeys = get_primary_keys_dict(config)

    db_table_names = engine.table_names()
    for table_name in db_table_names:
        if "geo" not in table_name and "table_names" not in table_name:
            split_values = primarykeys[table_name[-9:-4]].split(',')
            for x in split_values:
                try:
                    connection.execute(
                        "ALTER TABLE "+table_name+" ALTER COLUMN "+x+" varchar(max) NOT NULL;",
                    )
                    connection.execute(
                        "ALTER TABLE "+table_name+" ALTER COLUMN "+x+" int NOT NULL;",
                    )
                    connection.execute(
                        "ALTER TABLE "+table_name+" ADD PRIMARY KEY ("+",".join(split_values)+");",
                    )
                except:
                    logging.warning(
                        "Could not execute queries for changing column type and primary key: "+table_name,
                    )


def main():
    # parse commandline arguments
    config_file_path = parse_args()
    config = load_config_file(config_file_path)
    logging.basicConfig(
        filename=config['configDirectory'] +
        'process_to_db_log.log', filemode='w', level=logging.DEBUG,
    )
    create_db(config)
    process_data(config)
    set_primary_keys(config)


if __name__ == '__main__':
    main()
    end_time = time.time()
    hours, rem = divmod(end_time-start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    logging.info("Finished in {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(minutes), seconds,
    ))
