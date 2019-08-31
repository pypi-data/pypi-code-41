from typing import List, Iterator, Union
from rdsr_navigator.concept_name import ConceptName
from rdsr_navigator.repr_display import reper_html
from rdsr_navigator.sr_exceptions import SrMissingContentException
import rdsr_navigator.value_extractors as ves

_VALUE_EXTRACTORS: List[ves.ValueExtractorBase] = [ves.CodeMeaningExtractor(),
                                                   ves.MeasuredValuesExtractor(),
                                                   ves.TextValueExtractor(),
                                                   ves.UidExtractor(),
                                                   ves.DateTimeExtractor()]

class SrElement:
    def __init__(self, dicom_data) -> None:
        self._dicom_data = dicom_data

    def __str__(self) -> str:
        return str(self.concept_name)

    def __repr__(self) -> str:
        return repr(self.concept_name)

    def __getitem__(self, concept_names: Union[str, List[str]]) -> 'SrElement':
        if isinstance(concept_names, str):
            return self.get(concept_names)

        return self.get(*concept_names)

    def __truediv__(self, concept_name) -> 'SrElement':
        return self.get(concept_name)

    def __floordiv__(self, concept_name) -> Iterator['SrElement']:
        return self.get_all(concept_name)

    # Jupyter integration.
    def _repr_html_(self) -> str:
        header = ('Code Value', 'Coding Scheme Designator', 'Code Meaning', 'Value')
        table_rows = [('-', '-', '-', self.value if self.value is not None else '')]
        
        for entry in self.content_it():
            concept_name = entry.concept_name
            value = '' if entry.value is None else entry.value
            table_rows.append((concept_name.code_value,
                               concept_name.coding_scheme_designator,
                               concept_name.code_meaning,
                               value))

        return reper_html(header, table_rows)

    def _ipython_key_completions_(self) -> List[str]:
        keys = []
        for c in self.content_it():
            cn = c.concept_name
            keys.extend([cn.code_meaning, cn.code_value_csd])

        return keys

    # Properties.
    @property
    def concept_name(self) -> ConceptName:
        '''
            Concept name of this instance.
        '''
        assert_concept_name_code_sequence(self._dicom_data)
        concept_name_code = self._dicom_data.ConceptNameCodeSequence[0]

        return ConceptName(code_value=concept_name_code.CodeValue,
                           code_meaning=concept_name_code.CodeMeaning,
                           coding_scheme_designator=concept_name_code.CodingSchemeDesignator)

    @property
    def content(self) -> List['SrElement']:
        '''
            Lists of all entries.
        '''
        return list(self.content_it())

    @property
    def value(self):
        '''
            Extracts the value if a value of supported data types exists. Otherwise, None is returned.
        '''
        return self.get_value()

    # Methods.
    def get_value(self):
        for ve in _VALUE_EXTRACTORS:
            if ve.can_extract(self._dicom_data):
                return ve.extract_value(self._dicom_data)

        return None

    def get(self, *concept_names: str) -> 'SrElement':
        '''
            Returns the first entry with the specified concept name.
            If no entry is found, a ValueError exception is raised.
        '''
        if len(concept_names) > 1:
            return self._get_first(concept_names[0]).get(*concept_names[1:])

        if len(concept_names) == 1:
            return self._get_first(concept_names[0])

        raise ValueError('Invalid argument.')

    def _get_first(self, concept_name: str) -> 'SrElement':
        for concept in self.get_all(concept_name):
            return concept

        message = 'Could not find: "{0}"'.format(concept_name)
        raise SrMissingContentException(message=message)

    def get_all(self, concept_name: str) -> Iterator['SrElement']:
        '''
            Returns an iterator that iterates over entries with the specified concept name.
        '''
        for sr_element in self.content_it():
            cn = sr_element.concept_name
            if concept_name in (cn.code_meaning, cn.code_value_csd):
                yield sr_element

    def content_it(self) -> Iterator['SrElement']:
        '''
            Iterates over all entries.
        '''
        if hasattr(self._dicom_data, 'ContentSequence'):
            return (SrElement(content) for content in self._dicom_data.ContentSequence)

        return iter([])

def assert_concept_name_code_sequence(dicom_data) -> None:
    assert hasattr(dicom_data, 'ConceptNameCodeSequence')
    assert len(dicom_data.ConceptNameCodeSequence) == 1
