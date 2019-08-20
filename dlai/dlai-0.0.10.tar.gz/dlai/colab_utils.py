import re
import os
import shutil
import doctest
from typing import Optional



def setup_kaggle() -> None:
    """
    Function is used to setup Kaggle environment for dataset or competition downloading.
    """
    x = [f for f in os.listdir(os.curdir) if re.search('kaggle.*\.json', f)]
    assert len(x) == 1, 'Too much kaggle.json files'
    assert re.match('kaggle.*\.json', x[0]), 'Upload kaggle.json file'
    if not os.path.exists('/root/.kaggle'):
        os.makedirs('/root/.kaggle')
    shutil.move(x[0], '/root/.kaggle/kaggle.json')
    os.chmod('/root/.kaggle/kaggle.json', 0o600)


def download_kaggle_data(COMPETITION: Optional[str]=None, DATA_DIR: Optional[str]=None) -> None:
    """
    Downloads datasets from Kaggle.
    :param COMPETITION: Kaggle command to download datasets.
    :param DATA_DIR: Directory where to save files. If not specified, files are saved in working directory.
    :return: Downloads files.
    """
    if COMPETITION:
        if not DATA_DIR:
            os.system(COMPETITION)
        else:
            os.system('{} --unzip -p {}'.format(COMPETITION, str(DATA_DIR)))


def unarchive_data(
        FILES_TO_UNZIP: Optional[list]=None,
        DATA_DIR: Optional[str]=None,
        USE_SUBFOLDERS: Optional[bool]=False,
    ) -> None:
    """
    Used to unarchive specified files.
    :param FILES_TO_UNZIP: list of files to unarchive.
    :param DATA_DIR: directory where to save unarcjived data.
    :param USE_SUBFOLDERS: If True creates subfolders for data item. Default: False.
    :return: None
    """
    for filename in FILES_TO_UNZIP:
        # TODO path or string and destination folder
        if USE_SUBFOLDERS:
            # TODO add tar and etc
            dir_name = filename.split('.')[0]
        else:
            dir_name = ''
        shutil.unpack_archive(str(DATA_DIR/filename), extract_dir=str(DATA_DIR/dir_name))



if __name__ == '__main__':
    download_kaggle_data()