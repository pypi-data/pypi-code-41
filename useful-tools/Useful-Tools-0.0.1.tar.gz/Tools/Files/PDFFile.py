"""
Hello from Tools/Files/PDFFile.py

Functions:
    Merge
        Merge .pdf files.
    Demo
        This function is a demo of all functions and classes in this module.

Classes:
    PDFFile
        __init__
            Create a PDF file (.pdf) object.
        GetNumPages
            Get the number of pages of the .pdf file.
        GetOutlines
            Get the outlines of the .pdf file.
        GetPage
            Get a page of the .pdf file.
        GetInfo
            Get the document info of the .pdf file.
        AddBlankPage
            Add a blank page to the .pdf file.
        AddPage
            Add a page to the .pdf file.
        Save
            Save the .pdf file.
"""
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger


class PDFFile:
    def __init__(self, filename=None, mode="r"):
        """
        Create a PDF file (.pdf) object.

        Parameters
        ----------
        filename: str
            PDF file's (.pdf) name.
        mode
            The open mode, can be "r" or "w".
            "r" express read only, "w" express write only.
            If it's "r", then filename shouldn't be None.
            If it's "w", then filename should be None.

        Returns
        -------
        PDFFile
            Return its case.
        """
        assert mode in ["r", "w"]
        assert not (filename is None and mode == "r")
        assert not (filename is not None and mode == "w")
        self.__pdf_file_read = (PdfFileReader(open(filename, "rb"))
                                if mode == "r" else None)
        self.__pdf_file_write = PdfFileWriter()
        self.__mode = mode

    def GetNumPages(self):
        """
        Get the number of pages of the .pdf file.

        Returns
        -------
        int
            The number of pages.
        """
        if self.__mode == "r":
            return self.__pdf_file_read.getNumPages()
        else:
            return self.__pdf_file_write.getNumPages()

    def GetOutLines(self):
        """
        Get the outlines of the .pdf file.

        Returns
        -------
        list
            It's the outlines of the .pdf file.

        Raises
        ------
        AssertionError
            If the mode is "w", raise it.
        """
        assert self.__mode == "r"
        return self.__pdf_file_read.getOutlines()

    def GetPage(self, page_num):
        """
        Get a page of the .pdf file.

        Parameters
        ----------
        page_num: int
            The page number of the page you want to get.

        Returns
        -------
        PageObject
            It's a page you want to get.
        """
        if self.__mode == "r":
            return self.__pdf_file_read.getPage(page_num)
        else:
            return self.__pdf_file_write.getPage(page_num)

    def GetInfo(self):
        """
        Get the document info of the .pdf file.

        Returns
        -------
        DocumentInformation
            Return the document info of the .pdf file.

        Raises
        ------
        AssertionError
            If the mode is "w", raise it.
        """
        assert self.__mode == "r"
        return self.__pdf_file_read.getDocumentInfo()

    def AddBlankPage(self, width, height):
        """
        Add a blank page to the .pdf file.

        Parameters
        ----------
        width: int
            The width of the blank page.
        height: int
            The height of the blank page.

        Returns
        -------
        PageObject
            It's the blank page.
        """
        assert self.__mode == "w"
        return self.__pdf_file_write.addBlankPage(width, height)

    def AddPage(self, page):
        """
        Add a page to the .pdf file.

        Parameters
        ----------
        page: PageObject
            It's a page you want to add.
        """
        assert self.__mode == "w"
        self.__pdf_file_write.addPage(page)

    def Save(self, filename):
        """
        Save the .pdf file.

        Parameters
        ----------
        filename: str
            The filename you want to save.
        """
        assert self.__mode == "w"
        self.__pdf_file_write.write(open(filename, "wb"))


def Merge(filenames, output_filename):
    """
    Merge .pdf files.

    Parameters
    ----------
    filenames: list of str
        list of filenames.
    output_filename: str
        It is the path to store merged .pdf files.
    """
    merger = PdfFileMerger()
    for i in filenames:
        merger.append(PdfFileReader(open(i, "rb")))
    merger.write(output_filename)
    merger.close()


def Demo():
    """This function is a demo of all functions and classes in this module."""
    pdf_file = PDFFile("E:/pdf.pdf")
    print(pdf_file.GetNumPages())
    print(pdf_file.GetOutLines())
    page = pdf_file.GetPage(2)
    print(page)
    info = pdf_file.GetInfo()
    print(info.title)
    print(info.author)

    pdf_file = PDFFile(mode="w")
    print(pdf_file.AddBlankPage(1, 111))
    pdf_file.AddPage(page)
    pdf_file.Save("E:/pdf2.pdf")

    Merge(['E:/pdf.pdf', 'E:/pdf2.pdf'], "E:/merged.pdf")


if __name__ == '__main__':
    Demo()
