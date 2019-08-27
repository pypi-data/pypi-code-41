import re

import pandas as pd

from seeq.sdk import *

from . import _common
from . import _login
from . import _push


def search(query, all_properties=False, workbook=_common.DEFAULT_WORKBOOK_PATH, recursive=True, quiet=False):
    """
    Issues a query to the Seeq Server to retrieve metadata for signals,
    conditions, scalars and assets. This metadata can be used to retrieve
    samples, capsules for a particular time range.
    :param query: A dictionary of property / match-criteria pairs. Match
    criteria uses the same syntax as the Data tab in Seeq.
    :type query: dict, pd.DataFrame
    :param all_properties: True if all item properties should be retrieved.
    This currently makes the search operation much slower as retrieval of
    properties for an item requires a separate call.
    :type all_properties: bool
    :param workbook: A path string (with >> delimiters) to indicate a workbook
    for which to scope the search to. Note that globally scoped items will
    still be returned.
    :type workbook: str, None
    :param recursive: If True, searches that include a Path entry will include
    items at and below the specified location in an asset tree. If False,
    the query dictionary can only contain a Path entry and only items at the
    specified level will be returned.
    :type recursive: bool
    :param quiet: If True, suppresses progress output.
    :type quiet: bool
    :return: A DataFrame with rows for each item found and columns for each
    property.
    :rtype: pd.DataFrame
    """
    items_api = ItemsApi(_login.client)
    trees_api = TreesApi(_login.client)

    if isinstance(query, pd.DataFrame):
        queries = query.to_dict(orient='records')
        comparison = '=='
    else:
        queries = [query]
        comparison = '~='

    metadata = list()
    columns = list()
    warnings = list()

    _common.display_status('Initializing',
                           _common.STATUS_RUNNING,
                           quiet,
                           {
                               'Results': {
                                   'Time': 0,
                                   'Count': 0
                               }
                           })

    timer = _common.timer_start()

    def _add_to_dict(d, _key, val):
        d[_key] = _common.none_to_nan(val)

        # We want the columns to appear in a certain order (the order we added them in) for readability
        if _key not in columns:
            columns.append(_key)

    def _get_warning_string():
        if len(warnings) == 0:
            return ''

        return '<em><br>Warning:<br>%s</em>' + '<br>'.join(warnings)

    for query in queries:
        if 'ID' in query:
            # If ID is specified, short-circuit everything and just get the item directly
            _item = items_api.get_item_and_all_properties(id=query['ID'])  # type: ItemOutputV1
            _prop_dict = dict()
            for prop in _item.properties:  # type: PropertyOutputV1
                _add_to_dict(_prop_dict, prop.name, prop.value)

            # Name doesn't seem to appear in additional properties
            _add_to_dict(_prop_dict, 'Name', _item.name)

            metadata.append(_prop_dict)
            continue

        if not recursive:
            if len(query) != 1 or 'Path' not in query:
                raise RuntimeError(
                    'When recursive=False, query dictionary must contain only a Path entry. Use Pandas operations to '
                    'on the returned DataFrame to pare down results.')

        allowed_properties = ['Type', 'Name', 'Description', 'Path', 'Asset', 'Datasource Class', 'Datasource ID',
                              'Datasource Name', 'Cache Enabled', 'Archived', 'Scoped To']

        for key, value in query.items():
            if key not in allowed_properties:
                warnings.append('Property "%s" is not an indexed property and will be ignored. Use any of the '
                                'following searchable properties and then filter further using DataFrame '
                                'operations:\n"%s"' % (key, '", "'.join(allowed_properties)))

        item_types = list()
        clauses = list()

        if _common.present(query, 'Type'):
            item_type_specs = list()
            if isinstance(query['Type'], list):
                item_type_specs.extend(query['Type'])
            else:
                item_type_specs.append(query['Type'])

            for item_type_spec in item_type_specs:
                if item_type_spec == 'Signal':
                    item_types.extend(['StoredSignal', 'CalculatedSignal'])
                elif item_type_spec == 'Condition':
                    item_types.extend(['StoredCondition', 'CalculatedCondition'])
                elif item_type_spec == 'Scalar':
                    item_types.extend(['StoredScalar', 'CalculatedScalar'])
                else:
                    item_types.append(item_type_spec)

            del query['Type']

        if _common.present(query, 'Datasource Name'):
            datasource_results = items_api.search_items(filters=['Name == %s' % _common.get(query, 'Datasource Name')],
                                                        types=['Datasource'],
                                                        limit=100000)  # type: ItemSearchPreviewPaginatedListV1

            if len(datasource_results.items) > 1:
                raise RuntimeError('Multiple datasources found that match "%s"' % _common.get(query, 'Datasource Name'))
            elif len(datasource_results.items) == 0:
                raise RuntimeError('No datasource found that matches "%s"' % _common.get(query, 'Datasource Name'))
            else:
                datasource = datasource_results.items[0]  # type: ItemSearchPreviewV1
                query['Datasource ID'] = items_api.get_property(id=datasource.id, property_name='Datasource ID').value
                query['Datasource Class'] = items_api.get_property(id=datasource.id,
                                                                   property_name='Datasource Class').value

            del query['Datasource Name']

        for prop_name in ['Name', 'Description', 'Datasource Class', 'Datasource ID', 'Data ID']:
            if prop_name in query and query[prop_name] is not None:
                clauses.append(prop_name + comparison + query[prop_name])
                del query[prop_name]

        filters = [' && '.join(clauses)] if len(clauses) > 0 else []

        kwargs = {
            'filters': filters,
            'types': item_types,
            'limit': _common.DEFAULT_SEARCH_PAGE_SIZE
        }

        if workbook:
            if _common.is_guid(workbook):
                workbook_id = _common.sanitize_guid(workbook)
            else:
                workbook_id = _push.reify_workbook(workbook, create=False)

            if workbook_id:
                kwargs['scope'] = workbook_id
            elif workbook != _common.DEFAULT_WORKBOOK_PATH:
                raise RuntimeError('Workbook "%s" not found, or is not accessible by you' % workbook)

        if _common.present(query, 'Asset') and not _common.present(query, 'Path'):
            raise RuntimeError('"Path" query parameter must be present when "Asset" parameter present')

        asset_id = None
        path_parts = None
        if _common.present(query, 'Path'):
            path_parts = re.split(r'\s*>>\s*', query['Path'])
            if _common.present(query, 'Asset'):
                path_parts.append(query['Asset'])
                del query['Asset']

            for path_part in path_parts:
                tree_kwargs = dict()
                if 'scope' in kwargs:
                    tree_kwargs['scoped_to'] = kwargs['scope']

                if not asset_id:
                    tree_output = trees_api.get_tree_root_nodes(**tree_kwargs)  # type: AssetTreeOutputV1
                else:
                    tree_kwargs['id'] = asset_id
                    tree_output = trees_api.get_tree(**tree_kwargs)  # type: AssetTreeOutputV1

                found = False
                for child in tree_output.children:  # type: TreeItemOutputV1
                    if child.name == path_part:
                        found = True
                        asset_id = child.id
                        break

                if not found:
                    raise RuntimeError('Could not found asset "%s"' % query['Path'])

            del query['Path']

        if asset_id:
            kwargs['asset'] = asset_id

        if 'Scoped To' in query and query['Scoped To'] is not None:
            kwargs['scope'] = query['Scoped To']
            kwargs['filters'].append('@excludeGloballyScoped')

        def _do_search(offset):
            kwargs['offset'] = offset
            _common.display_status(
                'Querying Seeq Server for items' + _get_warning_string(),
                _common.STATUS_RUNNING,
                quiet,
                {
                    'Results': {
                        'Time': _common.timer_elapsed(timer),
                        'Count': len(metadata)
                    }
                })

            if recursive:
                return items_api.search_items(**kwargs)
            else:
                kwargs2 = {
                    'id': kwargs['asset'],
                    'offset': kwargs['offset'],
                    'limit': kwargs['limit']
                }

                if 'scope' in kwargs:
                    kwargs2['scoped_to'] = kwargs['scope']

                return trees_api.get_tree(**kwargs2)

        def _gather_results_item_search(result):
            item_search_preview = result  # type: ItemSearchPreviewV1
            prop_dict = dict()

            _add_to_dict(prop_dict, 'ID', item_search_preview.id)
            if len(item_search_preview.ancestors) > 1:
                _add_to_dict(prop_dict, 'Path', ' >> '.join([a.name for a in item_search_preview.ancestors[0:-1]]))
                _add_to_dict(prop_dict, 'Asset', item_search_preview.ancestors[-1].name)
            elif len(item_search_preview.ancestors) == 1:
                _add_to_dict(prop_dict, 'Asset', item_search_preview.ancestors[0].name)

            _add_to_dict(prop_dict, 'Name', item_search_preview.name)
            _add_to_dict(prop_dict, 'Description', item_search_preview.description)
            _add_to_dict(prop_dict, 'Type', item_search_preview.type)
            uom = item_search_preview.value_unit_of_measure if item_search_preview.value_unit_of_measure \
                else item_search_preview.source_value_unit_of_measure
            _add_to_dict(prop_dict, 'Value Unit Of Measure', uom)
            datasource_item_preview = item_search_preview.datasource  # type: ItemPreviewV1
            _add_to_dict(prop_dict, 'Datasource Name',
                         datasource_item_preview.name if datasource_item_preview else None)
            if all_properties:
                item = items_api.get_item_and_all_properties(id=item_search_preview.id)  # type: ItemOutputV1
                for prop in item.properties:  # type: PropertyOutputV1
                    _add_to_dict(prop_dict, prop.name, prop.value)

            metadata.append(prop_dict)

        def _gather_results_get_tree(result):
            tree_item_output = result  # type: TreeItemOutputV1
            prop_dict = dict()

            _add_to_dict(prop_dict, 'ID', tree_item_output.id)
            if len(path_parts) > 1:
                _add_to_dict(prop_dict, 'Path', ' >> '.join(path_parts[0:-1]))
                _add_to_dict(prop_dict, 'Asset', path_parts[-1])
            elif len(path_parts) == 1:
                _add_to_dict(prop_dict, 'Asset', path_parts[0])

            _add_to_dict(prop_dict, 'Name', tree_item_output.name)
            _add_to_dict(prop_dict, 'Description', tree_item_output.description)
            _add_to_dict(prop_dict, 'Type', tree_item_output.type)
            _add_to_dict(prop_dict, 'Value Unit Of Measure', tree_item_output.value_unit_of_measure)
            if all_properties:
                item = items_api.get_item_and_all_properties(id=tree_item_output.id)  # type: ItemOutputV1
                for prop in item.properties:  # type: PropertyOutputV1
                    _add_to_dict(prop_dict, prop.name, prop.value)

            metadata.append(prop_dict)

        if recursive:
            _iterate_over_output(_do_search, 'items', _gather_results_item_search)
        else:
            _iterate_over_output(_do_search, 'children', _gather_results_get_tree)

    _common.display_status(
        'Query successful' + _get_warning_string(),
        _common.STATUS_SUCCESS,
        quiet,
        {
            'Results': {
                'Time': _common.timer_elapsed(timer),
                'Count': len(metadata)
            }
        })

    return pd.DataFrame(data=metadata, columns=columns)


def _iterate_over_output(output_func, collection_name, action_func):
    offset = 0
    while True:
        output = output_func(offset)

        collection = getattr(output, collection_name)

        for item in collection:
            action_func(item)

        if len(collection) != output.limit:
            break

        offset += output.limit
