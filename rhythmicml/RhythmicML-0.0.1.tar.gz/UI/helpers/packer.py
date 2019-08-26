from rhythmic.general import faultReturnHandler;
from zipfile import ZipFile, ZIP_DEFLATED;

@faultReturnHandler
def packFiles(folder_path, archive_absolute_path, files_list_dictionary):
    """
    packFiles(folder_path, archive_absolute_path, files_list_dictionary)

    folder_path - a folder scanned with scan_folder.scanModelFolder to get files_list;
    files_list_dictionary - dictionaries, containing "file_path" items with "absolute_path" field: {"file-path": path [,... ]}
    (see helpers/os_files_operations.py)
    """
    relative_index = len(folder_path) + 1;

    with ZipFile(archive_absolute_path, mode = 'w', compression = ZIP_DEFLATED) as version_zip:

        for item_path in files_list_dictionary:
            item = files_list_dictionary[item_path];
            version_zip.write(item["absolute_path"], item["absolute_path"][relative_index:]);

    return "[ {} ] packed to [ {} ]".format(folder_path, archive_absolute_path);

@faultReturnHandler
def unpackSingleFile(archive_absolute_path, file_to_unpack_absolute_path, model_path):
    
    archive_member_to_unpack = file_to_unpack_absolute_path[ len(model_path) + 1: ];
    
    with ZipFile(archive_absolute_path) as version_package:
        version_package.extract(archive_member_to_unpack, model_path)

    return archive_member_to_unpack;

@faultReturnHandler
def unpackVersion(archive_absolute_path, model_path):

    with ZipFile(archive_absolute_path) as version_package:
        version_package.extractall(model_path)

    return True;