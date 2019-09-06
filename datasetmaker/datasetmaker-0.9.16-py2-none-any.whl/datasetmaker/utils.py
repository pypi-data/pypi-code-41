import os
import shutil
import pathlib
from collections.abc import MutableMapping
import pandas as pd
import ddf_utils
from ddf_utils import package
from ddf_utils.io import dump_json
import requests
from datasetmaker.path import DDF_DIR
from .exceptions import CountryNotFoundException
from .indicator import read_concepts


def mkdir(path, rm_if_exists=False):
    """
    Create a directory.

    Parameters
    ----------
    path : str or Path, path to directory.
    rm_if_exists : bool, remove existing directory if it exists.
    """
    if os.path.exists(path):
        if rm_if_exists:
            shutil.rmtree(path)
    else:
        os.mkdir(path)
    return path


def ddfify(path, **kwargs):
    kwargs['status'] = kwargs.get('status', 'draft')
    kwargs['title'] = kwargs.get('title', kwargs.get('name'))
    kwargs['topics'] = kwargs.get('topics', [])
    kwargs['default_measure'] = kwargs.get('default_measure', '')
    kwargs['default_primary_key'] = '--'.join(sorted(kwargs.get('default_primary_key', [])))
    kwargs['author'] = kwargs.get('author', 'Datastory')
    meta = package.create_datapackage(path, **kwargs)
    dump_json(os.path.join(path, "datapackage.json"), meta)


def pluck(seq, name):
    """
    Extracts a list of property values from list of dicts

    Parameters
    ----------
    seq : sequence, sequence to pluck values from.
    name : str, key name to pluck.
    """
    return [x[name] for x in seq]


def flatten(seq):
    """
    Perform shallow flattening operation (one level) of seq

    Parameters
    ----------
    items : sequence, the sequence to flatten.
    """
    out = []
    for item in seq:
        for subitem in item:
            out.append(subitem)
    return out


def add_entity_to_package(package_path, entity_name):
    """
    Convenience function to add ad hoc entities to existing packages

    Parameters
    ----------
    package_path : str or pathlib.Path, path to existing data package.
    entity_name : str, name of entity in question.
    """

    package_concepts_path = os.path.join(package_path, 'ddf--concepts.csv')
    package_concepts = pd.read_csv(package_concepts_path)
    if package_concepts.concept.str.contains(entity_name).any():
        return
    ontology_concepts = read_concepts()
    ontology_concept = ontology_concepts.loc[
        ontology_concepts.concept == entity_name]
    if ontology_concept.empty:
        raise ValueError('Entity does not exist in ontology')
    package_concepts = package_concepts.append(ontology_concept, sort=True)
    package_concepts.to_csv(package_concepts_path, index=False)
    entity_path = pathlib.Path(DDF_DIR) / f'ddf--entities--{entity_name}.csv'
    entity_frame = pd.read_csv(entity_path, sep=',')
    entity_frame.to_csv(os.path.join(package_path,
                                     f'ddf--entities--{entity_name}.csv'),
                        index=False)
    meta = ddf_utils.package.create_datapackage(package_path)
    ddf_utils.io.dump_json(os.path.join(
        package_path, "datapackage.json"), meta)


class CountryDict(MutableMapping):
    def __init__(self, data={}):
        self.mapping = {}
        self.update({k.lower(): v for k, v in data.items()})

    def __getitem__(self, key):
        if type(key) is float:  # NaN
            return None
        if not key.lower() in self.mapping:
            self.__missing__(key)
        return self.mapping[key.lower()]

    def __delitem__(self, key):
        del self.mapping[key.lower()]

    def __setitem__(self, key, value):
        self.mapping[key.lower()] = value

    def __missing__(self, key):
        raise CountryNotFoundException(f'Country {key} not found')

    def __call__(self, key):
        return self.__getitem__(key)

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return str(self.mapping)


class SDMXHandler:
    """
    Requesting and transforming SDMX-json data.

    Parameters
    ----------
    dataset : str, dataset identifier
    loc : list, list of countries
    subject : list, list of subjects

    Examples
    --------

    >>> sdmx = SDMXHandler('CSPCUBE', ['AUS', 'AUT'], ['FDINDEX_T1G'])
    >>> sdmx.data
    [{'Value': 0.0,
    'Year': '1997',
    'Subject': 'FDINDEX_T1G',
    'Country': 'AUT',
    'Time Format': 'P1Y',
    'Unit': 'IDX',
    'Unit multiplier': '0'}]
    """

    # TODO: URL should not be hardcoded
    base_url = "https://stats.oecd.org/sdmx-json/data"

    def __init__(self, dataset, loc=[], subject=[], **kwargs):
        loc = "+".join(loc)
        subject = "+".join(subject)
        filters = f"/{subject}.{loc}" if loc or subject else ''
        url = f"{self.base_url}/{dataset}{filters}/all"
        r = requests.get(url, params=kwargs)
        self.resp = r.json()

    def _map_dataset_key(self, key):
        key = [int(x) for x in key.split(":")]
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(key, self.dimensions)}

    def _map_attributes(self, attrs):
        attrs = [x for x in attrs if x is not None]
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(attrs, self.attributes)}

    @property
    def periods(self):
        return self.resp["structure"]["dimensions"]["observation"][0]

    @property
    def dimensions(self):
        return self.resp["structure"]["dimensions"]["series"]

    @property
    def attributes(self):
        return self.resp["structure"]["attributes"]["series"]

    @property
    def data(self):
        observations = []
        for key, unit in self.resp["dataSets"][0]["series"].items():
            dimensions = self._map_dataset_key(key)
            attributes = self._map_attributes(unit["attributes"])
            z = zip(self.periods["values"], unit["observations"].items())
            for period, (_, observation) in z:
                data = {"Value": observation[0]}
                data[self.periods["name"]] = period["id"]
                data.update(dimensions)
                data.update(attributes)
                observations.append(data)
        return observations
