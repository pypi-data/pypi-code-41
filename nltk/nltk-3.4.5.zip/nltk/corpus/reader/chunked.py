# Natural Language Toolkit: Chunked Corpus Reader
#
# Copyright (C) 2001-2019 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Edward Loper <edloper@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
A reader for corpora that contain chunked (and optionally tagged)
documents.
"""

import os.path, codecs

from six import string_types

import nltk
from nltk.corpus.reader.bracket_parse import BracketParseCorpusReader
from nltk.tree import Tree
from nltk.tokenize import *
from nltk.chunk import tagstr2tree
from nltk.corpus.reader.util import *
from nltk.corpus.reader.api import *


class ChunkedCorpusReader(CorpusReader):
    """
    Reader for chunked (and optionally tagged) corpora.  Paragraphs
    are split using a block reader.  They are then tokenized into
    sentences using a sentence tokenizer.  Finally, these sentences
    are parsed into chunk trees using a string-to-chunktree conversion
    function.  Each of these steps can be performed using a default
    function or a custom function.  By default, paragraphs are split
    on blank lines; sentences are listed one per line; and sentences
    are parsed into chunk trees using ``nltk.chunk.tagstr2tree``.
    """

    def __init__(
        self,
        root,
        fileids,
        extension='',
        str2chunktree=tagstr2tree,
        sent_tokenizer=RegexpTokenizer('\n', gaps=True),
        para_block_reader=read_blankline_block,
        encoding='utf8',
        tagset=None,
    ):
        """
        :param root: The root directory for this corpus.
        :param fileids: A list or regexp specifying the fileids in this corpus.
        """
        CorpusReader.__init__(self, root, fileids, encoding)
        self._cv_args = (str2chunktree, sent_tokenizer, para_block_reader, tagset)
        """Arguments for corpus views generated by this corpus: a tuple
        (str2chunktree, sent_tokenizer, para_block_tokenizer)"""

    def raw(self, fileids=None):
        """
        :return: the given file(s) as a single string.
        :rtype: str
        """
        if fileids is None:
            fileids = self._fileids
        elif isinstance(fileids, string_types):
            fileids = [fileids]
        return concat([self.open(f).read() for f in fileids])

    def words(self, fileids=None):
        """
        :return: the given file(s) as a list of words
            and punctuation symbols.
        :rtype: list(str)
        """
        return concat(
            [
                ChunkedCorpusView(f, enc, 0, 0, 0, 0, *self._cv_args)
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def sents(self, fileids=None):
        """
        :return: the given file(s) as a list of
            sentences or utterances, each encoded as a list of word
            strings.
        :rtype: list(list(str))
        """
        return concat(
            [
                ChunkedCorpusView(f, enc, 0, 1, 0, 0, *self._cv_args)
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def paras(self, fileids=None):
        """
        :return: the given file(s) as a list of
            paragraphs, each encoded as a list of sentences, which are
            in turn encoded as lists of word strings.
        :rtype: list(list(list(str)))
        """
        return concat(
            [
                ChunkedCorpusView(f, enc, 0, 1, 1, 0, *self._cv_args)
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def tagged_words(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of tagged
            words and punctuation symbols, encoded as tuples
            ``(word,tag)``.
        :rtype: list(tuple(str,str))
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 0, 0, 0, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def tagged_sents(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of
            sentences, each encoded as a list of ``(word,tag)`` tuples.

        :rtype: list(list(tuple(str,str)))
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 1, 0, 0, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def tagged_paras(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of
            paragraphs, each encoded as a list of sentences, which are
            in turn encoded as lists of ``(word,tag)`` tuples.
        :rtype: list(list(list(tuple(str,str))))
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 1, 1, 0, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def chunked_words(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of tagged
            words and chunks.  Words are encoded as ``(word, tag)``
            tuples (if the corpus has tags) or word strings (if the
            corpus has no tags).  Chunks are encoded as depth-one
            trees over ``(word,tag)`` tuples or word strings.
        :rtype: list(tuple(str,str) and Tree)
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 0, 0, 1, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def chunked_sents(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of
            sentences, each encoded as a shallow Tree.  The leaves
            of these trees are encoded as ``(word, tag)`` tuples (if
            the corpus has tags) or word strings (if the corpus has no
            tags).
        :rtype: list(Tree)
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 1, 0, 1, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def chunked_paras(self, fileids=None, tagset=None):
        """
        :return: the given file(s) as a list of
            paragraphs, each encoded as a list of sentences, which are
            in turn encoded as a shallow Tree.  The leaves of these
            trees are encoded as ``(word, tag)`` tuples (if the corpus
            has tags) or word strings (if the corpus has no tags).
        :rtype: list(list(Tree))
        """
        return concat(
            [
                ChunkedCorpusView(
                    f, enc, 1, 1, 1, 1, *self._cv_args, target_tagset=tagset
                )
                for (f, enc) in self.abspaths(fileids, True)
            ]
        )

    def _read_block(self, stream):
        return [tagstr2tree(t) for t in read_blankline_block(stream)]


class ChunkedCorpusView(StreamBackedCorpusView):
    def __init__(
        self,
        fileid,
        encoding,
        tagged,
        group_by_sent,
        group_by_para,
        chunked,
        str2chunktree,
        sent_tokenizer,
        para_block_reader,
        source_tagset=None,
        target_tagset=None,
    ):
        StreamBackedCorpusView.__init__(self, fileid, encoding=encoding)
        self._tagged = tagged
        self._group_by_sent = group_by_sent
        self._group_by_para = group_by_para
        self._chunked = chunked
        self._str2chunktree = str2chunktree
        self._sent_tokenizer = sent_tokenizer
        self._para_block_reader = para_block_reader
        self._source_tagset = source_tagset
        self._target_tagset = target_tagset

    def read_block(self, stream):
        block = []
        for para_str in self._para_block_reader(stream):
            para = []
            for sent_str in self._sent_tokenizer.tokenize(para_str):
                sent = self._str2chunktree(
                    sent_str,
                    source_tagset=self._source_tagset,
                    target_tagset=self._target_tagset,
                )

                # If requested, throw away the tags.
                if not self._tagged:
                    sent = self._untag(sent)

                # If requested, throw away the chunks.
                if not self._chunked:
                    sent = sent.leaves()

                # Add the sentence to `para`.
                if self._group_by_sent:
                    para.append(sent)
                else:
                    para.extend(sent)

            # Add the paragraph to `block`.
            if self._group_by_para:
                block.append(para)
            else:
                block.extend(para)

        # Return the block
        return block

    def _untag(self, tree):
        for i, child in enumerate(tree):
            if isinstance(child, Tree):
                self._untag(child)
            elif isinstance(child, tuple):
                tree[i] = child[0]
            else:
                raise ValueError('expected child to be Tree or tuple')
        return tree
