def sync(annex_dir='./'):
    """Sync the SurrogateModeling annex to Zenodo

    This function first searches for any changes in the data files; if there are any, a new version
    is created on Zenodo, and the relevant files are uploaded, deleted, etc.  It then collects the
    Zenodo metadata (author list, related identifiers, etc.) from zenodo_metadata.json, along with
    the description to be placed on the Zenodo from zenodo_description.html.  These changes are made
    to the Zenodo record, whether the existing record (if no files changed) or the new record (if
    files changed).

    Note that 

    Parameters
    ----------
    annex_dir: str, optional [defaults to './']
        Absolute or relative path to base directory of SurrogateModeling annex with data files.

    """
    import json
