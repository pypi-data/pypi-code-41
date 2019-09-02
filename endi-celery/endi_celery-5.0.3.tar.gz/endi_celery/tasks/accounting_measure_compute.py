# -*- coding: utf-8 -*-
"""
Tasks used to compile treasury measures
"""
import transaction

from pyramid_celery import celery_app
from sqlalchemy import or_, desc
from collections import OrderedDict

from endi_base.models.base import DBSESSION
from endi_base.mail import send_mail
from endi.models.accounting.operations import (
    AccountingOperationUpload,
    AccountingOperation,
)
from endi.models.accounting.treasury_measures import (
    TreasuryMeasure,
    TreasuryMeasureGrid,
    TreasuryMeasureType,
    TreasuryMeasureTypeCategory,
)
from endi_celery.conf import (
    get_recipients_addresses,
)
from endi.models.accounting.income_statement_measures import (
    IncomeStatementMeasure,
    IncomeStatementMeasureGrid,
    IncomeStatementMeasureType,
    IncomeStatementMeasureTypeCategory,
)

from endi_celery.tasks import utils


logger = utils.get_logger(__name__)


class GridCacheItem:
    """
    Wraps a grid in cache and provide storages for

    measures
    total value by measure_type
    total value by measure type category
    """
    def __init__(self, grid):
        self.grid = grid
        self._category_totals = {}
        self._type_totals = {}
        self._measures = {}

    def clean_old_measures(self, type_ids):
        """
        Clean old measures

        Set them to  or remove them if theire type is not in the type list

        :param list type_ids: List of ids (int)
        :returns: The list of measures to remove
        """
        old_measures = [
            measure for measure in self.grid.measures
            if measure.measure_type_id not in type_ids
        ]
        self.grid.measures = [
            measure for measure in self.grid.measures
            if measure.measure_type_id in type_ids
        ]

        for measure in self.grid.measures:
            measure.value = 0
            self._measures[measure.measure_type_id] = measure
        return old_measures

    def get_measures(self):
        """
        Collect all existing measures (newly created or already existing)
        """
        return self._measures

    def store_measure(self, measure):
        """
        Store a measure in the measure cache

        :param obj measure: A child of BaseTreasuryMeasure
        """
        self._measures[measure.measure_type_id] = measure
        if measure not in self.grid.measures:
            self.grid.measures.append(measure)

    def set_total_type(self, measure):
        """
        Store the total value for a given measure type in the grid's cache

        :param obj measure: A child of BaseTreasuryMeasure
        """
        self._type_totals[measure.measure_type_id] = measure.value

    def update_category_total(self, measure):
        """
        Update the category total value for a given measure type in the grid's
        cache

        :param obj measure: A child of BaseTreasuryMeasure
        """
        measure_type = measure.measure_type
        if not measure_type.computed_total:
            if measure_type.category_id not in self._category_totals:
                self._category_totals[measure_type.category_id] = 0
            self._category_totals[measure_type.category_id] += measure.value

    def get_type_total(self, typ_id):
        """
        Get the total type for a given measure type

        :param int typ_id: The id of the measure type
        """
        return self._type_totals.get(typ_id, 0)

    def get_category_total(self, category_id):
        """
        Get the category total for a given measure type category

        :param int category_id: The id of the category
        """
        return self._category_totals.get(category_id, 0)


class GridCache:
    """
    A grid cache used to temporarly store all datas related to the current
    computation

    Eache item is an Accounting Measure Grid wraped with the GridCacheItem
    object
    """
    def __init__(self):
        self._datas = {}

    def store_grid(self, key, grid):
        self._datas[key] = GridCacheItem(grid)
        return self._datas[key]

    def get(self, key):
        return self._datas.get(key)


