from rdsr_navigator.value_extractors.value_extractor_base import ValueExtractorBase

class TextValueExtractor(ValueExtractorBase):

    @staticmethod
    def can_extract(dicom_obj) -> bool:
        return hasattr(dicom_obj, 'TextValue')

    @staticmethod
    def extract_value(dicom_obj):
        return str(dicom_obj.TextValue)
