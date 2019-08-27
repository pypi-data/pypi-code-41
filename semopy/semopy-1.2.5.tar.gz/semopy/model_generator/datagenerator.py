'''The module contains methods for generating a data for a given model.'''

from .utils import get_tuple_index, ThreadsManager
from numpy.random import normal
from functools import partial
from pandas import DataFrame
import numpy as np


DEFAULT_NORMAL = partial(normal, 0, 1)
DEFAULT_ERROR = partial(normal, 0, np.sqrt(0.1))


def generate_data(mpart: dict, spart: dict, mpart_params: dict,
                  spart_params: dict, num_rows: int,
                  threads: ThreadsManager,
                  generator=DEFAULT_NORMAL,
                  error_generator=DEFAULT_ERROR,
                  exo_override=False):
    '''Generates a datasample given the model and it's parameters.
    
    Keyword arguments:
        mpart           -- A measurement part.
        
        spart           -- A structural part.
        
        params_mpart    -- Measurement part parameters.
        
        params_spart    -- Structural part parameters.
        
        num_rows        -- Number of samples in a dataset to be generated.
        
        threads         -- An auxilary object produced by generate_structural_part.
        
                           
        generator       -- A function f(shape) that is used to randomly generate
                           data.
                           
        error_generator -- A function f(shape) that is used to randomly generate
                           errors for data.

                           
    Returns:
        
        A dataframe table.
    '''
    latents = set(mpart.keys())
    indicators = {ind for lv in latents for ind in mpart[lv]}
    out_arrows = {mf for v in spart for mf in spart[v]}
    in_arrows = {v for v in spart}
    exogenous = out_arrows - in_arrows
    spart_vars = in_arrows | out_arrows
    variables = indicators | spart_vars
    if threads is None:
        threads = ThreadsManager()
        threads.load_from_dict(spart, True)
    threads.load_from_dict(mpart)
    data = DataFrame(0.0, index=range(num_rows),
                     columns=sorted(list(variables)))
    exo_it = iter(exogenous)
    if exo_override is not None:
        if type(exo_override) != np.array:
            exo_override = exo_override.values
        k = max(0, num_rows - exo_override.shape[0])
        for i, v in zip(range(exo_override.shape[1]), exo_it):
            if k:
                col = np.append(exo_override[:, i], generator([k]))
            else:
                col = exo_override[:num_rows, i]
            data[v] = col
    for v in exo_it:
        data[v] = generator([num_rows])
    data_copy = data.copy()
    for v in exogenous:
        data_ref = data_copy.copy()
        it = iter(threads.get_confluent_path(v))
        prev = next(it)
        for nodes in it:
            visited = set()
            for a, b in zip(nodes, prev):
                if (a, b) not in visited and a is not None:
                    if a not in indicators:
                        p = spart_params[a]
                        i = get_tuple_index(p, 0, b)
                    else:
                        p = mpart_params[b]
                        i = get_tuple_index(p, 0, a)
                    mult = p[i][1]
                    t = mult * data_ref[b]
                    data_ref[a] += t
                    data[a] += t
                visited.add((a, b))
            prev = nodes
    for v in variables:
        data[v] += error_generator([num_rows])
    return data.drop(latents, 1)