class BaseMeasureCompiler(object):
    """
    Base measure compiler

    Uses a cache to store grids currently edited

    For each grid, the cache contains :

        - Measures already created
        - totals by category
        - totals by type

    Totals are used in a second time to compute "total" measures (not related to
    account numbers)
    """
    measure_type_class = None
    measure_type_category_class = None
    measure_grid_class = None
    measure_class = None

    def __init__(self, upload, operations):
        self.upload = upload
        self.filetype = upload.filetype
        self.operations = operations
        self.session = DBSESSION()
        self.cache = GridCache()

        # Collect all types
        self.common_measure_types = self._collect_common_measure_types()
        self.categories = self._collect_categories()
        self.computed_measure_types = self._collect_computed_measure_types()

        self.all_type_ids = [t.id for t in self.common_measure_types]
        for cat_id, types in self.computed_measure_types.items():
            self.all_type_ids.extend([t.id for t in types])

        self.processed_grids = []

    def _get_active_type_query(self):
        """
        Build a query to list active measure types
        :returns: An sqlalchemy query object
        """
        return self.measure_type_class.query(
        ).join(
            self.measure_type_category_class
        ).filter(
            self.measure_type_class.active == True  # noqa: E712
        ).filter(
            self.measure_type_category_class.active == True  # noqa: E712
        )

    def _collect_common_measure_types(self):
        """
        Retrieve measure types that are not computed from other measures
        :returns: The list of measure types
        """
        return self._get_active_type_query().filter(
            or_(
                self.measure_type_class.is_total == False,  # noqa: E712
                self.measure_type_class.total_type == 'account_prefix',
            )
        ).all()

    def _collect_categories(self):
        """
        Retrieve all measure type categories
        """
        return self.measure_type_category_class.get_categories()

    def _collect_computed_measure_types(self):
        """
        Collect computed measure types and store them by category id

        :returns: a dict {category_id: [list of MeasureType]}
        """
        result = OrderedDict()
        query = self._get_active_type_query()
        query = query.filter(
            self.measure_type_class.is_total == True,  # noqa: E712
        ).filter(
            self.measure_type_class.total_type != 'account_prefix',
        ).order_by(
            self.measure_type_category_class.order
        ).order_by(self.measure_type_class.order)
        for typ in query:
            result.setdefault(typ.category_id, []).append(typ)
        return result

    def get_cache_key_from_grid(self, grid):
        """
        Build a cache key based on the given grid object

        :param obj grid: The grid instance
        :returns: A valid dict key
        """
        pass

    def get_cache_key_from_operation(self, operation):
        """
        Build a cache key based on the given operation object

        :param obj operation: The AccountingOperation instance
        :returns: A valid dict key
        """
        pass

    def _get_new_measure(self, measure_type, grid_id):
        """
        Build a new measure
        """
        measure = self.measure_class(
            label=measure_type.label,
            grid_id=grid_id,
            measure_type_id=measure_type.id,
            order=measure_type.order,
        )
        self.session.add(measure)
        self.session.flush()
        return measure

    def _clean_existing_grid(self, grid_item):
        """
        Clean an existing grid on first load
        specific to the Measure Types

        :param obj grid_item: A GridCacheItem instance
        """
        pass

    def get_grid_item(self, operation):
        """
        Retrieve the grid related to the given operation datas

        :param obj operation: an AccountingOperation instance
        :returns: A Grid instance
        """
        key = self.get_cache_key_from_operation(operation)
        grid_item = self.cache.get(key)
        if grid_item is None:
            grid = self._query_grid(operation)
            if grid is None:
                grid = self._get_new_grid(operation)
                self.session.add(grid)
                self.session.flush()
                grid_item = self.cache.store_grid(key, grid)
            else:
                grid_item = self.cache.store_grid(key, grid)
                self._clean_existing_grid(grid_item)
        return grid_item

    def get_values_for_computation(self, grid_item):
        """
        Collect total values in a dict for complex datas computation

        :param obj grid_item: An instance of GridCacheItem
        """
        result = {}
        for category in self.categories:
            result[category.label] = grid_item.get_category_total(category.id)

        for typ_ in self.common_measure_types:
            result[typ_.label] = grid_item.get_type_total(typ_.id)

        for typlist_ in self.computed_measure_types.values():
            for typ_ in typlist_:
                value = grid_item.get_type_total(typ_.id)
                result[typ_.label] = value

        return result

    def _cache_grid_totals(self):
        """
        Cache all grid totals in order to use them in computation
        """
        for grid_item in self.processed_grids:
            for measure in grid_item.get_measures().values():
                grid_item.set_total_type(measure)
                grid_item.update_category_total(measure)

    def _process_common_measures(self):
        """
        Compile common measures (related to an account prefix) with the given
        operations

        :returns: A list of GridCacheItem
        """
        logger.debug(
            u"    + Processing datas with {}".format(self.__class__.__name__)
        )
        for operation in self.operations:
            if operation.company_id is None:
                continue

            current_grid_item = self.get_grid_item(operation)
            grid = current_grid_item.grid
            if current_grid_item not in self.processed_grids:
                self.processed_grids.append(current_grid_item)

            measures = current_grid_item.get_measures()

            for measure_type in self.common_measure_types:
                matched = False
                if measure_type.match(operation.general_account):
                    measure = measures.get(measure_type.id)
                    if measure is None:
                        measure = self._get_new_measure(
                            measure_type,
                            grid.id,
                        )
                        current_grid_item.store_measure(measure)

                    measure.value += operation.total()
                    matched = True

                if matched:
                    self.session.merge(measure)
                    self.session.flush()

        return self.processed_grids

    def _complete_grids_with_common_measures(self):
        """
        Insert common measures in the grids if not set yet
        """
        for grid_item in self.processed_grids:
            logger.debug("Completing grid %s" % grid_item.grid.id)
            measures = grid_item.get_measures()
            for measure_type in self.common_measure_types:
                measure = measures.get(measure_type.id)
                if measure is None:
                    measure = self._get_new_measure(
                        measure_type,
                        grid_item.grid.id,
                    )
                    grid_item.store_measure(measure)
                else:
                    logger.debug("Updating the order of the given measure %s : was %s becomes %s" % (measure.label, measure.order, measure_type.order))
                    measure.order = measure_type.order
                    self.session.merge(measure)

    def _process_computed_measures(self):
        """
        Process dynamically computed measures (based on the other ones)

        :returns: A list of GridCacheItem
        """
        for grid_item in self.processed_grids:
            measures = grid_item.get_measures()
            for category_id, measure_types in \
                    self.computed_measure_types.items():
                for measure_type in measure_types:
                    values = self.get_values_for_computation(grid_item)
                    value = measure_type.compute_total(values)
                    measure = measures.get(measure_type.id)
                    if measure is None:
                        measure = self._get_new_measure(
                            measure_type,
                            grid_item.grid.id,
                        )
                        grid_item.store_measure(measure)
                    else:
                        measure.order = measure_type.order

                    measure.value = value
                    self.session.merge(measure)
                    grid_item.set_total_type(measure)

        return self.processed_grids

    def process_datas(self):
        """
        Main entry point to process measure computation
        """
        self._process_common_measures()
        self._complete_grids_with_common_measures()
        self.session.flush()
        self._cache_grid_totals()
        self._process_computed_measures()
        self.session.flush()
        return [griditem.grid for griditem in self.processed_grids]


