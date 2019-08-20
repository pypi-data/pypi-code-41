# system modules
import logging
import re
import os
import glob
import warnings
import csv
import io
import datetime
import collections
from urllib.parse import urlparse, parse_qsl
import time

# internal modules
import mqttstore
from mqttstore.cli.commands.main import cli
from mqttstore.cli.commands.sqlite.config import (
    Configuration,
    BrokerSectionError,
)
from mqttstore.sqlite import SQLiteDataBase
from mqttstore.queue import StorageQueue

# external modules
import click
import xdgspec

logger = logging.getLogger(__name__)

default_dbfile = os.path.join(
    xdgspec.XDGPackageDirectory("XDG_DATA_HOME", mqttstore.__name__).path,
    "db.sqlite",
)


@cli.command(
    help="Store MQTT data to an SQLite database",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "-c",
    "--config",
    "configfiles",
    help="Add a configuration file to read. "
    "Can be specified multiple times."
    "By default, ",
    type=click.Path(readable=True, exists=False, dir_okay=False),
    multiple=True,
    show_envvar=True,
    show_default=True,
    default=(
        os.path.join(
            xdgspec.XDGPackageDirectory(
                "XDG_CONFIG_HOME", mqttstore.__name__
            ).path,
            "sqlite.conf",
        ),
    ),
)
@click.option(
    "-f",
    "--file",
    "dbfile",
    help="Database file. Overwrites the configuration.",
    show_default=default_dbfile,
    metavar="PATH",
    type=lambda arg: arg if arg is None else click.Path(dir_okay=False)(arg),
)
@click.option(
    "-b",
    "--bundle-interval",
    help="Interval of seconds to use for bundling "
    "incoming datasets before storing. Overwrites the configuration.",
    metavar="SECONDS",
    type=lambda x: x if x is None else click.FloatRange(min=0)(x),
)
@click.option(
    "-t",
    "--time-column",
    help="Name of the column used to store the time. "
    "Overwrites the configuration.",
)
@click.option("-v", "--log-mqtt", help="Show MQTT log messages", is_flag=True)
@click.pass_context
def sqlite(ctx, configfiles, dbfile, bundle_interval, time_column, log_mqtt):
    ctx.ensure_object(dict)

    config = Configuration()
    logger.debug("Reading configuration files {}".format(configfiles))
    config.read(configfiles)

    if "database" not in config:
        config.add_section("database")
    if bundle_interval is not None:
        config["database"]["bundle_interval"] = str(bundle_interval)
    if dbfile is not None:
        config["database"]["file"] = str(dbfile)
    if time_column is not None:
        config["database"]["time_column"] = time_column

    buf = io.StringIO()
    config.write(buf)
    logger.debug("Configuration:\n{}".format(buf.getvalue().strip()))

    storage_queue = StorageQueue()
    storage_queue.bundle_interval = config["database"].getfloat(
        "bundle_interval", 0
    )

    def start_client(client):
        logger.info(
            "Starting MQTT client {client._client_id} connecting to "
            "broker {client._host}:{client._port}...".format(client=client)
        )

        def on_log(client, obj, level, string):
            logger.info(
                "Client {client._client_id} on "
                "{client._host}:{client._port}: {msg}".format(
                    client=client, msg=string
                )
            )

        if log_mqtt:
            client.on_log = on_log
        client.queue = storage_queue
        client.loop_start()
        return client

    try:
        clients = tuple(map(start_client, config.clients))
    except BrokerSectionError as e:
        raise click.ClickException(
            "Error setting up MQTT clients from "
            "configuration: {error}".format(error=e)
        )

    if not clients:
        ctx.fail("No MQTT brokers configured.")

    def close_clients():
        for client in clients:
            logger.debug(
                "disconnecting MQTT client {client._client_id}".format(
                    client=client
                )
            )
            client.disconnect()

    database_file = config["database"].get("file", default_dbfile)
    directory, filename = os.path.split(database_file)
    if not os.path.exists(directory):
        logger.debug("Creating directory {}".format(repr(directory)))
        os.makedirs(directory)
    database = SQLiteDataBase(os.path.expanduser(database_file))

    ctx.call_on_close(close_clients)
    ctx.call_on_close(database.close)

    def store_queued_datasets():
        for dt, instruction in storage_queue.old_datasets:
            logger.debug(
                "Executing storage instruction {}".format(instruction)
            )
            for table_name, data in instruction.items():
                if table_name not in database:
                    database.create_table(
                        table_name,
                        {
                            config["database"].get(
                                "time-column", "time"
                            ): datetime.datetime
                        },
                    )
                table = database.get_table(table_name)
                table.insert(
                    data={
                        **data,
                        **{config["database"].get("time-column", "time"): dt},
                    }
                )

    logger.debug("Looping forever")
    try:
        while True:
            store_queued_datasets()
            time.sleep(max(storage_queue.bundle_interval * 1.5, 0.1))
    except KeyboardInterrupt as e:
        logger.info(
            "Recieved {etype}. "
            "Storing remaining queued datasets, then exit.".format(
                etype=type(e).__name__
            )
        )
        store_queued_datasets()
