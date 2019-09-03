# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["CrecsPredictor", "Crecs"]

import json
from typing import Any, Dict, List, Optional, TypeVar, TYPE_CHECKING

from sagemaker.estimator import EstimatorBase
from sagemaker.fw_utils import create_image_uri
from sagemaker.model import Model
from sagemaker.predictor import (
    RealTimePredictor,
    json_deserializer,
    json_serializer,
)
from sagemaker.vpc_utils import VPC_CONFIG_DEFAULT

from crecs import rs
from crecs.sage import abc, utils


if TYPE_CHECKING:
    from sagemaker.session import Session
else:
    Session = None


class CrecsPredictor(RealTimePredictor):
    def __init__(self, endpoint_name: str, sagemaker_session: Any = None):
        super().__init__(
            endpoint_name,
            sagemaker_session,
            json_serializer,
            json_deserializer,
        )


T = TypeVar("T")


class Crecs(EstimatorBase):
    # NOTE defining these even if we are not inheriting from Framework
    __framework_name__ = "crecs"

    def __init__(
        self,
        recommender: Any,
        hyperparameters: Dict[str, Any] = None,
        *,
        role: str,
        train_instance_type: str,
        train_instance_count: int = 1,
        train_volume_size: int = 30,
        train_volume_kms_key: str = None,
        train_max_run: int = 24 * 60 * 60,
        input_mode: str = "File",
        output_path: str = None,
        output_kms_key: str = None,
        base_job_name: str = None,
        sagemaker_session: Session = None,
        tags: List[Dict[str, str]] = None,
        subnets: List[str] = None,
        security_group_ids: List[str] = None,
        model_uri: str = None,
        model_channel_name: str = "model",
        metric_definitions: List[Dict[str, Any]] = None,
        framework_version: str = "master",
    ):
        hp = {} if hyperparameters is None else hyperparameters
        hp = {**hp, "recommender": recommender}

        # validate hyper parameters
        self._hyperparameters = utils.normalize_hyperparameters(hp)
        utils.load_recommender(hp)

        self.framework_version = framework_version
        super().__init__(
            role,
            train_instance_count,
            train_instance_type,
            train_volume_size,
            train_volume_kms_key,
            train_max_run,
            input_mode,
            output_path,
            output_kms_key,
            base_job_name,
            sagemaker_session,
            tags,
            subnets,
            security_group_ids,
            model_uri=model_uri,
            model_channel_name=model_channel_name,
            metric_definitions=metric_definitions,
        )

    def train_image(self) -> str:
        return create_image_uri(
            self.sagemaker_session.boto_region_name,
            self.__framework_name__,
            self.train_instance_type,
            self.framework_version,
            account=788_429_729_734,
        )

    def hyperparameters(self) -> Dict[str, str]:
        return self._hyperparameters

    def create_model(
        self,
        vpc_config_override: str = VPC_CONFIG_DEFAULT,
        model_data: str = None,
        **kwds: Any,
    ) -> Model:
        return Model(
            model_data or self.model_data,
            self.train_image(),
            self.role,
            predictor_cls=CrecsPredictor,
            sagemaker_session=self.sagemaker_session,
            vpc_config=self.get_vpc_config(vpc_config_override),
            **kwds,
        )
