# -*- coding: utf-8 -*-
#! python3

"""
    Isogeo XML Fixer - Mover from GeoSource ZIP

    Purpose:     Parse a folder containing exported metadata from GeoSource
    and rename files qualifying by XML type and title.
    Authors:     Isogeo
    Python:      3.6.x
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
from os import rename
from pathlib import Path
import re
import shutil
from uuid import UUID

# 3rd party library
import click
from lxml import etree

# modules
from csv_reporter import CsvReporter
from reader_iso19139 import MetadataIso19139
from reader_iso19110 import MetadataIso19110

# #############################################################################
# ########## Globals ###############
# ##################################

# required subfolders
input_dir = Path("input/").mkdir(exist_ok=True)
output_dir = Path("output/").mkdir(exist_ok=True)

# logging
logging.basicConfig(level=logging.INFO)

# #############################################################################
# ########## Functions #############
# ##################################
def list_metadata_folder(folder: str, kind: str = "geosource") -> tuple:
    """Parse a directory structure to list metadata folders.

    :param str folder: path to the parent folder to parse.
    :param str kind: tool structure to check. Until now, only geosource.

    Geosource - expected structure:
    
        Foldername is a valid UUID. 

        Mode        Length Name
        ----        ------ ----
        d-----             0135b681-5a76-4824-b7fa-0c492df3182d
        d-----             0135b681-5a76-4824-b7fa-0c492df3182d/metadata
        ------      19593  0135b681-5a76-4824-b7fa-0c492df3182d/metadata/metadata.xml
        d-----             0135b681-5a76-4824-b7fa-0c492df3182d/private
        d-----             0135b681-5a76-4824-b7fa-0c492df3182d/public
        ------      858    0135b681-5a76-4824-b7fa-0c492df3182d/info.xml
    """
    li_metadata_folders = []
    # parse folder structure
    for subfolder in folder.glob("**"):
        # if foldername is a valid UUID, it's a geosource subfolder
        try:
            UUID(subfolder.name)
        except ValueError:
            continue
        # check if required subfolders are present
        if not check_folder_structure(subfolder):
            logging.info("Folder ignored because of bad structure.")
            continue
        # check if required metadata.xml is present
        if not get_md_path(subfolder):
            logging.info("Folder ignored because of missing metadata file.")
            continue
        # append to the list
        li_metadata_folders.append(subfolder.resolve())
    return tuple(li_metadata_folders)


def check_folder_structure(folder: str, kind: str = "geosource") -> bool:
    """Check folder structure.

    :param str folder: path to the folder to check.
    :param str kind: tool structure to check. Until now, only geosource.
    """
    subfolders = [x.name for x in folder.iterdir() if x.is_dir()]
    return set(["metadata", "private", "public"]).issubset(subfolders)


def get_md_global_info(folder: str) -> tuple:
    """Extract required information from the info.xml expected to be at the
    root fo each metadata folder.

    :param str folder: path to the folder where to look for the info.xml file.
    
    Structure of the returned tuple:

        (catalog UUID,
         absolute path to the metadata.xml,
         metadata type (ISO number),
         list of absolute paths to attached files   
         )
    """
    # get metadata path
    md_path = get_md_path(folder)
    # get info file
    info_path = folder / "info.xml"
    if not info_path.is_file():
        logging.error("Info file not found.")
        return False

    # read info.xml
    info_xml = etree.parse(str(info_path))

    # store global data
    cat_uuid = info_xml.xpath("/info/general/siteId/text()")[0]  # catalog identifier
    md_type = info_xml.xpath("/info/general/schema/text()")[0]  # ISO number

    # list attached files (public and private) and keep only existing files
    l_files_pub = info_xml.xpath("/info/public/file")  # public markup
    l_files_priv = info_xml.xpath("/info/private/file")  # private markup

    l_files = [
        Path(folder / "public" / x.get("name"))
        for x in l_files_pub
        if Path(folder / "public" / x.get("name")).is_file()
    ]
    l_files.extend(
        [
            Path(folder / "private" / x.get("name")).resolve()
            for x in l_files_priv
            if Path(folder / "private" / x.get("name")).is_file()
        ]
    )

    return (cat_uuid, md_path, md_type, l_files)


def get_md_path(folder: str) -> tuple:
    """Return absolute path to the input metadata.xml file expected to be stored
    into the 'metadata/metadata.xml' subfolder within  each metadata folder.

    :param str folder: path to the folder where to look for the metadata/metadata.xml file.
    """
    # check expected path
    md_path = folder / "metadata" / "metadata.xml"
    if not md_path.is_file():
        logging.error("No metadata file found in {}".format(md_path.resolve()))
        return False

    return md_path.resolve()


def get_metadata(metadata_path: str, metadata_type: str = "iso19139") -> tuple:
    """Load metadata as an object and get required information (title, SRS...).

    :param str metadata_path: path to the metadata.
    :param str metadata_type: type of metadata. iso19139 or iso19110.
    """
    # load depending on the ISO format
    if metadata_type == "iso19139":
        md = MetadataIso19139(xml=metadata_path)
        d_md = {"title": md.title}
    elif metadata_type == "iso19110":
        md = MetadataIso19110(xml=metadata_path)
        d_md = {"title": md.name}
    else:
        logging.warning("Metadata type not supported: {}".format(metadata_type))
        return False

    #
    return d_md


# #############################################################################
# ####### Command-line ############
# #################################
@click.command()
@click.option(
    "--input_dir",
    default=r"input",
    help="Path to the input folder. Default: './input'.",
)
@click.option(
    "--output_dir",
    default=r"output",
    help="Path to the output folder. Default: './output'.",
)
@click.option("--csv", default=1, help="Summarize into a CSV file. Default: True.")
@click.option(
    "--limit",
    default=None,
    help="Parse only the specified number of files (useful for tests). Leave blank for no limit (default).",
)
@click.option("--log", default="DEBUG", help="Log level. Default: ERROR.")
def cli_switch_from_geosource(input_dir, output_dir, csv, limit, log):
    """
    """
    # logging option
    logging.basicConfig(
        format="%(asctime)s || %(levelname)s "
        "|| %(module)s || %(funcName)s || %(lineno)s "
        "|| %(message)s",
        level=log,
    )
    #
    input_folder = Path(input_dir)
    if not input_folder.exists():
        raise IOError("Input folder doesn't exist.")
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    # get list of metadata
    li_metadata_folders = list_metadata_folder(input_folder)
    logging.info(
        "{} compatible metadata folders found.".format(len(li_metadata_folders))
    )
    # guess if it's a 19110 or a 19139 metadata
    d_metadata = {i: get_md_global_info(i) for i in li_metadata_folders}
    # csv report
    if not csv:
        logging.debug("CSV export disabled.")
    csv_report = CsvReporter(
        csvpath=Path("./report.csv"),
        headers=["name", "filename", "title", "format", "Format"],
    )

    # parse dict
    with click.progressbar(
        d_metadata, label="Parsing metadata...", length=len(d_metadata)
    ) as dico_mds:
        for i in dico_mds:
            # print(i)
            # print(d_metadata.get(i)[2], get_md_title(
            #     d_metadata.get(i)[1], d_metadata.get(i)[2]))
            # print(d_metadata.get(i)[0], d_metadata.get(i)[2])

            # ensure that the dest folder is created
            dest_dir = output_dir.joinpath(d_metadata.get(i)[0], d_metadata.get(i)[2])
            dest_dir.mkdir(parents=True, exist_ok=True)
            # format output filename
            try:
                md = get_metadata(d_metadata.get(i)[1], d_metadata.get(i)[2])
            except Exception as err:
                logging.error(
                    "Parsing {} returned an error: {}".format(d_metadata.get(i)[1], err)
                )
                continue
            # print(md)
            if not md:
                continue
            md_title = md.get("title")
            if not md_title:
                md_title = "NoTitle"
                logging.warning("Title is missing: {}".format(d_metadata.get(i)[1]))
            dest_filename = dest_dir.joinpath(
                re.sub(r"[^\w\-_\. ]", "", md_title) + ".xml"
            )
            # copy
            # print(dest_filename.resolve())
            shutil.copy(str(d_metadata.get(i)[1]), str(dest_filename.resolve()))

            # report
            if csv:
                csv_report.add_unique(md)


# #############################################################################
# ### Stand alone execution #######
# #################################

if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    cli_switch_from_geosource()
