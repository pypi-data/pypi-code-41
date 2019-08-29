from pathlib import Path
from typing import Union
from xml.etree import ElementTree as ET
from xml.dom import minidom

PathLike = Union[str, Path]  # python3.5 compatible


def subset_head(
    source_file: PathLike, target_file: PathLike, data_tag: str, ratio: float
):
    root = ET.parse(str(source_file)).getroot()

    data_length = len(root.findall(data_tag))
    desired_length = int(data_length * ratio)

    met_count = 0
    less_data = []
    print(met_count, desired_length)
    for element in root:
        if met_count < desired_length and element.tag == data_tag:
            met_count += 1
            less_data.append(element)
        elif element.tag != data_tag:
            less_data.append(element)

    new_string = "<r>"
    for element in less_data:
        new_string += ET.tostring(element, encoding="unicode")
    new_string += "</r>"
    new_xml = minidom.parseString(new_string).toprettyxml()

    with open(str(target_file), "w") as file:
        file.write(new_xml)
