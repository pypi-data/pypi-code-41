#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Program entry point."""

#
# Copyright (c) 2019 Jürgen Mülbert. All rights reserved.
#
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#
# Lizenziert unter der EUPL, Version 1.2 oder - sobald
#  diese von der Europäischen Kommission genehmigt wurden -
# Folgeversionen der EUPL ("Lizenz");
# Sie dürfen dieses Werk ausschließlich gemäß
# dieser Lizenz nutzen.
# Eine Kopie der Lizenz finden Sie hier:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Sofern nicht durch anwendbare Rechtsvorschriften
# gefordert oder in schriftlicher Form vereinbart, wird
# die unter der Lizenz verbreitete Software "so wie sie
# ist", OHNE JEGLICHE GEWÄHRLEISTUNG ODER BEDINGUNGEN -
# ausdrücklich oder stillschweigend - verbreitet.
# Die sprachspezifischen Genehmigungen und Beschränkungen
# unter der Lizenz sind dem Lizenztext zu entnehmen.
#

import argparse
from pathlib import Path
import configparser
import os  # noqa: E402
import logging
import logging.config

from .openorders import cleanoutputdir
from .openorders import getserviceperson
from .openorders import getdata
from .openorders import generateorders


def main():
    """Program entry point."""

    logging.config.fileConfig('logging.conf')
    # logger = logging.getLogger(__name__)

    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'DataPath': 'InputPath',
        'OutPath': 'OutputPath',
        'PersonFile': 'Person',
        'DataFile': 'Data'
    }

    config['DEBUG'] = {
        'LogFile': 'JMOpenOrders.log',
        'Level': 'INFO'
    }

    inifile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jmopenorders.ini')
    if Path(inifile).exists():
        logging.debug('Read existing config file: %s', inifile)
        config.read(inifile)

    else:
        logging.debug('Create new config file: %s', inifile)
        with open(inifile, 'w') as configfile:
            config.write(configfile)

    parser = argparse.ArgumentParser()
    parser.add_argument('--personfile', type=str, help="The File with the Service Persons")
    parser.add_argument('--datafile', type=str, help="The File with the Data")
    parser.add_argument('--datapath', type=str, help="The Path to the Data File")
    parser.add_argument('--outpath', type=str, help="The Directory for the Excel-Files")

    args = parser.parse_args()

    settings_change = False

    if args.personfile is None:
        logging.debug("take Personfile from configfile to: %s", config['DEFAULT']['PersonFile'])
    else:
        settings_change = True
        logging.debug("set new config for Personfile from args['personfile'] = %s", args.personfile)
        config['DEFAULT']['PersonFile'] = args.personfile

    if args.datafile is None:
        logging.debug("take Datafile from configfile to: %s", config['DEFAULT']['DataFile'])
    else:
        settings_change = True
        logging.debug("set new config for Datafile from args['datafile']  = %s", args.datafile)
        config['DEFAULT']['DataFile'] = args.datafile

    if args.datapath is None:
        logging.debug("take DataPath from configfile to: %s", config['DEFAULT']['DataPath'])
    else:
        settings_change = True
        logging.debug("set new config for Datapath from args[datapath]= %s", args.datapath)
        config['DEFAULT']['DataPath'] = args.datapath

    if args.outpath is None:
        logging.debug('take OutputPath from configfile to: %s', config['DEFAULT']['OutPath'])
    else:
        settings_change = True
        logging.debug("st new config for Output Path from args[OutPath]= %s", args.outpath)
        config['DEFAULT']['OutPath'] = args.outpath

    if settings_change is True:
        logging.debug('Write changes to config file: %s', inifile)
        with open(inifile, 'w') as configfile:
            config.write(configfile)

    logging.basicConfig(filename=config['DEBUG']['logfile'], level=logging.DEBUG)

    personfile = os.path.join(os.path.abspath(config['DEFAULT']['DataPath']), config['DEFAULT']['PersonFile'])
    logging.debug('Personfile= %s', personfile)
    names = getserviceperson.GetServicePerson(personfile)
    berater = names.get()

    datafile = os.path.join(os.path.abspath(config['DEFAULT']['DataPath']), config['DEFAULT']['DataFile'])
    data = getdata.GetData(datafile)
    orders = data.get()

    cleanoutputdir.CleanOutputDir(config['DEFAULT']['OutPath'])

    for actual_berater in berater:
        print("actual_berater: " + actual_berater)
        berater_name = actual_berater
        print("Berater Name: " + berater_name)
        create_table = generateorders.GenerateOrders(config['DEFAULT']['OutPath'])
        create_table.create(actual_name=berater_name, actual_content=orders)


if __name__ == "__main__":

    main()
