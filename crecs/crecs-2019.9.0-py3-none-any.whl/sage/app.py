# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

import json
import logging

import flask
from werkzeug import exceptions
from werkzeug.http import HTTP_STATUS_CODES


JSON_CT = "application/json"

logger = logging.getLogger(__name__)


class App(flask.Flask):
    def __init__(self, model: RecommenderModel, n_items: int):
        super().__init__("sagetuner")

        self.model = model
        self.n_items = n_items

        self.MAX_CONTENT_LENGTH = 1024 * 1024
        # useless
        # self.config['MAX_CONTENT_LENGTH'] = self.MAX_CONTENT_LENGTH

        self.add_url_rule("/ping", "ping", self.ping)
        self.add_url_rule(
            "/invocations", "invocations", self.invocations, methods=["POST"]
        )

    def ping(self) -> flask.Response:
        return self.response_class("{}", 200, content_type=JSON_CT)

    def invocations(self) -> flask.Response:
        req: flask.Request = flask.request
        if req.mimetype != JSON_CT:
            raise exceptions.UnsupportedMediaType

        assert isinstance(req.content_length, int)
        if req.content_length > self.MAX_CONTENT_LENGTH:
            raise exceptions.RequestEntityTooLarge

        dataset = self.read_dataset()
        out = self.model.recommend(dataset)[0]

        return self.response_class(json.dumps(out), 200, content_type=JSON_CT)

    def read_dataset(self) -> Dataset:
        req: flask.Request = flask.request
        # data = msgpack.load(
        #    req.stream, max_buffer_size=self.MAX_CONTENT_LENGTH, raw=False
        # )
        # return Dataset.Schema().convert(data)

        data = json.load(req.stream)
        return DatasetSchema(n_items=self.n_items).decode(data)

    def handle_exception(self, exc: Exception) -> flask.Response:
        logger.exception("Unhandled error")
        code = 500
        desc = str(exc)
        if isinstance(exc, exceptions.HTTPException):
            if exc.code is not None:
                code = exc.code
            if exc.description is not None:
                desc = exc.description

        name = HTTP_STATUS_CODES.get(code, "Unknown Error")
        data = json.dumps({"name": name, "code": code, "description": desc})
        return self.response_class(data, code, content_type=JSON_CT)

    # NOTE: I believe flask's stubs are wrong
    handle_user_exception = handle_exception  # type: ignore
