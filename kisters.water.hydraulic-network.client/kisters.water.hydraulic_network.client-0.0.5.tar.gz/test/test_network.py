import os
import uuid
from datetime import datetime
from unittest import TestCase

import requests
from kisters.water.hydraulic_network.client import (
    Network,
    OpenIDConnect,
    RESTClient,
    TemporaryAccess,
)
from kisters.water.hydraulic_network.models import Metadata, link, node
from kisters.water.hydraulic_network.models.element import InvalidAttributeError

TEST_DATA = {
    "links": [
        {
            "uid": "channel",
            "source_uid": "junction",
            "target_uid": "storage",
            "stations": [
                {
                    "roughness": 10.0,
                    "cross_section": [
                        {"z": 0, "lr": -5},
                        {"z": 0, "lr": 5},
                        {"z": 10, "lr": -5},
                        {"z": 10, "lr": 5},
                    ],
                }
            ],
            "cross_sections": [
                {
                    "cross_section": [
                        {"width": 10.0, "level": 0},
                        {"width": 10.0, "level": 10},
                    ]
                }
            ],
            "length": 100.0,
            "roughness": 10.0,
            "model": "saint-venant",
            "roughness_model": "chezy",
            "created": "2019-06-27T16:53:05",
            "display_name": "channel",
            "type": "Channel",
        },
        {
            "uid": "delay",
            "source_uid": "junction",
            "target_uid": "storage",
            "transit_time": 10.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "delay",
            "type": "Delay",
        },
        {
            "uid": "flow_controlled_structure",
            "source_uid": "junction",
            "target_uid": "storage",
            "min_flow": -1.0,
            "max_flow": 1.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "flow_controlled_structure",
            "type": "FlowControlledStructure",
        },
        {
            "uid": "orifice",
            "source_uid": "junction",
            "target_uid": "storage",
            "model": "free",
            "coefficient": 1.0,
            "aperture": 10.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "orifice",
            "type": "Orifice",
        },
        {
            "uid": "pipe",
            "source_uid": "junction",
            "target_uid": "storage",
            "diameter": 1.0,
            "length": 10.0,
            "roughness": 10.0,
            "model": "hazen-williams",
            "check_valve": False,
            "created": "2019-06-27T16:53:05",
            "display_name": "pipe",
            "type": "Pipe",
        },
        {
            "uid": "pump",
            "source_uid": "junction",
            "target_uid": "storage",
            "speed": [
                {"flow": 1, "head": 1, "speed": 1},
                {"flow": 3, "head": 3, "speed": 1},
            ],
            "min_speed": 1.0,
            "max_speed": 1.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "pump",
            "type": "Pump",
        },
        {
            "uid": "turbine",
            "source_uid": "junction",
            "target_uid": "storage",
            "speed": [
                {"flow": 1, "head": 1, "speed": 1},
                {"flow": 3, "head": 3, "speed": 1},
            ],
            "min_speed": 1.0,
            "max_speed": 1.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "turbine",
            "type": "Turbine",
        },
        {
            "uid": "valve",
            "source_uid": "junction",
            "target_uid": "storage",
            "diameter": 10.0,
            "model": "prv",
            "coefficient": 1.0,
            "setting": 0.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "valve",
            "type": "Valve",
        },
        {
            "uid": "weir",
            "source_uid": "junction",
            "target_uid": "storage",
            "model": "free",
            "coefficient": 1.0,
            "min_crest_level": 0.0,
            "max_crest_level": 0.0,
            "crest_width": 10.0,
            "created": "2019-06-27T16:53:05",
            "display_name": "weir",
            "type": "Weir",
        },
    ],
    "nodes": [
        {
            "uid": "flow_boundary",
            "location": {"x": 0.0, "y": 0.0, "z": 0.0},
            "created": "2019-06-27T16:53:05",
            "display_name": "flow_boundary",
            "schematic_location": {"x": 0.0, "y": 0.0, "z": 0.0},
            "type": "FlowBoundary",
        },
        {
            "uid": "junction",
            "location": {"x": 0.0, "y": 1.0, "z": 0.0},
            "created": "2019-06-27T16:53:05",
            "display_name": "junction",
            "schematic_location": {"x": 0.0, "y": 1.0, "z": 0.0},
            "type": "Junction",
        },
        {
            "uid": "level_boundary",
            "location": {"x": 1.0, "y": 0.0, "z": 0.0},
            "created": "2019-06-27T16:53:05",
            "display_name": "level_boundary",
            "schematic_location": {"x": 1.0, "y": 0.0, "z": 0.0},
            "type": "LevelBoundary",
        },
        {
            "uid": "storage",
            "location": {"x": 1.0, "y": 1.0, "z": 0.0},
            "level_volume": [
                {"level": 0.0, "volume": 0.0},
                {"level": 10.0, "volume": 10.0},
            ],
            "created": "2019-06-27T16:53:05",
            "display_name": "storage",
            "schematic_location": {"x": 1.0, "y": 1.0, "z": 0.0},
            "type": "Storage",
        },
    ],
    "metadata": {
        "created": "2019-06-25T14:18:37",
        "projection": "unknown",
        "datum": "unknown",
        "num_hierarchy_levels": 1,
    },
}

