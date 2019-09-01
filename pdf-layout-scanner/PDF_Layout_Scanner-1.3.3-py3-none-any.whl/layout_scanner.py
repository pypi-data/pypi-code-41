#!/usr/bin/python3

import sys
import os
from tqdm import tqdm
from binascii import b2a_hex
import pandas as pd
import pickle
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar, LTPage
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
formatter = Formatter('%(asctime)s %(name)s[%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")
logger = getLogger(__name__)
logger.setLevel(INFO)
handler = StreamHandler()
handler.setLevel(logger.getEffectiveLevel())
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

def with_pdf(pdf_doc, fn, pdf_pwd, *args, logger=logger):
    """Open the pdf document, and apply the function, returning the results"""
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, "rb")
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser, pdf_pwd)
        # connect the parser and document objects
        parser.set_document(doc)

        if doc.is_extractable:
            # apply the function and return the result
            result = fn(doc, *args)

        # close the pdf file
        fp.close()
    except IOError:
        # the file doesn't exist or similar problem
        logger.warn('Failed to open {}'.format(pdf_doc))
        pass
    return result


# Table of Contents
def _parse_toc(doc):
    """With an open PDFDocument object, get the table of contents (toc) data
    [this is a higher-order function to be passed to with_pdf()]"""
    toc = []
    try:
        outlines = doc.get_outlines()
        for (level, title, dest, a, se) in outlines:
            toc.append((level, title))
    except PDFNoOutlines:
        pass
    return toc


def get_toc(pdf_doc, pdf_pwd=""):
    """Return the table of contents (toc), if any, for this pdf file"""
    return with_pdf(pdf_doc, _parse_toc, pdf_pwd)


