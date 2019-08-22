#!/bin/env python2
# -*- coding: utf-8 -*-

import logging.config
import os
import subprocess
from time import gmtime,strftime
import yaml
from influxdb import InfluxDBClient
from pprint import pprint, pformat
import datetime
import psycopg2
from psycopg2.extras import execute_values
import click
from fdsnextender import FdsnExtender

logger = logging.getLogger(__name__)

def validate_config(cfg):
  """
  Validate configuration
  """
  # Logger file exists and is readable ?

  return True

def dict_dumper(dict):
  try:
    return dict.toJSON()
  except:
    return dict.__dict__


def scan_volume(path):
  """
  Scanne un volume indiqué par son chemin (path).
  La fonction lance une commande "du -d4 path" et analyse chaque ligne renvoyée.
  Elle renvoie une liste de dictionnaires :
  [ {year: 2011, network: 'G', size: '100', files: '14', station: 'STAT', channel: 'BHZ.D'}, ...]
  """
  data = []
  volume = os.path.realpath(path)+'/'
  logger.debug("Volume %s"%(volume))
  # TODO mettre le niveau de profondeur (2) en option
  starttime = datetime.datetime.now()
  lines = subprocess.check_output(["du", "--exclude", ".snapshot", "-d4", volume]).decode("utf-8").splitlines()
  logger.debug("Volume scanned in %s"%(datetime.datetime.now() - starttime))
  for l in lines:
    logger.debug(l)
    (size, path) = l.split('\t')
    # On ne garde que le chemin qui nous intéresse
    path = path.replace(volume,'').split('/')
    # Ne pas considérer le seul chemin de niveau 1
    if len(path) == 4:
      logger.debug(f"path : {path}")
      logger.debug(f"size : {size}")
      (channel, quality) = path[3].split('.')
      data.append({'year': path[0], 'network': path[1], 'station': path[2], 'channel': channel, 'quality': quality, 'size': size})
  return data


def scan_volumes(volumes):
  # volumes is a complex data type :
  # List of dictionaries of 2 elements (path and type)
  # [{path: /bla/bla, type: plop}, {path: /bli/bli, type: plip}]
  # En sortie, une liste de dictionnaires :
  # [ {stat}, {stat}, ]
  volume_stats = []
  for volume in volumes:
    logger.debug("Preparing scan of volume %s", volume['path'])
    starttime = datetime.datetime.now()
    if 'path' in volume:
      stats = scan_volume(volume['path'])
      # On rajoute le type comme un élément de chaque statistique
      if 'type' in volume:
        for s in stats:
          s['type'] = volume['type']
      volume_stats.append(stats)
      # If a type of data was specified, then we add this tag to the stats
    else:
      raise ValueError("Volume has no path key : %s"%(volume))
  # on applati la liste de listes :
  logger.debug("All volumes scanned in %s"%(datetime.datetime.now() - starttime))
  return [ x for vol in volume_stats for x in vol ]


