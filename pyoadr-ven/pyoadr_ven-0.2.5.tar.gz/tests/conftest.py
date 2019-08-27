import pytest

from pyoadr_ven import database
from pyoadr_ven import OpenADRVenAgent


VTN_ADDRESS = "https://openadr-staging"


database.setup_db()


@pytest.fixture
def agent():

    agent = OpenADRVenAgent(
        ven_id="ven01",
        vtn_id="vtn01",
        vtn_address=VTN_ADDRESS,
        security_level="standard",
        poll_interval_secs=15,
        log_xml=False,
        opt_in_timeout_secs=3,
        opt_in_default_decision="optIn",
        request_events_on_startup=True,
        report_parameters={},
        client_pem_bundle="/home/peter/carboncoop/hems/docker/data/carboncoop-hems-shared-data/client.pem",
        vtn_ca_cert="/home/peter/carboncoop/hems/docker/data/carboncoop-hems-shared-data/ca.crt",
    )
    return agent
