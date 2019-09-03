# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = [
    "load_object",
    "normalize_hyperparameters",
    "load_recommender",
    "load_params",
    "default_dataset_loader",
]

import importlib
import inspect
import pickle
from typing import Any, Callable, Dict, Type, TypeVar, cast, TYPE_CHECKING


from crecs.rs.abc import Recommender
from crecs.sage import abc


T = TypeVar("T")


def load_object(value: str) -> Any:
    try:
        module_path, object_path = value.rsplit(":", 1)
    except ValueError:
        raise ValueError(f"Invalid object path {value!r}") from None

    module = importlib.import_module(module_path)
    out: Any = module
    try:
        for attr in object_path.split("."):
            out = getattr(out, attr)
    except AttributeError:
        raise ValueError(
            f"Module {module_path} has no attribute {object_path}"
        ) from None
    return out


def load_class(value: str, type: Type[T]) -> Type[T]:
    t = load_object(value)
    assert issubclass(t, type)
    return t


# def dataset_loader(fn: Callable[[abc.HP], T]) -> abc.DatasetLoader[T]:
#    o = type(fn.__name__, (), {"load_dataset": fn})
#    return cast(abc.DatasetLoader[T], o)


def default_dataset_loader(data: abc.HP) -> Any:
    with open("/opt/ml/input/data/training/dataset.pkl", "rb") as fp:
        return pickle.load(fp)


def default_recommender_saver(rec: Any) -> None:
    with open("model.pkl", "wb") as fp:
        pickle.dump(rec, fp)


def normalize_hyperparameters(hp: Dict[str, Any]) -> Dict[str, str]:
    out = {}
    for k, v in hp.items():
        if not isinstance(k, str):
            raise ValueError("Hyperparameter names must be strings")
        if not isinstance(v, (int, float, str)):
            raise ValueError(
                f"Invalid HyperParameter type for {k!r}: {type(v)}"
            )
        out[k] = str(v)
    return out


def load_recommender(data: abc.HP) -> Recommender[T]:
    obj = load_object(str(data.pop("recommender")))
    return (
        obj.load_recommender(data)
        if isinstance(obj, abc.RecommenderLoader)
        else obj
    )


_ALLOWED_TYPES = (int, float, str)


def load_params(cls: Type[Any], data: abc.HP) -> Dict[str, Any]:
    sig = inspect.signature(cls.__init__)

    out = {}
    for param in sig.parameters.values():
        if param.name == "self":
            continue

        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            raise TypeError("*args and **kwargs hyperparamters not supported")

        try:
            val: Any = str(data[param.name])
        except KeyError:
            if param.default is param.empty:
                raise TypeError(f"Missing hyperparameter {param.name}")
        else:
            if val.startswith("@"):
                val = load_object(val[1:])

            typ = param.annotation
            if isinstance(typ, type) and issubclass(typ, _ALLOWED_TYPES):
                val = typ(val)

            out[param.name] = val

    return out

