from django import forms
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, NOT_APPLICABLE, OTHER

from ..form_validator import FormValidator
from ..base_form_validator import (
    ModelFormFieldValidatorError,
    InvalidModelFormFieldValidator,
)
from form_validators_app.models import Alphabet
import pdb


class TestApplicableFieldValidator(TestCase):
    """Test applicable_if().
    """

    def setUp(self):
        Alphabet.objects.create(name="A", short_name="A")
        Alphabet.objects.create(name="B", short_name="B")
        Alphabet.objects.create(name="C", short_name="C")
        Alphabet.objects.create(name="D", short_name="D")
        Alphabet.objects.create(name=OTHER, short_name=OTHER)
        Alphabet.objects.create(name=NOT_APPLICABLE, short_name=NOT_APPLICABLE)

    def test_m2m_applicable_if(self):
        """
        """

        cleaned_data = dict(
            f1=YES, alphabet=Alphabet.objects.filter(name__in=[NOT_APPLICABLE])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_applicable_if,
            YES,
            field="f1",
            m2m_field="alphabet",
        )

        try:
            form_validator.m2m_applicable_if(NO, field="f1", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        cleaned_data = dict(f1=NO, alphabet=Alphabet.objects.filter(name__in=["A"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_applicable_if,
            YES,
            field="f1",
            m2m_field="alphabet",
        )

    def test_m2m_applicable_if2(self):

        cleaned_data = dict(
            f1=YES, alphabet=Alphabet.objects.filter(name__in=["A", "B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_applicable_if(YES, field="f1", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_m2m_required(self):

        cleaned_data = dict(f1=YES, alphabet=Alphabet.objects.none())

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError, form_validator.m2m_required, "alphabet"
        )

        cleaned_data = dict(f1=YES, alphabet=Alphabet.objects.filter(name="A"))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_required("alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_m2m_required_if(self):
        """
        """

        cleaned_data = dict(
            f1=YES, alphabet=Alphabet.objects.filter(name__in=[NOT_APPLICABLE])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_required_if(YES, field="f1", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        cleaned_data = dict(f1=YES, alphabet=Alphabet.objects.none())

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_required_if,
            YES,
            field="f1",
            m2m_field="alphabet",
        )

    def test_m2m_single_selection_if(self):
        """
        """

        cleaned_data = dict(f1=YES, alphabet=Alphabet.objects.filter(name__in=["A"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_single_selection_if("A", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

        cleaned_data = dict(
            f1=YES, alphabet=Alphabet.objects.filter(name__in=["A", "B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_single_selection_if,
            "A",
            m2m_field="alphabet",
        )

    def test_m2m_other_specify(self):
        cleaned_data = dict(
            f1=YES, f3=None, alphabet=Alphabet.objects.filter(name__in=["A", "B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

        cleaned_data = dict(
            f1=YES, f3="HELLO", alphabet=Alphabet.objects.filter(name__in=["C", "B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

        cleaned_data = dict(f1=YES, f3="HELLO", alphabet=Alphabet.objects.none())

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

        cleaned_data = dict(
            f1=YES, f3="value", alphabet=Alphabet.objects.filter(name__in=["A", "B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.m2m_other_specify(
                "A", m2m_field="alphabet", field_other="f3"
            )
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_m2m_other_specify_applicable(self):
        cleaned_data = dict(
            f1=YES,
            f3=NOT_APPLICABLE,
            alphabet=Alphabet.objects.filter(name__in=["A", "B"]),
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify_applicable,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

        cleaned_data = dict(
            f1=YES, f3="A", alphabet=Alphabet.objects.filter(name__in=["B"])
        )

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify_applicable,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

        cleaned_data = dict(f1=YES, f3="A", alphabet=Alphabet.objects.none())

        form_validator = FormValidator(cleaned_data=cleaned_data)
        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_other_specify_applicable,
            "A",
            m2m_field="alphabet",
            field_other="f3",
        )

    def test_m2m_selection_expected(self):
        cleaned_data = dict(alphabet=Alphabet.objects.filter(name__in=["B"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_selection_expected,
            "A",
            m2m_field="alphabet",
        )

        cleaned_data = dict(alphabet=Alphabet.objects.filter(name__in=["A"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_selection_expected("A", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_m2m_selections_not_expected(self):
        cleaned_data = dict(alphabet=Alphabet.objects.filter(name__in=["A", "B"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        self.assertRaises(
            forms.ValidationError,
            form_validator.m2m_selections_not_expected,
            "A",
            "B",
            m2m_field="alphabet",
        )

        cleaned_data = dict(alphabet=Alphabet.objects.filter(name__in=["B"]))

        form_validator = FormValidator(cleaned_data=cleaned_data)

        try:
            form_validator.m2m_selections_not_expected("A", m2m_field="alphabet")
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")
