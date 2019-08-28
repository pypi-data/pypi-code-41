class TestClient:
    client_id = "30vhDIDRNLMdGWgwhswJFhrMxw98ztEv"
    client_secret = ""
    audience = ""
    env_id = "64c6dde7-7830-47c1-a411-6c39c158ec79"


class TestOrganization:
    id = "02efa741-a96f-4124-a463-ae13a704b8fc"
    name = "Lineage Logistics"


class TestFacility:
    """Known facility used for testing"""

    id = 85  # 65
    name = "Chesapeake_201"
    asset_id = "4475c753-fc5a-4f66-ac22-32c27f6aaa4b"
    organization_id = "02efa741-a96f-4124-a463-ae13a704b8fc"


class TestChannel:
    """Test channel for Message Bus service"""

    id = "1c38a051-dc0a-4b84-b470-98775138e4d1"
    name = "feed:1"
    service_id = "GCXd2bwE9fgvqxygrx2J7TkDJ3efXBKM"
    organization_id = "02efa741-a96f-4124-a463-ae13a704b8fc"
    organization_name = "Lineage Logistics"


class TestField:
    """Test field for IOT service"""

    id = 130706
    output_id = 8697
    field_human_name = "wpe.caphist.alphashiftot"
    facility_id = 184
    grouping_id = "004f9966-45b7-441b-8541-755b2d2d08d4"
    feed_id = 25
    feed_key = "some-key"


class TestTriggeredEvent:
    id = "7365924b-df32-4694-afa8-9eee174be1b9"
    event_id = "952a8d55-3b2c-462d-a8a0-24c6a76d868b"
    event_type_id = "0a5057fa-85ae-43e0-9137-9e5372c2566d"


class TestWorker:
    config_id = "1c5eac15-3d38-4432-8f6b-9f585202429a"
    env_id = "4a9cfc2b-2580-4d01-8e67-0ea176296746"


class TestAssetType:
    id = "c5e33fbb-3134-4d71-aeb3-79775d19ac28"
    organization_id = "5428b34c-521b-4f20-b6f0-67a6d968e21b"
    label = "TestParentType"
    attribute_id = "af6c222d-1b07-4262-8650-768a45c94640"
    metric_id = "4262a67f-b52a-4f7d-a821-94776158c519"


class TestAsset:
    id = "c776760f-025f-4ffc-943e-602726243c19"
    organization_id = "5428b34c-521b-4f20-b6f0-67a6d968e21b"
