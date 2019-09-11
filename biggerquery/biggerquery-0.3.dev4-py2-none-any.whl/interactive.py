from __future__ import absolute_import

from inspect import getargspec

import pandas as pd

from .configuration import DatasetConfig
from .job import Job


def interactive_component(**dependencies):
    def decorator(standard_component):
        return InteractiveComponent(standard_component,
                                    {dep_name: dep.config for dep_name, dep in dependencies.items()})

    return decorator


class InteractiveDatasetManager(object):
    """Let's you run operations on a dataset, without the need of creating a component."""

    def __init__(self,
                 project_id,
                 dataset_name,
                 internal_tables=None,
                 external_tables=None,
                 extras=None):
        self.config = DatasetConfig(
            project_id=project_id,
            dataset_name=dataset_name,
            internal_tables=internal_tables,
            external_tables=external_tables,
            extras=extras)

    def write_truncate(self, table_name, sql, partitioned=True):
        return self._tmp_interactive_component_factory(
            'write_truncate_to_{}'.format(table_name),
            'write_truncate',
            table_name,
            sql,
            partitioned=partitioned,
            operation_name='auto')

    def write_append(self, table_name, sql, partitioned=True):
        return self._tmp_interactive_component_factory(
            'write_append_to_{}'.format(table_name),
            'write_append',
            table_name,
            sql,
            partitioned=partitioned,
            operation_name='auto')

    def write_tmp(self, table_name, sql):
        return self._tmp_interactive_component_factory(
            'write_tmp_to_{}'.format(table_name),
            'write_tmp',
            table_name,
            sql,
            operation_name='auto')

    def collect(self, sql):
        return self._tmp_interactive_component_factory(
            'collect',
            'collect',
            sql,
            operation_name='auto')

    def create_table(self, create_query):
        return self._tmp_interactive_component_factory(
            'create_table',
            'create_table',
            create_query,
            operation_name='auto')

    def _tmp_interactive_component_factory(self, component_name, method, *args, **kwargs):
        @interactive_component(dataset_manager=self)
        def tmp_component(dataset_manager):
            return getattr(dataset_manager, method)(*args, **kwargs)

        tmp_component.__name__ = component_name
        return tmp_component


class InteractiveComponent(object):
    """Let's you run the component for specific runtime
     and peek a operation results as the pandas.DataFrame."""

    def __init__(self, standard_component, dependency_config):
        self._standard_component = standard_component
        self._dependency_config = dependency_config

    def run(self, runtime):
        _, component_callable = self._component_callable_factory()
        return Job(component_callable, **self._dependency_config).run(runtime)

    def run_operation(self, runtime, operation_name):
        """Runs specified operation in component."""
        _, component_callable = self._component_callable_factory(operation_name=operation_name)
        return Job(component_callable, **self._dependency_config).run(runtime)

    def peek(self, runtime, operation_name='auto', limit=1000):
        """Returns a result of the specified operation in the form of pandas.DataFrame, without really running the
        operation and affecting a table."""
        results_container, component_callable = self._component_callable_factory(operation_name=operation_name,
                                                                                 peek=True, peek_limit=limit)
        Job(component_callable, **self._dependency_config).run(runtime)
        try:
            return results_container[0]
        except IndexError:
            raise ValueError("Operation '{}' not found".format(operation_name))

    def peek_cost(self, runtime, operation_name='auto'):
        return '1 $'

    def __call__(self, **kwargs):
        _, component_callable = self._component_callable_factory()
        return component_callable(**kwargs)

    def _component_callable_factory(self, operation_name=None, peek=None, peek_limit=None):
        operation_settings = {'operation_name': operation_name, 'peek': peek, 'peek_limit': peek_limit}
        results_container = []

        def component_callable(**kwargs):
            operation_level_dataset_managers = {k: OperationLevelDatasetManager(v, **operation_settings)
                                                for k, v in kwargs.items()}

            component_return_value = self._standard_component(**operation_level_dataset_managers)

            for operation_level_dataset_manager in operation_level_dataset_managers.values():
                if operation_level_dataset_manager.result:
                    results_container.extend(operation_level_dataset_manager.result)

            return component_return_value

        component_callable_with_proper_signature = "def reworked_function({signature}):\n    return original_func({kwargs})\n".format(
            signature=','.join([arg for arg in getargspec(self._standard_component).args]),
            kwargs=','.join(['{arg}={arg}'.format(arg=arg) for arg in getargspec(self._standard_component).args]))
        component_callable_with_proper_signature_code = compile(component_callable_with_proper_signature, "fakesource",
                                                                "exec")
        fake_globals = {}
        eval(component_callable_with_proper_signature_code, {'original_func': component_callable}, fake_globals)

        component_callable = fake_globals['reworked_function']
        component_callable.__name__ = operation_name or self._standard_component.__name__

        return results_container, component_callable


class OperationLevelDatasetManager(object):
    """
    Let's you run specified operation or peek a result of a specified operation.
    """

    def __init__(self, dataset_manager, peek=False, operation_name=None, peek_limit=1000):
        self._dataset_manager = dataset_manager
        self._peek = peek
        self._operation_name = operation_name
        self._peek_limit = peek_limit
        self._results_container = []

    def write_truncate(self, table_name, sql, partitioned=True, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_truncate,
            sql=sql,
            table_name=table_name,
            partitioned=partitioned,
            custom_run_datetime=custom_run_datetime)

    def write_append(self, table_name, sql, partitioned=True, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_append,
            sql=sql,
            table_name=table_name,
            partitioned=partitioned,
            custom_run_datetime=custom_run_datetime)

    def write_tmp(self, table_name, sql, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.write_tmp,
            sql=sql,
            table_name=table_name,
            custom_run_datetime=custom_run_datetime)

    def collect(self, sql, custom_run_datetime=None, operation_name=None):
        return self._run_write_operation(
            operation_name=operation_name,
            method=self._dataset_manager.collect,
            sql=sql,
            custom_run_datetime=custom_run_datetime)

    def create_table(self, create_query, operation_name=None):
        if self._operation_name == operation_name or self._operation_name is None:
            return self._results_container, self._dataset_manager.create_table(create_query)

    @property
    def runtime_str(self):
        return self._dataset_manager.runtime_str

    @property
    def result(self):
        return self._results_container

    def _collect_select_result_to_pandas(self, sql):
        sql = sql if 'limit' in sql.lower() else sql + '\nLIMIT {}'.format(str(self._peek_limit))
        return self._as_pandas(self._dataset_manager.collect(sql))

    def _run_write_operation(self, operation_name, method, sql, *args, **kwargs):
        if self._should_peek_operation_results(operation_name):
            result = self._collect_select_result_to_pandas(sql)
            self._results_container.append(result)
            return result
        elif self._should_run_operation(operation_name):
            return self._as_pandas(method(*args, sql=sql, **kwargs) or [])

    def _as_pandas(self, rows):
        return pd.DataFrame([dict(r.items()) for r in rows])

    def _should_peek_operation_results(self, operation_name):
        return self._operation_name == operation_name and self._peek is not None

    def _should_run_operation(self, operation_name):
        return self._operation_name == operation_name or self._operation_name is None