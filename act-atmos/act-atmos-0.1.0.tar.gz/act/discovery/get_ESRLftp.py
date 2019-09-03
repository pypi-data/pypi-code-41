import urllib

def download(category='meteorology', parameter=None, meas_type='in-situ',
             frequency=None, site=None, year=None):
    """
    Function for working with the CropScape API to get a crop type based on

    Parameters
    ----------
    category : str
        Corresponds to category field in the ftp data finder

    Returns
    -------
    category : string
        String of the crop type at that specific lat/lon for the given year

    """


    if frequency is None or site is None or year is None:
        return

    # Build up the URL
    base_url = 'ftp://aftp.cmdl.noaa.gov/data'
    url = '/'.join([base_url,category,meas_type,site,year])

