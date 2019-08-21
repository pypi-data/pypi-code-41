import pandas
import numpy
import matplotlib.pyplot as plt
import seaborn as sns
import json

float_types = (float, numpy.float, numpy.float16, numpy.float32, numpy.float64)
int_types = (int, numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64)
bool_types = (bool, numpy.bool_)
collection_types = (dict, list, set, numpy.ndarray)

numeric_types = float_types + int_types
pseudo_numeric_types = float_types + int_types + bool_types

na_values = [
    '', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
    '1.#IND', '1.#QNAN', 'N/A', 'NULL', 'NaN', 'n/a', 'nan', 'null'
]


def get_json_dumpable(data, depth: int = 0, max_depth: int = None):
    if isinstance(data, dict):
        result = {
            __process_value(k, depth=depth, max_depth=max_depth):
                __process_value(v, depth=depth, max_depth=max_depth)
            for k, v in data.items()
        }
    elif isinstance(data, (list, set, numpy.ndarray)):
        result = [
            __process_value(x, depth=depth, max_depth=max_depth) for x in data
        ]
    elif isinstance(data, pseudo_numeric_types):
        if isinstance(data, int_types):
            result = int(data)
        elif isinstance(data, float_types):
            result = float(data)
        else:
            result = bool(data)
    else:
        raise TypeError('Unsupported type {}'.format(type(data)))

    return result


def __process_value(v, depth: int, max_depth: int):
    if depth == max_depth:
        raise Exception('Maximum depth {} reached'.format(max_depth))
    if isinstance(v, (str, pandas.datetime)):
        v_new = str(v)
    elif isinstance(v, bool_types):
        v_new = bool(v)
    elif isinstance(v, float_types):
        v_new = float(v)
    elif isinstance(v, int_types):
        v_new = int(v)
    elif isinstance(v, collection_types):
        v_new = get_json_dumpable(
            data=v.copy(),
            depth=depth + 1,
            max_depth=max_depth
        )
    elif v is None:
        v_new = v
    else:
        raise TypeError('Unsupported type {}'.format(type(v)))
    return v_new


def jprint(j, indent=2, **kwargs):
    print(json.dumps(get_json_dumpable(j, *kwargs), indent=indent))


def find_key(x: (dict, list), key: str, broad=False) -> list:
    """
    :param x: dictionary or list containing dictionaries
    :param key: key to look for
    :param broad: broad match for the value
    :return:
    """
    res = []

    if isinstance(x, dict):
        match = __match_key(d=x, key=key, broad=broad)
        if match[0]:
            found = [
                find_key(x=x[m], key=key, broad=broad)
                for m in match[1]
            ]

            res = [
                list((m, f)) if len(f) > 1
                else m[0] if len(m) == 1 else m
                for m, f in zip(match[1], found)
            ]

        else:
            for k, v in x.items():
                if isinstance(v, (dict, list)):
                    res += [
                        [k] + e if isinstance(e, list)
                        else [k] + [e]
                        for e in find_key(x=v, key=key, broad=broad)]

    elif isinstance(x, list):
        for i, v in enumerate(x):
            res += [
                [[i]] + e if isinstance(e, list)
                else [[i]] + [e]
                for e in find_key(x=v, key=key, broad=broad)
            ]
    return res


def __match_key(d: dict, key: str, broad: bool):
    if broad:
        b_match = [k for k in d.keys() if key in k]
        return any(b_match), b_match
    else:
        return key in d.keys(), [key]


def get_keys(d: dict, key: str, broad: bool = False) -> list:
    keys = find_key(x=d, key=key, broad=broad)
    result = []
    for k in keys:
        elem = ""
        for e in k:
            if isinstance(e, list):
                z = str(e[-1])
            else:
                z = "'{}'".format(e)
            elem += "[{}]".format(z)
        result.append(elem)
    return result


def describe(
        df: pandas.DataFrame, columns=None, excluded_columns=None,
        n_max_levels=100, n_bins=100):
    """
    :param df: pandas.DataFrame to plot
    :param columns: columns to plot. None plots all the columns in df
    :param excluded_columns: columns to exclude
    :param n_max_levels: maximum number of levels to plot. Variables with more
            than n_max_levels will not be plot
    :param n_bins: nunber of bins for float/int variables
    """
    original_figsize = plt.rcParams['figure.figsize']
    plt.rcParams['figure.figsize'] = (18, original_figsize[1])

    if columns is None:
        columns = df.columns
    if excluded_columns is not None:
        columns = [x for x in columns if x not in excluded_columns]

    for col in columns:
        dtype = df[col].dtype
        uniques = df[col].unique()
        n_uniques = len(uniques)

        infos = '[variable: {}] [dtype: {}] [n_uniques: {}] ' \
            .format(col, dtype, n_uniques)
        print('{:_<125} '.format(infos))

        if dtype in float_types:
            df[col].hist(bins=n_bins)
            plt.tick_params('x', rotation=45)
        elif dtype in int_types:
            if n_uniques <= n_max_levels:
                sns.countplot(df[col])
                plt.tick_params('x', rotation=45)
            else:
                df[col].hist(bins=n_bins)
                plt.tick_params('x', rotation=45)
        elif dtype == 'O' and n_uniques < n_max_levels:
            sns.countplot(df[col])
            plt.tick_params('x', rotation=45)

        plt.show()

    plt.rcParams['figure.figsize'] = original_figsize


# auxiliary functions
def inv_logit(x):
    return numpy.exp(x) / (1 + numpy.exp(x))


def linear(x):
    return x


def reciprocal(x):
    return 1.0 / x


def logit(x):
    return numpy.log(x / (1 - x))


def sign(x):
    return int(x > 0)
