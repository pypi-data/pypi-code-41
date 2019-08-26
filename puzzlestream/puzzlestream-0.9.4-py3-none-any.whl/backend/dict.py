# -*- coding: utf-8 -*-
"""Dictionary module.

contains PSDict
"""

from copy import copy

from puzzlestream.backend.reference import PSCacheReference
from puzzlestream.backend.stream import PSStream


class PSDict(dict):

    """Dictionary with some extra functionality.

    Python dictionary complemented by logging changes to the dict and getting
    and deleting items from stream; basically a view on the stream.
    """

    def __init__(self, sectionID: int, stream: PSStream,
                 changelog: list = [], data: dict = {}):
        """Dictionary initialisation.

        Args:
            sectionID (int): ID of the stream section the dict belongs to.
            stream (PSStream): Puzzlestream stream object.
            changelog (list): Initial change log.
            data (dict): Initial data.
        """
        self.__changelog = changelog
        self.__id, self.__stream = sectionID, stream

        super().__init__(data)

    def __iter__(self) -> str:
        """Iterate first over values in dict (RAM), then over stream.

        Yields:
            key (str): Key in dictionary / stream.
        """
        for key in super().__iter__():
            yield key

        for key in self.__stream:
            ID = key.split("-")[0]

            if int(ID) == self.__id:
                keyn = key[len(ID) + 1:]

                if (not super().__contains__(keyn) and
                        self.__stream.__contains__(key)):
                    yield keyn

    def __contains__(self, key: str) -> bool:
        """Checks if key in dict or the corresponding part of the stream.

        Args:
            key (str): key to check.

        Returns:
            Whether the key exists either in the dict or in the stream (bool).
        """
        return (super().__contains__(key) or
                self.__stream.__contains__(self.__streamKey(key)))

    def __delitem__(self, key: str):
        """Delete item from dict and corresponding part of the stream.

        Args:
            key (str): key of the item to delete.

        Raises:
            KeyError if item is not to be found in dict or stream.
        """
        if (not super().__contains__(key) and not
                self.__stream.__contains__(self.__streamKey(key))):
            raise KeyError(key)

        if super().__contains__(key):
            super().__delitem__(key)
        if self.__stream.__contains__(self.__streamKey(key)):
            self.deleteFromStream(key)

    def __streamKey(self, key: str) -> str:
        """Return stream key corresponding to key, e.g. x -> 1-x.

        Args:
            key (str): key to translate.

        Returns:
            Translated key (str).
        """
        return str(self.__id) + "-" + key

    def __getitem__(self, key: str, traceback: bool = True):
        """Get item `key` from this dict / the stream.

        Return item from RAM if possible, if not the item is loaded from the
        stream and stored in RAM for faster access later on.

        Args:
            key (str): Key of the item that is returned.

        Returns:
            data (:obj:): Object corresponding to `key`.
        """
        if super().__contains__(key) and traceback:
            data = super().__getitem__(key)
        elif self.__stream.__contains__(self.__streamKey(key)):
            data = self.__stream.getItem(self.__id, key)
            if traceback:
                if isinstance(data, PSCacheReference):
                    data = self.__stream.getItem(int(data), key)
            super().__setitem__(key, data)
        else:
            raise KeyError(key)
        return data

    def __setitem__(self, key: bool, value: object):
        """Store item and log key in changelog.

        Args:
            key (str): Key in dict / stream.
            value (:obj:): Object to be saved.
        """
        if key not in self.changelog:
            self.changelog.append(key)
        super().__setitem__(key, value)

    def deleteFromStream(self, key: str):
        """Delete item `key` from stream (and this dict).

        Args:
            key (str): key of the item to be deleted (not a stream key!)
        """
        if super().__contains__(key):
            super().__delitem__(key)
        del self.__stream[self.__streamKey(key)]

    def copy(self):
        """Return a copy of the dictionary.

        Returns:
            Copy of this dictionary (PSDict)
        """
        return copy(self)

    def reload(self):
        """Reload cached data from stream."""
        for key in list(super().keys()):
            if self.__stream.__contains__(self.__streamKey(key)):
                data = self.__stream.getItem(self.__id, key)
                if isinstance(data, PSCacheReference):
                    data = self.__stream.getItem(int(data), key)
                super().__setitem__(key, data)
            else:
                super().__delitem__(key)

    @property
    def changelog(self) -> list:
        """List, contains keys changed since last reset."""
        return self.__changelog

    def resetChangelog(self):
        """Reset changelog to an empty list."""
        self.__changelog = []

    def cleanRam(self):
        """Delete everything from Ram."""
        super().clear()
