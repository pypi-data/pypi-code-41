from abc import ABC, abstractmethod

from cmt.a_map import AMap


class AConverter(ABC):
    @staticmethod
    @abstractmethod
    def convert(source: AMap) -> AMap:
        """
        Convert to the other map format of same version.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def downgrade(source: AMap) -> AMap:
        """
        Downgrade to the format version below.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def upgrade(source: AMap) -> AMap:
        """
        Upgrade to the format version above.
        """
        raise NotImplementedError
