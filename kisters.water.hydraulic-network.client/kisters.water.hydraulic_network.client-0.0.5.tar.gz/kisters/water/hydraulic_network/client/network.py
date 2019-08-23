import json

from kisters.water.hydraulic_network.models import Metadata, link, node


class Network:
    _resource = "rest", "networks"

    def __init__(self, name, client, drop_existing=False):
        self._name = name
        self._client = client
        self._network_resource = (*self._resource, self.name)
        if drop_existing:
            self.drop()

    def initialize(self, nodes=None, links=None, metadata=None):
        network_data = {}
        if nodes:
            network_data["nodes"] = self._validate_serialize_elements(nodes, node)
        if links:
            network_data["links"] = self._validate_serialize_elements(links, link)
        if metadata:
            if isinstance(metadata, dict):
                metadata = Metadata(**metadata)
            network_data["metadata"] = metadata.asdict(json_compatible=True)
        self._client.put(self._network_resource, network_data)

    def get_links(
        self,
        uids=None,
        display_names=None,
        element_type=None,
        adjacent_nodes=None,
        only_interior=True,
        datetime=None,
    ):
        """Gets an iterable of links

        Gets the the links in the network. The links are filterable by optional
        kwargs.

        :param uids:
            Optional list of uid strings to match
        :param display_names:
            Optional list of display name strings to match
        :param element_type:
            Optional element type string to match
        :param adjacent_nodes:
            Optional list of node uids that the links are connected to
        :param only_interior:
            Don't to match links that are attached at only one end to an adjacent_node
        """
        parameters = {}
        if uids:
            parameters["uids"] = ",".join(uids)
        if display_names:
            parameters["display_names"] = ",".join(display_names)
        if element_type:
            if isinstance(element_type, str):
                parameters["type"] = element_type
            elif hasattr(element_type, "__name__"):
                parameters["type"] = element_type.__name__
            else:
                raise ValueError(
                    "kwarg element_type {} should be string or element class".format(
                        element_type
                    )
                )
        if adjacent_nodes:
            adjacent_node_uids = [
                (node if isinstance(node, str) else node.uid) for node in adjacent_nodes
            ]
            parameters["adjacent_node_uids"] = ",".join(adjacent_node_uids)
        if not only_interior:
            parameters["only_interior"] = "False"
        if datetime:
            if hasattr(datetime, "isoformat"):
                datetime = datetime.isoformat()
            parameters["datetime"] = datetime
        result = self._client.get((*self._network_resource, "links"), parameters)
        return [link.instantiate(elem) for elem in result["links"]]

    def get_nodes(
        self,
        uids=None,
        display_names=None,
        element_type=None,
        extent=None,
        schematic_extent=None,
        datetime=None,
    ):
        """Gets an iterable of nodes

        Gets the the nodes in the network. The nodes are filterable by optional
        kwargs.

        :param uids:
            Optional list of uid strings to match
        :param display_names:
            Optional list of display name strings to match
        :param element_type:
            Optional element type string to match
        :param extent:
            Optional mapping of extent dimensions to min and max extent of that
            dimension that returned nodes should be found within.
        :param schematic_extent:
            Optional mapping of schematic_extent dimensions to min and max extent
            of that dimension that returned nodes should be found within.
        """
        parameters = {}
        if uids:
            parameters["uids"] = ",".join(uids)
        if display_names:
            parameters["display_names"] = ",".join(display_names)
        if element_type:
            if isinstance(element_type, str):
                parameters["type"] = element_type
            elif hasattr(element_type, "__name__"):
                parameters["type"] = element_type.__name__
            else:
                raise ValueError(
                    "kwarg element_type {} should be string or element class".format(
                        element_type
                    )
                )
        if extent:
            parameters["extent"] = json.dumps(extent)
        if schematic_extent:
            parameters["schematic_extent"] = json.dumps(schematic_extent)
        if datetime:
            if hasattr(datetime, "isoformat"):
                datetime = datetime.isoformat()
            parameters["datetime"] = datetime

        result = self._client.get((*self._network_resource, "nodes"), parameters)
        return [node.instantiate(elem) for elem in result["nodes"]]

    @staticmethod
    def _validate_serialize_elements(elements, element_group):
        validated_elements = []
        for element in elements:
            if isinstance(element, dict):
                # Instantiate and validate element defintion
                element = element_group.instantiate(element)
            validated_elements.append(element.asdict(json_compatible=True))
        return validated_elements

    def save_nodes(self, nodes):
        """Save an iterable of node definitions"""
        nodes = self._validate_serialize_elements(nodes, node)
        for elem in nodes:
            self._client.post((*self._network_resource, "nodes"), {"attributes": elem})

    def save_links(self, links):
        """Save an iterable of link definitions"""
        links = self._validate_serialize_elements(links, link)
        for elem in links:
            self._client.post((*self._network_resource, "links"), {"attributes": elem})

    def get_metadata(self, datetime=None):
        """Get a network's metadata"""
        parameters = {}
        if datetime:
            if hasattr(datetime, "isoformat"):
                datetime = datetime.isoformat()
            parameters["datetime"] = datetime
        result = self._client.get((*self._network_resource, "metadata"), parameters)
        if "schematic_extent" in result and not result["schematic_extent"]:
            del result["schematic_extent"]
        if "extent" in result and not result["extent"]:
            del result["extent"]
        return Metadata(**result)

    def set_metadata(self, metadata=None, **kwargs):
        """Set a network's metadata"""
        metadata = metadata or {}
        if isinstance(metadata, Metadata):
            metadata = metadata.asdict(json_compatible=True)
        metadata.update(kwargs)
        if metadata:
            self._client.post((*self._network_resource, "metadata"), metadata)

    def drop(self):
        """Removes the network"""
        self._client.delete(self._network_resource)

    def drop_links(self, uids):
        """Deletes the links with the given uids"""
        for uid in uids:
            self._client.delete((*self._network_resource, "links", uid))

    def drop_nodes(self, uids):
        """Deletes the nodes with the given uids"""
        for uid in uids:
            self._client.delete((*self._network_resource, "nodes", uid))

    @property
    def name(self):
        """The name of the network"""
        return self._name
