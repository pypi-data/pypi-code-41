import pytest

from pyoadr_ven import database
from pyoadr_ven import OpenADRVenAgent


VTN_ADDRESS = "https://openadr-staging"
VEN_ID = "ven01"
VTN_ID = "vtn01"

database.setup_db()


@pytest.fixture
def agent():

    agent = OpenADRVenAgent(
        ven_id=VEN_ID,
        vtn_id=VTN_ID,
        vtn_address=VTN_ADDRESS,
        security_level="standard",
        poll_interval_secs=15,
        log_xml=True,
        opt_timeout_secs=30,
        opt_default_decision="optIn",
        request_events_on_startup=True,
        report_parameters={},
        client_pem_bundle="/home/peter/carboncoop/hems/docker/data/carboncoop-hems-shared-data/client.pem",
        vtn_ca_cert="/home/peter/carboncoop/hems/docker/data/carboncoop-hems-shared-data/ca.crt",
    )
    return agent