class TreasuryMeasureCompiler(BaseMeasureCompiler):
    measure_type_class = TreasuryMeasureType
    measure_type_category_class = TreasuryMeasureTypeCategory
    measure_grid_class = TreasuryMeasureGrid
    measure_class = TreasuryMeasure
    label = u"Génération des états de trésorerie"

    def get_message(self, grids):
        return u"""Génération des états de trésorerie

États de trésorerie générés : {}

----
enDI
""".format(len(grids))

    def get_cache_key_from_operation(self, operation):
        """
        Build a cache key based on the given operation object
        """
        key = (operation.company_id, self.upload.updated_at.date())
        return key

    def get_cache_key_from_grid(self, grid):
        """
        Build a cache key based on the given grid object
        """
        key = (grid.company_id, grid.date)
        return key

    def _query_grid(self, operation):
        """
        Query a grid associated to the given operation

        Query filters should match the get_cache_key_from_operation options
        """
        query = TreasuryMeasureGrid.query().filter_by(
            date=self.upload.updated_at.date()
        ).filter_by(company_id=operation.company_id)

        query = query.order_by(
            desc(TreasuryMeasureGrid.datetime)
        )
        return query.first()

    def _get_new_grid(self, operation):
        """
        Build a new grid based on the given operation

        :param obj operation: The AccountingOperation from which we build
        measure
        """
        return TreasuryMeasureGrid(
            date=self.upload.updated_at.date(),
            company_id=operation.company_id,
            upload=self.upload,
        )

    def _clean_existing_grid(self, grid_item):
        """
        Clean an existing grid on first load

        :param obj grid_item: A GridCacheItem instance
        """
        for measure in grid_item.grid.measures:
            self.session.delete(measure)


