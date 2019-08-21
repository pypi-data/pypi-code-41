import logging
import subprocess
import os


def tbShaclValidate(data_file, shape_file=None, shacl_validate=None):
    """
    Run the TopBraid SHACL validation tool.

    Args:
        data_file: path to data file in turtle format.
        shape_file: path to shape file in turtle format, defaults to data_file if not specified.
        shacl_validate: path to the shaclvalidate.sh script or equivalent. Derived from SHACLROOT if not specified.

    Returns: (captured stdout, captured stderr)

    """
    if shacl_validate is None:
        try:
            shacl_validate = os.path.expanduser(os.path.join(os.environ["SHACLROOT"], "shaclvalidate.sh"))
        except KeyError as e:
            logging.error("Environment variable SHACLROOT must point to the folder containing shaclvalidate.sh")
            return None,None
    args = [shacl_validate, "-datafile", data_file]
    if shape_file is not None:
        args.append("-shapesfile")
        args.append(shape_file)
    completed = subprocess.run(args,capture_output=True)
    logging.debug("ARGS=" + str(completed.args))
    return completed.stdout, completed.stderr


