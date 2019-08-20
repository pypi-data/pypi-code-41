from lxml import etree as et

from pathlib import Path, WindowsPath

import argparse


def collapse_nodes(metadata_content):
    """
    :param metadata_content: This can be pathlib's Path, string containing the path to the Metadata file or already parsed element tree's _ElementTree
    :return:
    """

    expansion_attrs = {'SurveyDatasetTreeNodeExpanded',
                       'TablesTreeNodeExpanded',
                       'IterationsTreeNodeExpanded',
                       'DatasetsTreeNodeExpanded',
                       'TreeNodeCollapsed',
                       'GeoTypeTreeNodeExpanded',
                       'GeoCorrespondenceTreeNodeExpanded'}

    if type(metadata_content) == WindowsPath or type(metadata_content) == str:

        parser = et.XMLParser(strip_cdata=False)
        metadata_document = et.parse(str(metadata_content), parser=parser)

        for element in metadata_document.iter():
            for attr in expansion_attrs:
                try:
                    element.attrib[attr] = "false"
                except KeyError:
                    continue

        return metadata_document

    elif type(metadata_content) == et._ElementTree:
        for element in metadata_content.iter():
            for attr in expansion_attrs:
                try:
                    element.attrib[attr] = "false"
                except KeyError:
                    continue

        return metadata_content


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Collapse all nodes in the metadata file.')
    parser.add_argument('input', type=str, help='Metadata file or folder')
    args = parser.parse_args()

    if args.input.endswith('.xml'):
        doc = collapse_nodes(args.input)
        doc.write(str(args.input))

    else:
        path_xmls = Path(args.input)

        for file in path_xmls.iterdir():
            doc = collapse_nodes(file)
            doc.write(str(file.name))
