import filters as f
from filters.test import BaseFilterTestCase

from test.models import Specie


class ModelTestCase(BaseFilterTestCase):
    """
    Note: most of the animals referenced in this test case are cuddly
    because, let's face it, those are more fun to research (:
    """
    filter_type = f.ext.Model

    def test_pass_none(self):
        """
        ``None`` always passes this filter.

        Chain with ``Required`` to reject null values.
        """
        self.assertFilterPasses(
            self._filter(None, model=Specie),
        )

    def test_pass_pk_match(self):
        """
        The incoming value matches the PK of an existing record.
        """
        # noinspection SpellCheckingInspection
        target_specie = \
            Specie.objects.create(
                binomial_name='Mesocricetus Auratus',
                common_name='Golden Hamster',
                is_cuddly=True,
            )

        self.assertFilterPasses(
            self._filter(target_specie.pk, model=Specie),
            target_specie,
        )

    def test_fail_no_pk_match(self):
        """
        The incoming value does not match the PK of any existing
        records.
        """
        self.assertFilterErrors(
            self._filter(42, model=Specie),
            [f.ext.Model.CODE_NOT_FOUND],
        )

    def test_pass_alternate_field_match(self):
        """
        You can configure the constraint to match a value other than
        PK.
        """
        # noinspection SpellCheckingInspection
        target_specie = Specie.objects.create(
            binomial_name='Setonix Brachyurus',
            common_name='Quokka',
            is_cuddly=False,
        )

        self.assertFilterPasses(
            self._filter(
                target_specie.common_name,
                model=Specie,
                field='common_name',
            ),

            target_specie,
        )

        # Note that we specified ``common_name`` as the match field, so
        # PK no longer works.
        self.assertFilterErrors(
            self._filter(
                target_specie.pk,
                model=Specie,
                field='common_name'
            ),

            [f.ext.Model.CODE_NOT_FOUND],
        )

    def test_fail_too_many_matches(self):
        """
        The incoming value matches more than one record.
        """
        # noinspection SpellCheckingInspection
        Specie.objects.create(
            binomial_name='Enhydra Lutris',
            common_name='Sea Otter',
            is_cuddly=True,
        )

        # noinspection SpellCheckingInspection
        Specie.objects.create(
            binomial_name='Aix Galericulata',
            common_name='Mandarin Duck',
            is_cuddly=True,
        )

        self.assertFilterErrors(
            self._filter(True, model=Specie, field='is_cuddly'),
            [f.ext.Model.CODE_NOT_UNIQUE],
        )

    def test_predicates(self):
        """
        You can use ``predicates`` to specify additional filters to add to
        the query.
        """
        # noinspection SpellCheckingInspection
        target_specie = \
            Specie.objects.create(
                binomial_name='Bradypus Pygmaeus',
                common_name='Dwarf Sloth',
                is_cuddly=True,
            )

        # Note that without any predicates, the filter will find our specie
        # just fine.
        self.assertFilterPasses(
            self._filter(
                target_specie.common_name,
                model=Specie,
                field='common_name',
            ),

            target_specie,
        )

        # However, if we add a predicate that restricts the search to
        # non-cuddlies, the input is no longer valid.
        self.assertFilterErrors(
            self._filter(
                target_specie.common_name,
                model=Specie,
                field='common_name',
                filter={'is_cuddly': False},
            ),

            [f.ext.Model.CODE_NOT_FOUND],
        )

    def test_error_predicate_invalid(self):
        """
        Predicates must return :py:class:`django.db.models.query.QuerySet`
        objects, or else they are invalid.
        """
        # noinspection SpellCheckingInspection
        Specie.objects.create(
            binomial_name='Allactaga Tetradactyla',
            common_name='Jerboa',

            # I honestly can't tell.
            is_cuddly=None,
        )

        filter_ = \
            self.filter_type(
                model=Specie,
                field='common_name',

                # ``QuerySet.count`` returns an integer, not a ``QuerySet``.
                count=(),
            )

        # Note that the exception isn't raised until the filter is applied.
        with self.assertRaises(ValueError):
            filter_.apply('Jerboa')

    def test_pass_predicate_side_effects(self):
        """
        Reckless use of predicates that trigger write queries may result in
        side effects.
        """
        # noinspection SpellCheckingInspection
        target_specie = \
            Specie.objects.create(
                binomial_name='Otolemur Crassicaudatus',
                common_name='Galago',
                is_cuddly=True,
            )

        filter_ = self.filter_type(
            model=Specie,
            field='binomial_name',

            update={'is_cuddly': False},
        )

        with self.assertRaises(ValueError):
            filter_.apply(target_specie.binomial_name)

        # An exception was raised... but not before the DB record was
        # updated!
        self.assertFalse(Specie.objects.get(pk=target_specie.pk).is_cuddly)