@click.command()
@click.option('--config-file',  'configfile', type=click.File(), help='Configuration file path', envvar='CONFIG_FILE', show_default=True, default=f"{os.path.dirname(os.path.realpath(__file__))}/config.yml")
def cli(configfile):

    try:
      cfg = yaml.load(configfile, Loader=yaml.SafeLoader)
    except Error as e:
      print(f"Error reading file {configfile}")

    validate_config(cfg)
    # At this point we ensure that configuration is sane.

    logger_file = cfg['logger_file']
    if not logger_file.startswith('/'):
      logger_file =  os.path.split(configfile.name)[0]+'/'+logger_file
    logging.config.fileConfig(logger_file)
    logger = logging.getLogger("resif_data_reporter")
    logger.info("Starting")
    statistics = []
    use_cache = False

    # Refresh or use cache ?
    # Try to open data.yaml
    cache_file = cfg['cache_file']
    try:
      if not cache_file.startswith('/'):
        cache_file = os.path.split(configfile.name)[0]+'/'+cache_file
      with open(cache_file, 'r') as ymlfile:
        cache = yaml.load(ymlfile, Loader=yaml.SafeLoader)
      # Compare volumes in cfg and in cache
      if cfg['volumes'] == cache['volumes']:
        # Get previous run data
        previous_run_date = datetime.datetime.strptime(cache['date'], "%Y-%m-%d").date()
        # Compute cache age
        if datetime.date.today() - previous_run_date > datetime.timedelta(days=(cfg['cache_ttl'])):
          logger.info("Cache is old, let's scan volumes")
          statistics = scan_volumes(cfg['volumes'])
        else:
          logger.info("Cache is available, let's be lazy for this time and use it")
          use_cache = True
          statistics = cache['statistics']
    except FileNotFoundError:
      logger.debug("Cache file %s not found, let's scan volumes."%cfg['cache_file'])
      statistics = scan_volumes(cfg['volumes'])

    logger.debug(statistics)
    today = datetime.date.today().strftime("%Y-%m-%d")
    # add the network_type (is the network permanent or not) to the statistic
    # also insert the extended network code.
    extender = FdsnExtender()
    for stat in statistics:
      if stat['network'] in cfg['metadata']['permanent_networks']:
        stat['is_permanent'] = True
      else :
        stat['is_permanent'] = False
        try:
          stat['network'] = extender.extend(stat['network'], int(stat['year']))
        except ValueError:
          logger.warning("Network %s exists ?"%stat['network'])
      stat['date'] = today
      logger.debug(stat)


    # Open dump file and write the stats.
    if use_cache == False:
      try:
        with open(os.path.split(configfile.name)[0]+"/data.yaml", 'w') as outfile:
          yaml.dump({'date': today,
                     'volumes': cfg['volumes'],
                     'statistics': statistics
                    },
                    outfile, default_flow_style=False)
      except:
        logger.error("Error writing data to cache : "+sys.exc_info()[0])


      # Write to postgres database
      if 'postgres' in cfg:
        logger.info('Writing to postgres database')
        conn = psycopg2.connect(dbname=cfg['postgres']['database'], user=cfg['postgres']['user'], host=cfg['postgres']['host'], password=cfg['postgres']['password'], port=cfg['postgres']['port'])
        cur = conn.cursor()
        execute_values(cur,
                     """INSERT INTO datastats (network, year, station, channel, quality, type, size, is_permanent, date) VALUES %s""",
                     statistics,
                     "(%(network)s, %(year)s, %(station)s, %(channel)s, %(quality)s, %(type)s, %(size)s, %(is_permanent)s, %(date)s)")
        conn.commit()

      if 'influxdb' in cfg:
        logger.info('Writing in influxdb')
        influxdb_json_data = []
        # Compose json data
        record_time = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
        for stat in statistics:
          influxdb_json_data.append(
              {"measurement": cfg['influxdb']['measurement'],
               "tags": {
                 "year": int(stat['year']),
                 "network": stat['network'],
                 "station": stat['station'],
                 "channel": stat['channel'],
                 "quality": stat['quality'],
                 "permanent": bool(stat['is_permanent']),
                 "type": stat['type'],
                 "date": stat['date']
               },
               "time": record_time,
               "fields": {
                 "size": int(stat['size'])
               }
          }
          )
        logger.info(pformat(influxdb_json_data))

        # Now, send this data to influxdb
        try:
          logger.info("Sending data to influxdb")

          logger.debug("host     = "+cfg['influxdb']['server'])
          logger.debug("port     = "+str(cfg['influxdb']['port']))
          logger.debug("database = "+cfg['influxdb']['database'])
          logger.debug("username = "+cfg['influxdb']['user'])

          client = InfluxDBClient(host     = cfg['influxdb']['server'],
                                  port     = cfg['influxdb']['port'],
                                  database = cfg['influxdb']['database'],
                                  username = cfg['influxdb']['user'],
                                  password = cfg['influxdb']['password'],
                                  ssl      = cfg['influxdb']['ssl'],
                                  verify_ssl = cfg['influxdb']['verify_ssl']
          )

          client.write_points(influxdb_json_data)
        except Exception as e:
          logger.error("Unexpected error writing data to influxdb")
          logger.error(e)



if __name__ == "__main__":
    main()
