"""
Hello from Tools/Files/WordFile.py

Functions:
    Demo
        This function is a demo of all functions and classes in this module.

Classes:
    WordFile
        __init__
            Create a Word file (.docx) object.
        ToPDF
            Converting Word documents in .docx format into .pdf documents.
"""
from win32com.client import Dispatch, constants, gencache
import pythoncom
import os.path


class WordFile:
    """
    Word (.docx) File Object.
    """
    def __init__(self, filename):
        """
        Create a Word file (.docx) object.

        Parameters
        ----------
        filename: str
            Word file's (.docx) name.

        Returns
        -------
        WordFile
            Return its case.

        Raises
        ------
        AssertionError
            If the file does not exist and the suffix is not '.docx', raise it.
        """
        assert os.path.isfile(filename)
        assert filename.endswith(".docx")
        self.__filename = filename

    def ToPDF(self, pdf_file_name):
        """
        Converting Word documents in .docx format into .pdf documents.

        Parameters
        ----------
        pdf_file_name: str
            This is where the converted .pdf file is stored,
            such as E:/pdf_file/convert.pdf.

        Returns
        -------
        bool
            If the conversion is successful, return True, otherwise False.
        """
        try:
            pythoncom.CoInitialize()
            gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
            w = Dispatch("Word.Application")
            try:
                doc = w.Documents.Open(self.__filename, ReadOnly=1)
                doc.ExportAsFixedFormat(pdf_file_name, constants.wdExportFormatPDF,
                                        Item=constants.wdExportDocumentWithMarkup,
                                        CreateBookmarks=constants.
                                        wdExportCreateHeadingBookmarks)
                w.Quit(constants.wdDoNotSaveChanges)
                return True
            except Exception:
                return False
        except Exception:
            return False


def Demo():
    """This function is a demo of all functions in this module."""
    word_file = WordFile("E:/doc.docx")
    print(word_file.ToPDF("E:/pdf.pdf"))


if __name__ == '__main__':
    Demo()
