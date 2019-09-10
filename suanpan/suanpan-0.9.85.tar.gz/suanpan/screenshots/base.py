# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.state.base import IndexSaver, TimeSaver
from suanpan.state.storage import StorageSaver
from suanpan.storage import storage
from suanpan.utils import image


class ScreenshotsSaver(StorageSaver):
    def update(self, imageOrPath):
        data = image.read(imageOrPath) if isinstance(imageOrPath, str) else imageOrPath
        self.current.localPath = storage.getPathInTempStore(self.current.storageName)
        storageName = storage.storagePathJoin(
            self.current.storageName, self.currentPattern
        )
        localPath = storage.localPathJoin(self.current.localPath, self.currentPattern)
        image.save(localPath, data, self.current.get("flag"))
        return storage.upload(storageName, localPath)


class ScreenshotsIndexSaver(ScreenshotsSaver, IndexSaver):
    PATTERN = "screenshot_{index}.png"


class ScreenshotsTimeSaver(ScreenshotsSaver, TimeSaver):
    PATTERN = "screenshot_{time}.png"
