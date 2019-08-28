from urllib.request import urlopen
from batchgenerators.utilities.file_and_folder_operations import *
from hd_glio.paths import folder_with_parameter_files
import shutil
import zipfile


def maybe_download_weights():
    if not isfile(join(folder_with_parameter_files, 'fold_0', "model_best.model")) or not \
            isfile(join(folder_with_parameter_files, 'fold_0', "model_best.model.pkl")):
        if isdir(folder_with_parameter_files):
            shutil.rmtree(folder_with_parameter_files)
        maybe_mkdir_p(folder_with_parameter_files)

        out_filename = join(folder_with_parameter_files, "parameters.zip")

        if not os.path.isfile(out_filename):
            url = "https://zenodo.org/record/3380272/files/hd_glio_params.zip?download=1"
            print("Downloading", url, "...")
            data = urlopen(url).read()
            with open(out_filename, 'wb') as f:
                f.write(data)

        zipfile.ZipFile(out_filename).extractall(path=folder_with_parameter_files)
        os.remove(out_filename)