# Extracting Images
def write_file(folder, filename, filedata, flags="w"):
    """Write the file data to the folder and filename combination
    (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
    if os.path.isdir(folder):
        file_obj = open(os.path.join(folder, filename), flags)
        file_obj.write(filedata)
        file_obj.close()

def determine_image_type(stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = str(b2a_hex(stream_first_4_bytes))
    if bytes_as_hex.startswith("ffd8"):
        file_type = ".jpeg"
    elif bytes_as_hex == "89504e47":
        file_type = ".png"
    elif bytes_as_hex == "47494638":
        file_type = ".gif"
    elif bytes_as_hex.startswith("424d"):
        file_type = ".bmp"
    return file_type


def save_image(lt_image, page_number, images_folder):
    """Try to save the image data from this LTImage object, and return the file name, if successful"""
    if not lt_image.stream: raise RuntimeError

    file_stream = lt_image.stream.get_rawdata()
    if not file_stream: raise RuntimeError

    file_ext = determine_image_type(file_stream[0:4])
    if not file_ext: raise RuntimeError

    file_name = "".join([str(page_number), "_", lt_image.name, file_ext])
    write_file(images_folder, file_name, file_stream, flags="wb")
    return file_name


# Extracting Text
def to_bytestring(s, enc="utf-8"):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)


def update_page_text(
        df, lt_obj, pct=0.2, additional_grouping=True, separate_lines=False,
        logger=logger,
):
    """
    Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash

    df:
        cols = [x0, y0, x1, y1, class, objs, str]
    """
    if df is None: df = pd.DataFrame(columns=['x0', 'y0', 'x1', 'y1', 'class', 'objs', 'str'])

    if isinstance(lt_obj, (LTTextLine)):
        store_new_line(df, lt_obj, pct, additional_grouping=additional_grouping, logger=logger)
    elif isinstance(lt_obj, LTTextBox):
        if separate_lines:
            for line in lt_obj:
                update_page_text(
                    df, lt_obj=line, pct=pct, additional_grouping=additional_grouping,
                    separate_lines=separate_lines, logger=logger,
                )
        else:
            store_new_line(df, lt_obj, pct, additional_grouping=additional_grouping, logger=logger)
    else:
        raise NotImplementedError(lt_obj)
    return df

def store_new_line(df, lt_obj, pct, additional_grouping=True, logger=logger):
    '''
    store a new line to df
    '''
    x0, y0, x1, y1 = lt_obj.bbox
    candidates = df[
        (df['class'] == lt_obj.__class__)
        & (df['x0'] >= x0 * (1 - pct))
        & (df['x0'] <= x0 * (1 + pct))
        & (df['x1'] >= x1 * (1 - pct))
        & (df['x1'] <= x1 * (1 + pct))
        & (df['y1'] <= y0)
    ]

    if (candidates.shape[0] > 0) & additional_grouping:
        if candidates.shape[0] > 1:
            logger.warn('candidates has shape {}'.format(candidates.shape))
        target = candidates.iloc[0]
        old_y1 = df.at[target.name, 'y1']
        df.at[target.name, 'y1'] = y1
        df.at[target.name, 'objs'].append(lt_obj)
        df.at[target.name, 'str'].append(to_bytestring(lt_obj.get_text()))
        logger.info('Manually Merged y1: {} -> {}'.format(old_y1, y1))
    else:
        df.loc[0 if pd.isnull(df.index.max()) else df.index.max() + 1] = [
            *lt_obj.bbox, lt_obj.__class__, [lt_obj], [to_bytestring(lt_obj.get_text())]
        ]
    return df

def parse_lt_objs(
        lt_objs, page_number, images_folder, text_content=None,
        return_df=False, progressbar=False, page_id=None, page_size=None,
        additional_grouping=True, separate_lines=False,
        logger=logger,
):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    if text_content is None:
        text_content = []

    if progressbar:
        generator = tqdm(lt_objs, desc='parse objs')
    else:
        generator = lt_objs

    page_text = None
    # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in generator:
        if isinstance(lt_obj, (LTTextBox, LTTextLine, LTChar)):
            # text, so arrange is logically based on its column width
            page_text = update_page_text(
                page_text, lt_obj,
                additional_grouping=additional_grouping,
                separate_lines=separate_lines,
            )
        elif isinstance(lt_obj, LTImage):
            # an image, so save it to the designated folder, and note its place in the text
            try:
                saved_file = save_image(lt_obj, page_number, images_folder)
                # use html style <img /> tag to mark the position of the image within the text
                text_content.append(
                    '<img src="' + os.path.join(images_folder, saved_file) + '" />'
                )
            except (IOError, RuntimeError):
                logger.error("failed to save image on page{} {}".format(page_number, lt_obj))
        elif isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            text_content.append(
                parse_lt_objs(
                    lt_obj, page_number, images_folder, text_content,
                    return_df=return_df, progressbar=progressbar,
                    additional_grouping=additional_grouping,
                    separate_lines=separate_lines,
                )
            )

    if page_text is None:
        if return_df:
            return pd.DataFrame()
        else: return ''

    if return_df:
        text_content.append(page_text)
        page_content = pd.concat(text_content, ignore_index=True)
        if page_id is not None:
            page_content['page'] = page_id
        if page_size is not None:
            page_content['page_size'] = [page_size] * len(page_content)
        return page_content
    else:
        page_text = page_text.sort_values('y0')
        page_text = page_text['str'].apply(lambda x: text_content.append(''.join(x)))
        return "\n".join(text_content)


# Processing Pages
def _parse_pages(doc, images_folder, return_df=False, progressbar=False, separate_lines=False, additional_grouping=True):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()

    laparams = LAParams(detect_vertical=True, all_texts=True)
    # all_texts will enable layout analysis in LTFigure objs
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    if progressbar: generator = tqdm(enumerate(PDFPage.create_pages(doc)), desc='pages')
    else: generator = enumerate(PDFPage.create_pages(doc))

    text_content = []
    for i, page in generator:
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(
            parse_lt_objs(
                layout, (i + 1), images_folder,
                return_df=return_df,
                progressbar=progressbar,
                page_id=i, page_size=page.cropbox,
                additional_grouping=additional_grouping,
                separate_lines=separate_lines,
            )
        )

    if return_df: return pd.concat(text_content, ignore_index=True)
    else: return text_content

def _get_ltcontainer(doc):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()

    laparams = LAParams(detect_vertical=True, all_texts=True)
    # all_texts will enable layout analysis in LTFigure objs
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(layout)

    return text_content

def _get_page_size(doc):
    '''get page size'''

    sizes = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        sizes.append(page.cropbox)
    return sizes


def get_pages(
        pdf_doc, pdf_pwd="", images_folder="/tmp",
        return_df=False, progressbar=False, separate_lines=False,
        additional_grouping=True,
):
    """
    Process each of the pages in this pdf file and
    return a list of strings representing the text found in each page

    Args:
        pdf_doc: pdf file
        pdf_pwd: password if necessary
        images_folder: the directory where figures are saved
        return_df: whether you want a result in a Dataframe or not
        progressbar: whether not to show the progressbar
        separate_lines: group lines or not
        additional_grouping: if True, group the lines regarding
            the predefined rules
    """
    return with_pdf(
        pdf_doc, _parse_pages, pdf_pwd, images_folder,
        return_df, progressbar, separate_lines, additional_grouping
    )

def get_sizes(pdf_doc, pdf_pwd=""):
    '''get the sizes of each page'''
    return with_pdf(pdf_doc, _get_page_size, pdf_pwd)

def get_ltcontainer(pdf_doc, pdf_pwd=''):
    '''
    get the raw ltcontainer.
    '''
    return with_pdf(pdf_doc, _get_ltcontainer, pdf_pwd)
