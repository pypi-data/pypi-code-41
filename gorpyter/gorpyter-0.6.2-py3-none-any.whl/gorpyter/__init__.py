"""
Please refer to the documentation provided in the README.md,
which can be found at gorpyter's PyPI URL: https://pypi.org/project/gorpyter/
"""

name = "gorpyter"

import os
import platform

import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import pandas2ri

import pandas as pd
# import databricks.koalas as ks


def setup():
    """Verify your Python and R dependencies, and attempt to install them."""
    print("""
        CHECKLIST
        =============================================
    """)

    # python version
    py_v_str = platform.python_version()
    py_v_str_chop = py_v_str[:3]
    py_v_fl = float(py_v_str_chop)
    if py_v_fl < 3.7:
        print("\u0009\u2717 ERROR: this package recommends Python 3.7 or higher, but your Jupyter Python environment is '" + py_v_str + "'.")
    elif py_v_fl >= 3.7:
        print("\u0009\u2713 -- The version of your Jupyter Python environment is '" + py_v_str + "'.")        

    # r environment
    try:
        os.environ['R_HOME']
    except:
        print("""
            \u2717 ERROR: The default Jupyter/Conda path for R, `os.environ['R_HOME']` is undefined, cannot print it's path.
            This should have been set when running the Docker image like so:
            `-e R_HOME=/opt/conda/lib/R`
        """)
        try:
            print("\u0009Attempting to set `os.environ['R_HOME']` manually...")
            os.environ['R_HOME'] = '/opt/conda/lib/R'
        except:
            print("\u0009Failed to set `R_HOME` this must not be a conda managed jupyter environment with both R and Python kernels.")
        else:
            print("\u0009\u2713 -- 'R_HOME' is now `" + os.environ['R_HOME'] + "`." ) 
    else:
        print("\u0009\u2713 -- The path of the Jupyter R enviroment being accessed by `rpy2` is '" + os.environ['R_HOME'] + "'.\n") 
    
    # python dependencies
    try:
        import rpy2, tzlocal, pandas, numpy #, databricks.koalas, tzlocal, pyspark
    except:
        print("""
            \u2717 ERROR: this package requires the following python packages:
            [rpy2, pandas, numpy,]
        """)
    else:
        print("\u0009\u2713 -- The Python dependencies of `gorpyter` are installed.") 


    # r dependencies... a few different variables and messages so checking them separately.
    import rpy2.robjects.packages as rpackages # not sure why defining at top of file outside this func is not working...
    utils = rpackages.importr('utils')
    from rpy2.rinterface import (NULL)

    # r tidyverse
    if rpackages.isinstalled('tidyverse'):
        print("\u0009\u2713 -- The `tidyverse` R library is installed in your R environment.")
    else:
        print("\u0009\u2717 ERROR: did not find `tidyverse` R library in your R environment.")
        try:
            utils.chooseCRANmirror(ind=1)
            print("""
                Attempting to install Tidyverse R package (aka ecosystem)...
                This may take between 1 second and 10 minutes...
                Check your console output to see install progress...
            """)
            utils.install_packages('tidyverse')
        except:
            print("\u0009\u2717 ERROR: failed to install `tidyverse` R library.")
        else:
            print("\u0009\u2713 -- successfully installed `tidyverse` R library.")

    # r gorr
    if rpackages.isinstalled('gorr'):
        print("\u0009\u2713 -- The `gorr` R library is installed in your R environment.")
    else:
        print("\u0009\u2717 ERROR: did not find `gorr` R library in your R environment.")
        try:
            print("\u0009Attempting to install gorr R package...")
            utils.install_packages("https://cdn.nextcode.com/public/libraries/gorr_0.2.5.tar.gz", repos = NULL, type = "source")
        except:
            print("\u0009\u2717 ERROR: failed to install `gorr` R library.")
        else:
            print("\u0009\u2713 -- successfully installed `gorr` R library.")

    # access the r dependencies
    try:
        rpackages.importr('gorr')
    except:
        print("\u2717 ERROR: Python cannot access 'gorr' R library package.")
    else:
        print("\u0009\u2713 -- Python was able to successfully load `gorr` as a module via `rpy2`.")

    print("""
        =============================================
    """)


def connect(project, api_key):
    """
        Authenticate with your WXNC instance gateway. 
        - Project is the `internal_project` name found in /csa/projects in CSA instance. 
        - API key can be found at /api-key-service/token in CSA instance.
        - Use `conn = gp.connect(project, api_key)` to feed con into the `gp.query(query, conn)` function.
    """
    r_gorr = rpackages.importr('gorr')
    
    conn = r_gorr.gor_connect(api_key=api_key, project=project)
    return conn


def query(query, conn):
    """
        Run a GOR query.
        - Returns results as a pandas data frame.
        - 2nd argument is the connection object created by connect().
    """
    r_gorr = rpackages.importr('gorr')
    
    # Run the query and return results as a R data frame.
    df = r_gorr.gor_query(query=query, conn=conn, parse=True)
    
    # Convert that R data frame to a pandas data frame.
    with localconverter(robjects.default_converter + pandas2ri.converter):
        pf = robjects.conversion.rpy2py(df)
    
    """
    # Covert that pandas data frame to a koalas data frame.
    # https://rpy2.github.io/doc/latest/html/pandas.html#interoperability-with-pandas
    # https://databricks.com/blog/2019/04/24/koalas-easy-transition-from-pandas-to-apache-spark.html
    kf = ks.from_pandas(pf)
    """

    return pf