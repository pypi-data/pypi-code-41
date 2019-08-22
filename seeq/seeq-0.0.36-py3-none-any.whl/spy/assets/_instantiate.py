from types import ModuleType

import pandas as pd

from ._model import _AssetBase


def instantiate(model, metadata):
    return pd.DataFrame(_instantiate(model, metadata))


def _instantiate(model, metadata):
    results = list()

    if isinstance(model, ModuleType):
        if 'Instance Path' not in metadata or 'Instance Asset' not in metadata or 'Instance Template' not in metadata:
            raise RuntimeError('"Instance Path", "Instance Asset", "Instance Template" are required columns')
        unique_assets = metadata[['Instance Path', 'Instance Asset', 'Instance Template']].drop_duplicates().dropna()
    elif issubclass(model, _AssetBase):
        if 'Instance Path' not in metadata or 'Instance Asset' not in metadata:
            raise RuntimeError('"Instance Path", "Instance Asset" are required columns')
        if 'Instance Template' in metadata:
            raise RuntimeError('"Instance Template" not allowed when "model" parameter is Asset/Mixin class '
                               'declaration')
        unique_assets = metadata[['Instance Path', 'Instance Asset']].drop_duplicates().dropna()
    else:
        raise RuntimeError('"model" parameter must be a Python module (with Assets/Mixins) or an Asset/Mixin class '
                           'declaration')

    for index, row in unique_assets.iterrows():
        if isinstance(model, ModuleType):
            template = getattr(model, row['Instance Template'].replace(' ', '_'))
        else:
            template = model

        instance = template({
            'Name': row['Instance Asset'],
            'Asset': row['Instance Asset'],
            'Path': row['Instance Path']
        })

        instance_metadata = metadata[(metadata['Instance Asset'] == row['Instance Asset']) &
                                     (metadata['Instance Path'] == row['Instance Path'])]

        results.extend(instance.build(instance_metadata))

    return results
