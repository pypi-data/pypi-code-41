import logging
from .imports import get_job_class

logging.basicConfig(
    format='%(asctime)s - DecodeJob v0.01 - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger("Runner")
logger.setLevel(logging.INFO)
logger.info("Finding job.py...")


def run():
    JobClass = get_job_class(logger)
    job = JobClass("s3", logger)
    job.run()