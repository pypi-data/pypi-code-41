from zipfile import ZipFile
from trydjango.settings import MEDIA_ROOT
import nmrglue as ng
import os
from django.core.exceptions import ValidationError


# zip file validation
def validate_zip_file(value):

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.zip']            # zip only
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension. zip file only for spectrum data.')
    # read the data with nmrglue
    with ZipFile(value) as zipfile:
        # get the list of files
        list = zipfile.namelist()
        path = os.path.join(MEDIA_ROOT, "spectrum")
        zipfile.extractall(path=path)
        path = os.path.join(path, list[0])
        try:
            ng.bruker.read_pdata(path)
        except:
            raise ValidationError(u'File structure error.')
        # try to look for baseline value
        try:
            os.path.join(path, "clevels")
        except:
            raise ValidationError(u'File incomplete error.')


# tsv file validation
def validate_tsv_file(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.tsv']            # tsv only
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension. tsv file only for peaks data')