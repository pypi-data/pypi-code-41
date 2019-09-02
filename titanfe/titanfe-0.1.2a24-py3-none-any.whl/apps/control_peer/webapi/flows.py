# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Routes for Flow management"""


from typing import Dict
from fastapi import APIRouter
from pydantic import BaseModel


# - Response Types
class FlowResponse(BaseModel):   # pylint: disable=too-few-public-methods
    name: str
    uid: int
    state: str


def create_flow_router(control_peer):
    """Setup the routing for flow management

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Returns:
        APIRouter: router/routes to manage the control peer's flows
    """
    router = APIRouter()

    @router.get("/", response_model=Dict[int, FlowResponse])
    def list_flows():  # pylint: disable=unused-variable
        """List the currently configured flows and their state"""
        flows = [
            FlowResponse(name=flow.name, uid=flow.uid, state=flow.state.name)
            for flow in control_peer.flows
        ]
        return {flow.uid: flow for flow in flows}

    return router
