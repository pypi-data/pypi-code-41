import importlib
import inspect


def get_job_class(logger):
    try:
        main = importlib.import_module("job")
        for name, obj in inspect.getmembers(main):
            if len(name) > 3 and "Job" == name[-3:]:
                logger.info(
                    f"Found job with name {name} in job.py. Running...")
                return obj
    except Exception as e:
        logger.error(f"Unable to import job.py. Unexpected exception {str(e)}")
