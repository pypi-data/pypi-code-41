from abc import ABC, abstractmethod

class ValueExtractorBase(ABC):

    @staticmethod
    @abstractmethod
    def can_extract(dicom_obj):
        pass

    @staticmethod
    @abstractmethod
    def extract_value(dicom_obj):
        pass