TEST_MODEL = {
    "nodes": [node.instantiate(elem) for elem in TEST_DATA["nodes"]],
    "links": [link.instantiate(elem) for elem in TEST_DATA["links"]],
    "metadata": Metadata(**TEST_DATA["metadata"]),
}

auth_config = {
    "client_id": os.environ["HYDRAULIC_NETWORK_CLIENT_ID"],
    "client_secret": os.environ["HYDRAULIC_NETWORK_CLIENT_SECRET"],
    "issuer_url": "https://auth.kisters.cloud/auth/realms/external",
}

rest_server_url = "https://{}.hydraulic-network.kisters.cloud/".format(
    os.environ["HYDRAULIC_NETWORK_DEPLOY_ID"]
)
authentication = OpenIDConnect(**auth_config)
client = RESTClient(url=rest_server_url, authentication=authentication)
network_name = "test-python-rest-client-{}".format(str(uuid.uuid4())[:6])


class TestRest(TestCase):
    def setUp(self):
        self.network = Network(network_name, client)

    def test00_initialize_with_dict(self):
        self.network.initialize(**TEST_DATA)

    def test00_initialize(self):
        self.network.initialize(**TEST_MODEL)

    def test01_no_auth(self):
        unauth_client = RESTClient(url=rest_server_url)
        with self.assertRaises(requests.exceptions.HTTPError):
            unauth_client.get(("rest", "networks"))
        network = Network("tmp", client=unauth_client)
        with self.assertRaises(requests.exceptions.HTTPError):
            network.get_metadata()

    def test02_temp_auth(self):
        access_token = authentication.get_access_token()
        temp_access = TemporaryAccess(access_token)
        network = Network(
            "tmp", client=RESTClient(url=rest_server_url, authentication=temp_access)
        )
        self.assertTrue(network.get_metadata())

    def test02_access_token_expiration(self):
        # Warning: this method accesses private vars for testing purposes
        # we pretend the token is expired to trigger a token refresh
        fake_expiration = datetime.utcnow()
        authentication._access_token_expiration = fake_expiration
        old_token = authentication._access_token
        authentication.get_access_token()
        self.assertNotEqual(fake_expiration, authentication._access_token_expiration)
        self.assertNotEqual(old_token, authentication._access_token)

    def test10_get_networks(self):
        names = client.get("rest/networks")
        self.assertIn(network_name, names)

    def test20_get_metadata(self):
        metadata = self.network.get_metadata()

        # Test static properties
        for prop, val in TEST_MODEL["metadata"].asdict().items():
            self.assertEqual(metadata[prop], val)

        # Test dynamic properties
        self.assertEqual(metadata["extent"], {"x": [0, 1], "y": [0, 1], "z": [0, 0]})
        self.assertEqual(metadata["schematic_extent"], {"x": [0, 1], "y": [0, 1]})

    def test21_get_metadata_filtered(self):
        metadata0 = self.network.get_metadata(datetime="2019-06-27T16:53:04")
        metadata1 = self.network.get_metadata(datetime=datetime(2019, 6, 27, 16, 53, 5))

        self.assertEqual(metadata1["extent"], {"x": [0, 1], "y": [0, 1], "z": [0, 0]})
        self.assertEqual(metadata1["schematic_extent"], {"x": [0, 1], "y": [0, 1]})
        with self.assertRaises(KeyError):
            metadata0["extent"]
        with self.assertRaises(KeyError):
            metadata0["schematic_extent"]

    def test22_put_metadata(self):
        original = TEST_MODEL["metadata"]
        test_datum = "test_datum"
        self.network.set_metadata(datum=test_datum)
        new_metadata = self.network.get_metadata()
        self.assertEqual(test_datum, new_metadata["datum"])
        self.assertEqual(original.created, new_metadata.created)

        self.network.set_metadata(original)
        self.test20_get_metadata()

    def test40_get_nodes(self):
        nodes = self.network.get_nodes()
        self.assertElementsUnchanged(nodes, TEST_MODEL["nodes"])

    def test41_get_nodes_filtered(self):
        nodes0 = self.network.get_nodes(datetime="2019-06-27T16:53:04")
        nodes1 = self.network.get_nodes(datetime=datetime(2019, 6, 27, 16, 53, 5))
        self.assertEqual(nodes0, [])
        self.assertElementsUnchanged(nodes1, TEST_MODEL["nodes"])

        subset_nodes = TEST_MODEL["nodes"][:2]
        result = self.network.get_nodes(
            display_names=[node["display_name"] for node in subset_nodes]
        )
        self.assertElementsUnchanged(result, subset_nodes)

        subset_nodes = TEST_MODEL["nodes"][:2]
        result = self.network.get_nodes(uids=[node["uid"] for node in subset_nodes])
        self.assertElementsUnchanged(result, subset_nodes)

        subset_node = TEST_MODEL["nodes"][0]
        result = self.network.get_nodes(element_type=subset_node["type"])
        self.assertElementsUnchanged(result, [subset_node])

        subset_node = TEST_MODEL["nodes"][0]
        result = self.network.get_nodes(element_type=type(subset_node))
        self.assertElementsUnchanged(result, [subset_node])

        subset_nodes = TEST_MODEL["nodes"][:2]
        result = self.network.get_nodes(extent={"x": [-0.5, 0.5]})
        self.assertElementsUnchanged(result, subset_nodes)

        subset_nodes = TEST_MODEL["nodes"][:2]
        result = self.network.get_nodes(schematic_extent={"x": [-0.5, 0.5]})
        self.assertElementsUnchanged(result, subset_nodes)

        result = self.network.get_nodes(extent={"z": [-0.5, 0.5]})
        self.assertElementsUnchanged(result, TEST_MODEL["nodes"])

        result = self.network.get_nodes(schematic_extent={"z": [-0.5, 0.5]})
        self.assertElementsUnchanged(result, TEST_MODEL["nodes"])

    def test46_drop_nodes(self):
        self.network.drop_nodes([node["uid"] for node in TEST_MODEL["nodes"]])
        nodes = self.network.get_nodes()
        self.assertEqual([], nodes)

    def test47_save_nodes(self):
        self.network.save_nodes(TEST_MODEL["nodes"])
        nodes = self.network.get_nodes()
        self.assertElementsUnchanged(nodes, TEST_MODEL["nodes"])

    def test48_ValueError(self):
        with self.assertRaises(ValueError):
            self.network.save_nodes(TEST_MODEL["links"])

    def test50_get_links(self):
        links = self.network.get_links()
        self.assertElementsUnchanged(links, TEST_MODEL["links"])

    def test51_get_links_filtered(self):
        links0 = self.network.get_links(datetime="2019-06-27T16:53:04")
        links1 = self.network.get_links(datetime=datetime(2019, 6, 27, 16, 53, 5))
        self.assertEqual(links0, [])
        self.assertElementsUnchanged(links1, TEST_MODEL["links"])

        subset_links = TEST_MODEL["links"][:2]
        result = self.network.get_links(
            display_names=[link["display_name"] for link in subset_links]
        )
        self.assertElementsUnchanged(result, subset_links)

        subset_links = TEST_MODEL["links"][:2]
        result = self.network.get_links(uids=[link["uid"] for link in subset_links])
        self.assertElementsUnchanged(result, subset_links)

        subset_link = TEST_MODEL["links"][0]
        result = self.network.get_links(element_type=subset_link["type"])
        self.assertElementsUnchanged(result, [subset_link])

        subset_link = TEST_MODEL["links"][0]
        result = self.network.get_links(element_type=type(subset_link))
        self.assertElementsUnchanged(result, [subset_link])

        result = self.network.get_links(adjacent_nodes=["junction", "storage"])
        self.assertElementsUnchanged(result, TEST_MODEL["links"])

        result = self.network.get_links(adjacent_nodes=["junction"])
        self.assertElementsUnchanged(result, [])

        result = self.network.get_links(
            adjacent_nodes=["junction"], only_interior=False
        )
        self.assertElementsUnchanged(result, TEST_MODEL["links"])

    def test56_drop_links(self):
        self.network.drop_links([link["uid"] for link in TEST_MODEL["links"]])
        links = self.network.get_links()
        self.assertEqual([], links)

    def test57_save_links(self):
        self.network.save_links(TEST_MODEL["links"])
        links = self.network.get_links()
        self.assertElementsUnchanged(links, TEST_MODEL["links"])

    def test90_drop(self):
        self.network.drop()
        links = self.network.get_links()
        self.assertEqual(links, [])
        nodes = self.network.get_nodes()
        self.assertEqual(nodes, [])
        self.network.drop()

    def test99_get_networks(self):
        names = client.get(("rest", "networks"))
        self.assertNotIn(network_name, names)

    def assertElementsUnchanged(self, elements0, elements1):
        elements0 = sorted(elements0, key=lambda elem: elem["uid"])
        elements1 = sorted(elements1, key=lambda elem: elem["uid"])
        self.assertTrue(len(elements0) == len(elements1))
        for elem0, elem1 in zip(elements0, elements1):
            self.assertDictEqual(elem0.asdict(), elem1.asdict())
