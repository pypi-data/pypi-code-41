import click
import logging
import os
os.makedirs(os.path.join(os.path.expanduser("~"), '.cnvrg'), exist_ok=True)
logging.basicConfig(filename=os.path.join(os.path.expanduser("~"), '.cnvrg', 'cnvrg.log'), filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def log_message(message, *args, **kwargs):
    click.secho(message, *args, **kwargs)
    logging.info(message)

def log_error(exception: Exception):
    logging.exception(exception)