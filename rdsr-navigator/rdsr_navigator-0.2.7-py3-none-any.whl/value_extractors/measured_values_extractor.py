from rdsr_navigator.value_extractors.value_extractor_base import ValueExtractorBase

class MeasuredValuesExtractor(ValueExtractorBase):

    @staticmethod
    def can_extract(dicom_obj):
        if not hasattr(dicom_obj, 'MeasuredValueSequence'):
            return False
        
        if len(dicom_obj.MeasuredValueSequence) != 1:
            return False
        
        mv = dicom_obj.MeasuredValueSequence[0]
        if not hasattr(mv, 'MeasurementUnitsCodeSequence'):
            return False

        if not hasattr(mv, 'NumericValue'):
            return False

        mucs = mv.MeasurementUnitsCodeSequence
        if len(mucs) != 1:
            return False

        if not hasattr(mucs[0], 'CodeMeaning'):
            return False

        return True

    @staticmethod
    def extract_value(dicom_obj):
        mv = dicom_obj.MeasuredValueSequence[0]
        return (convert_to_number(mv.NumericValue), mv.MeasurementUnitsCodeSequence[0].CodeMeaning)

def convert_to_number(num):
    return float(num)
