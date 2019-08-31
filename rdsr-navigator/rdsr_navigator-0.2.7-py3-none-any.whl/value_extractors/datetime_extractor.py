from rdsr_navigator.value_extractors.value_extractor_base import ValueExtractorBase

class DateTimeExtractor(ValueExtractorBase):

    @staticmethod
    def can_extract(dicom_obj):
        return hasattr(dicom_obj, 'DateTime')

    @staticmethod
    def extract_value(dicom_obj):
        return dicom_obj.DateTime