class IncomeStatementMeasureCompiler(BaseMeasureCompiler):
    measure_type_class = IncomeStatementMeasureType
    measure_type_category_class = IncomeStatementMeasureTypeCategory
    measure_grid_class = IncomeStatementMeasureGrid
    measure_class = IncomeStatementMeasure
    label = u"Génération des comptes de résultat"

    def get_message(self, grids):
        return u"""Génération des comptes de résultat :

Comptes de résultat traités : {}

----
enDI
""".format(len(grids)/12)

    def get_cache_key_from_operation(self, operation):
        """
        Build a cache key based on the given operation object
        """
        return (operation.company_id, operation.date.year, operation.date.month)

    def get_cache_key_from_grid(self, grid):
        """
        Build a cache key based on the given grid object
        """
        return (grid.company_id, grid.year, grid.month)

    def _query_grid(self, operation):
        """
        Query a grid associated to the given operation

        Query filters should match the get_cache_key_from_operation options
        """
        return IncomeStatementMeasureGrid.query().filter_by(
            year=operation.date.year
        ).filter_by(
            month=operation.date.month
        ).filter_by(company_id=operation.company_id).first()

    def _get_new_grid(self, operation):
        """
        Build a new grid based on the given operation

        :param obj operation: The AccountingOperation from which we build
        measure
        """
        return IncomeStatementMeasureGrid(
            year=operation.date.year,
            month=operation.date.month,
            company_id=operation.company_id,
            upload=self.upload,
        )

    def _clean_existing_grid(self, grid_item):
        """
        Clean an existing grid on first load

        :param obj grid_item: A GridCacheItem instance
        """
        # Only clean the old grid item measures (keep existing)
        old_measures = grid_item.clean_old_measures(self.all_type_ids)
        for measure in old_measures:
            self.session.delete(measure)


def get_measure_compilers(data_type, grid_type=None):
    """
    Retrieve the measure compilers to be used with this given type of datas

    :param str data_type: The type of data we build our measures from
    :returns: The measure compiler
    """
    if data_type == AccountingOperationUpload.ANALYTICAL_BALANCE:
        logger.info("  + Handling analytical_balance file")
        return [TreasuryMeasureCompiler]
    elif data_type == AccountingOperationUpload.GENERAL_LEDGER:
        logger.info("  + Handling General Ledger file")
        return [IncomeStatementMeasureCompiler]
    elif data_type == AccountingOperationUpload.SYNCHRONIZED_ACCOUNTING:
        logger.info("  + Handling Synchronized Datas")
        if grid_type == 'treasury':
            return [TreasuryMeasureCompiler]
        elif grid_type == 'income_statement':
            return [IncomeStatementMeasureCompiler]
        else:
            return [TreasuryMeasureCompiler, IncomeStatementMeasureCompiler]

MAIL_ERROR_SUBJECT = u"[Erreur] {}"
MAIL_SUCCESS_SUBJECT = u"[Succès] {}"


def send_success(request, mail_addresses, type_label, message):
    """
    Send a success email

    :param obj request: The current request object
    :param list mail_addresses: List of recipients e-mails
    :param str message: message to send
    """
    if mail_addresses:
        try:
            subject = MAIL_SUCCESS_SUBJECT.format(type_label)
            send_mail(request, mail_addresses, message, subject)
        except:
            logger.exception(u"Error sending email")


def send_error(request, mail_addresses, type_label, message):
    """
    Send an error email

    :param obj request: The current request object
    :param list mail_addresses: List of recipients e-mails
    :param str message: message to send
    """
    if mail_addresses:
        try:
            subject = MAIL_ERROR_SUBJECT.format(type_label)
            send_mail(request, mail_addresses, message, subject)
        except:
            logger.exception(u"Error sending email")


@celery_app.task(bind=True)
def compile_measures_task(self, upload_id, grid_type=None):
    """
    Celery task handling measures compilation
    """
    logger.info(
        u"Launching the compile measure task for upload {0}".format(upload_id)
    )

    if grid_type is not None:
        logger.info(u"Only compiling {} grids".format(grid_type))

    transaction.begin()
    upload = AccountingOperationUpload.get(upload_id)
    if upload is None:
        raise Exception(
            u"No AccountingOperationUpload instance with id {}".format(
                upload_id
            )
        )
    operations = AccountingOperation.query().filter_by(
        upload_id=upload_id
    ).all()

    mail_addresses = get_recipients_addresses(self.request)
    compiler_factories = get_measure_compilers(upload.filetype, grid_type)
    messages = []
    for compiler_factory in compiler_factories:
        try:
            compiler = compiler_factory(upload, operations)
            grids = compiler.process_datas()
            messages.append(compiler.get_message(grids))
        except Exception as err:
            logger.exception(u"Error while generating measures")
            transaction.abort()
            send_error(
                self.request,
                mail_addresses,
                compiler.label,
                err.message,
            )
            return False
        else:
            logger.info(u"{0} measure grids were handled".format(len(grids)))
            send_success(
                self.request,
                mail_addresses,
                compiler.label,
                compiler.get_message(grids),
            )
            logger.info(
                u"A success email has been sent to {0}".format(
                    mail_addresses
                )
            )

    transaction.commit()
    logger.info(u"The transaction has been commited")
    logger.info(u"* Task SUCCEEDED !!!")
