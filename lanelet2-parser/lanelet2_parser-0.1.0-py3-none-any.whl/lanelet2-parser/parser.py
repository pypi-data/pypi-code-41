import traceback
import xml.etree.ElementTree as ET
from ll2_parser.exceptions import InvalidFileFormatError, MissingResourceError

class Lanelet2Parser(object):

    def parse(self, src_file):
        '''
        Load OSM file and convert to dict format
        :param src_file: osm_file
        :return: osm_data
        '''
        # load xml file
        try:
            tree = ET.parse(src_file)
        except:
            raise MissingResourceError()

        # convert to dict format
        try:
            osm = tree.getroot()
            osm_data = {
                "version": osm.attrib["version"] if "version" in osm.attrib else 0.0,
                "generator": osm.attrib["generator"] if "generator" in osm.attrib else "unkown",
                "map_format": "",
                "map_version": "",
                "node": [],
                "way": [],
                "relation": []
            }
            # node
            for osm_node in osm.iter("node"):
                _osm_node = {
                    "id": osm_node.attrib["id"],
                    "visible": osm_node.attrib["visible"],
                    "lat": osm_node.attrib["lat"],
                    "lon": osm_node.attrib["lon"],
                    "tag": []
                }
                for node_tag in osm_node:
                    _node_tag = {
                        "k": node_tag.attrib["k"],
                        "v": node_tag.attrib["v"],
                    }
                    _osm_node["tag"].append(_node_tag)
                # append
                osm_data["node"].append(_osm_node)
            # way
            for osm_way in osm.iter("way"):
                _osm_way = {
                    "id": osm_way.attrib["id"],
                    "visible": osm_way.attrib["visible"],
                    "version": osm_way.attrib["version"] if "version" in osm_way.attrib else None,
                    "nd": [],
                    "tag": [],
                }
                # nd
                for way_nd in osm_way.findall("nd"):
                    _way_nd = {
                        "ref": way_nd.attrib["ref"]
                    }
                    _osm_way["nd"].append(_way_nd)
                # tag
                for way_tag in osm_way.findall("tag"):
                    _way_tag = {
                        "k": way_tag.attrib["k"],
                        "v": way_tag.attrib["v"],
                    }
                    _osm_way["tag"].append(_way_tag)
                # append
                osm_data["way"].append(_osm_way)
            # relation
            for osm_relation in osm.iter("relation"):
                _osm_relation = {
                    "id": osm_relation.attrib["id"],
                    "visible": osm_relation.attrib["visible"],
                    "action": osm_relation.attrib["action"] if "action" in osm_relation.attrib else None,
                    "member": [],
                    "tag": []
                }
                # member
                for relation_member in osm_relation.findall("member"):
                    _relation_member = {
                        "type": relation_member.attrib["type"],
                        "ref": relation_member.attrib["ref"],
                        "role": relation_member.attrib["role"],
                    }
                    _osm_relation["member"].append(_relation_member)
                # tag
                for relation_tag in osm_relation.findall("tag"):
                    _relation_tag = {
                        "k": relation_tag.attrib["k"],
                        "v": relation_tag.attrib["v"],
                    }
                    _osm_relation["tag"].append(_relation_tag)
                # append
                osm_data["relation"].append(_osm_relation)

            # validate
            is_ok = self.validate(osm_data)
            print("[Response]", is_ok)
            if is_ok is False:
                raise InvalidFileFormatError()

            return osm_data
        except:
            print(traceback.format_exc())
            raise InvalidFileFormatError

    def validate(self, osm_data):
        _osm_data = {
            "node": {},
            "way": {},
            "relation": {}
        }

        # convert dict format for key search
        for node in osm_data["node"]:
            if node["id"] in _osm_data["node"]:
                raise MissingResourceError("Node is duplicated.")
            _osm_data["node"][node["id"]] = node
        for way in osm_data["way"]:
            if way["id"] in _osm_data["way"]:
                raise MissingResourceError("Way is duplicated.")
            _osm_data["way"][way["id"]] = way
        for relation in osm_data["relation"]:
            if relation["id"] in _osm_data["relation"]:
                raise MissingResourceError("Relation is duplicated.")
            _osm_data["relation"][relation["id"]] = relation

        # check exist of way's node
        for way in osm_data["way"]:
            for nd in way["nd"]:
                if nd["ref"] not in _osm_data["node"]:
                    raise MissingResourceError("Way's node is not found.")
        # check exist of relation's member
        for relation in osm_data["relation"]:
            for member in relation["member"]:
                if member["type"] == "way":
                    if member["ref"] not in _osm_data["way"]:
                        raise MissingResourceError("Relation's way is not found.")
                if member["type"] == "relation":
                    if member["ref"] not in _osm_data["relation"]:
                        raise MissingResourceError("Relation's relation is not found.")

        return True





