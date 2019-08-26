# -*- coding: utf-8 -*-
"""Stream section module.

contains PSStreamSection
"""

from time import time
from puzzlestream.backend.dict import PSDict
from puzzlestream.backend.reference import PSCacheReference
from puzzlestream.backend.stream import PSStream


class PSStreamSection:
    """Stream section class - a view on the stream.

    A stream section is basically a view on one puzzle item's section of the
    stream. It holds the data itself (.data, a PSDict) as well as a record of
    all changes, the change log.
    """

    def __init__(self, sectionID: int, stream: PSStream):
        """Stream section init.

        Args:
            sectionID (int): ID of the puzzle item this section belongs to.
            stream (PSStream): The current Puzzlestream stream instance.
        """
        self.__stream = stream
        self.__id = sectionID
        self.changelog = {}

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return str(self.data)

    @property
    def id(self) -> int:
        """ID of the puzzle item this section belongs to."""
        return self.__id

    def updateData(self, lastStreamSectionID: int, data: PSDict, log: list,
                   clean: bool = False):
        """Update section data and log changes.

        Args:
            lastStreamSectionID (int): Previous section; may be referenced.
            data (PSDict): Data to be stored.
            log (list): List of items changed.
            clean (bool): Whether the stream should be cleared from outdated
                stuff after updating.
        """
        for key in data:
            if (key in self.changelog and key not in log and not
                    isinstance(data.__getitem__(key, traceback=False),
                               PSCacheReference)
                ):
                ref = PSCacheReference(lastStreamSectionID)
                if key in data:
                    del data[key]
                data[key] = ref

        for key in data:
            self.__stream.setItem(self.__id, key, data[key])

        self.__logChanges(log)
        if clean:
            self.__cleanStream(self.changelog)

    def __cleanStream(self, log: dict):
        """Clean stream from outdated elements."""
        for key in self.__stream:
            ID = key.split("-")[0]
            keyn = key[len(ID) + 1:]

            if keyn not in log and int(ID) == self.__id:
                del self.__stream[key]

    def __logChanges(self, log: dict):
        """Update change log."""
        for item in log:
            if (item in self.changelog and
                    self.__id not in self.changelog[item]):
                self.changelog[item].append(self.__id)
            else:
                self.changelog[item] = [self.__id]
        self.data.resetChangelog()

    @property
    def data(self) -> PSDict:
        """Stream section data (PSDict)."""
        return PSDict(self.__id, self.__stream)

    def addSection(self, streamSection):
        """Add data of other stream section to this one, update change log.

        Args:
            streamSection (PSStreamSection): Section to be added.
        """
        for key in list(streamSection.changelog.keys()):
            if key in streamSection.data:
                if isinstance(
                    streamSection.data.__getitem__(key, traceback=False),
                    PSCacheReference
                ):
                    self.__stream.setItem(
                        self.__id, key,
                        streamSection.data.__getitem__(key, traceback=False)
                    )
                else:
                    ref = PSCacheReference(streamSection.id)
                    self.__stream.setItem(self.__id, key, ref)
            else:
                del streamSection.changelog[key]
        self.changelog.update(streamSection.changelog)

    def copy(self, sectionID: int):
        """Return a copy of this section.

        Args:
            sectionID (int): ID of the new section.

        Returns:
            Copy of this section with indicated section ID (PSStreamSection).
        """
        new = PSStreamSection(sectionID, self.__stream)
        new.addSection(self)
        return new

    def connect(self, item):
        for key in self.__stream:
            ID = key.split("-")[0]
            keyn = key[len(ID) + 1:]
            if int(ID) == item.id and keyn not in self.data:
                if (key in self.__stream.references and
                        isinstance(self.__stream[key], PSCacheReference)):
                    self.__stream.setItem(self.id, keyn, self.__stream[key])
                else:
                    ref = PSCacheReference(item.id)
                    self.__stream.setItem(self.id, keyn, ref)

    def disconnect(self, item):
        for key in self.__stream:
            ID = key.split("-")[0]
            if (key in self.__stream.references and
                    isinstance(self.__stream[key], PSCacheReference)):
                if (int(ID) == self.__id or
                        self.__stream[key].sectionID == item.id or
                        self.__stream[key].sectionID == self.__id):
                    del self.__stream[key]
