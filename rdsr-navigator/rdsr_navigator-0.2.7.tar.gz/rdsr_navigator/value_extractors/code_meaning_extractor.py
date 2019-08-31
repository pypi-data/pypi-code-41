from rdsr_navigator.value_extractors.value_extractor_base import ValueExtractorBase

class CodeMeaningExtractor(ValueExtractorBase):

    @staticmethod
    def can_extract(dicom_obj):

        if not hasattr(dicom_obj, 'ConceptCodeSequence'):
            return False

        if len(dicom_obj.ConceptCodeSequence) != 1:
            return False

        if not hasattr(dicom_obj.ConceptCodeSequence[0], 'CodeMeaning'):
            return False

        return True

    @staticmethod
    def extract_value(dicom_obj):
        code_sequence = dicom_obj.ConceptCodeSequence
        return code_sequence[0].CodeMeaning
