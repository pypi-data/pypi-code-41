# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

import logging
import os
import pickle
import shutil
import subprocess
import sys
from typing import Any, cast

from crecs import rs
from crecs.sage import abc, utils


logger = logging.getLogger(__name__)


def train() -> None:
    from sagemaker_containers.beta import framework

    env = framework.training_env()
    logger.setLevel(env.log_level)

    logger.info("TRAIN")
    logger.debug(str(os.environ))
    logger.debug(str(sys.argv))
    logger.debug(str(env))

    hp = env.hyperparameters
    rec: rs.Recommender[Any] = utils.load_recommender(hp)
    logger.info(f"Loader recommender: {rec}")

    ds = (
        cast(abc.DatasetLoader[Any], rec).load_dataset
        if isinstance(rec, abc.DatasetLoader)
        else utils.default_dataset_loader
    )(hp)
    logger.info(f"Loaded dataset: {ds}")

    model = rec(ds)
    logger.info(f"Produced model: {model}")

    os.chdir("/opt/ml/model")

    (
        cast(abc.RecommenderModelSaver, rec).save_recommender
        if isinstance(rec, abc.RecommenderModelSaver)
        else utils.default_recommender_saver
    )(model)
