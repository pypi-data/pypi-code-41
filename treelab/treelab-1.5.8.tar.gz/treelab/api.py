import json
import threading
from contextlib import contextmanager
from typing import Iterator, Tuple

import numpy as np
import pandas as pd
from treelab.event_handling.event_handler import *
from treelab.event_handling.listenable import *
import time
from treelab.consts import UpdateAction, DatePattern, DateFormatter, FieldTypeMap
from functools import wraps
from datetime import datetime, timedelta
import re
import copy


class Treelab:
    def __init__(self, token):
        self.token = token

    def add_workspace(self, workspace_name: str):
        return Workspace(name=workspace_name, token=self.token)

    def workspace(self, workspace_id: str):
        return Workspace(workspace_id=workspace_id, token=self.token)

    def get_workspace(self, workspace_id: str):
        return Workspace(workspace_id=workspace_id, token=self.token)

    def _get_workspace(self, workspace_id: str, workspace_name: str = ''):
        return Workspace(workspace_id=workspace_id, name=workspace_name, token=self.token)

    def get_all_workspaces(self):
        client = TreeLabClient(token=self.token)
        workspaces = [self._get_workspace(workspace_id=res.id, workspace_name=res.name) for res in client.get_all_workspaces().result]
        client.close()
        return workspaces

    def update_workspace(self, workspace_id: str, name: str):
        workspace_id = TreeLabClient(token=self.token).update_workspace(UpdateWorkspaceInput(id=workspace_id, name=name)).id
        return Workspace(workspace_id=workspace_id, name=name, token=self.token)

    def get_workspace_by_name(self, name: str):
        workspaces = self.get_all_workspaces()
        return [workspace for workspace in workspaces if workspace.name == name]


class _TreelabObject(BasicListenable):
    def __init__(self):
        super().__init__(None)
        self._id = ""
        self._name = ""

    @property
    def id(self):
        return self._id

    @property
    def workspace(self):
        return self._workspace

    @property
    def name(self):
        return self._name

    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError('Data not implemented in '.format(self.__class__))

    @property
    def __repr_fields__(self):
        raise NotImplementedError

    @abstractmethod
    def _get_event_id(self, event: EventPayload):
        return event["workspaceId"]

    def should_be_listened(self, event: EventPayload, listener: Listener):
        return self.id in self._get_event_id(event) if isinstance(self, View) else self.id == self._get_event_id(event)

    def __repr__(self):
        items = {k: self.__dict__[k] for k in self.__repr_fields__}
        items = dict([('object_type', self.__class__.__name__)] + list(items.items()))
        return str(items)


class Workspace(_TreelabObject):
    __repr_fields__ = {'_id', '_name'}

    def __init__(self, token: str, workspace_id=None, name=""):
        super().__init__()
        self._name = name
        self.token = token
        self._id = self._create_workspace(workspace_id=workspace_id)
        # self._setup_init_subscription()
        self._workspace = self

    def get_name(self):
        if self.name == '' and self.id != '':
            workspace_projection = self.client.get_workspace(GetWorkspaceInput(id=self.id))
            self._name = workspace_projection.name
        return self.name

    @staticmethod
    def _create_client(workspace):
        workspace._client = TreeLabClient(token=workspace.token)

    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._create_client(self)
        return self._client

    def close(self):
        """
        If the workspace and child objects no longer have a GRPC connection, call close to close the connection
        :return:
        """
        if hasattr(self, '_client'):
            self.client.close()
            delattr(self, '_client')

    def _create_workspace(self, workspace_id: str) -> str:
        if not workspace_id:
            workspace_id = self.client.create_workspace(CreateWorkspaceInput(name=self.name)).id
        return workspace_id

    def setup_init_subscription(self):
        self._event_handler = EventHandler(self.id, self.token)

    @property
    def event_handler(self) -> EventHandler:
        return self._event_handler

    def register(self, listener: Union[Listener, Callable[[EventPayload], Any]], thread_num: int = 0):
        """
        Register a listener to event handler, the listener are in type of either function that takes an EventPayload
        as parameter, or a Listener, you can specify whether to run this task on a new thread by the parameter
        on_new_thread
        :param listener:
        :param thread_num:
        :return:
        """
        listener = self._get_real_listener(listener)
        listener._thread_num = thread_num
        self.event_handler.register(listener=listener)

    def register_list(self, listeners: List[Union[Listener, Callable[[EventPayload], Any]]]):
        """
        Register a list of listeners to event handler
        :param listeners:
        :return:
        """
        [self.register(listener) for listener in listeners]

    def _get_real_listener(self, listener: Union[Listener, Callable[[EventPayload], Any]]) -> Listener:
        return FunctionListener(listener, self.event_handler.get_new_listener_name()) if isinstance(listener, Callable) else listener

    def get_core(self, core_id: str):
        """
        Get a core based on core_id
        :param core_id:
        :return:
        """
        return Core(workspace=self, core_id=core_id, name='')

    def remove_core(self, core_id: str):
        return self.client.remove_core(RemoveCoreInput(workspaceId=self.id, coreId=core_id)).id

    def remove_cores(self, core_ids: List[str] = None, mode='ids'):
        """
        You can delete the specified core or all of the core
        :param core_ids:
        :param mode:
            if mode == ids:
                Deletes the specified core id and returns the core id that can be deleted
            if mode == all:
                Delete all core ids and return the deleted core id
        :return:
        """
        ids = [core.id for core in self.client.get_all_cores(GetCoresInput(workspaceId=self.id)).result]
        if mode == 'ids':
            core_ids = [core_id for core_id in core_ids if core_id in ids]
        elif mode == 'all':
            core_ids = ids
        else:
            raise ValueError(
                '{} remove_cores mode is not supported, please select mode between ids and all'.format(mode))
        return list(map(lambda core_id: self.client.remove_core(RemoveCoreInput(workspaceId=self.id, coreId=core_id)).id, core_ids))

    def get_cores_by_name(self, core_name: str) -> list:
        """
        get cores by core_name
        :param core_name:
        :return:
        """
        return [core for core in self.get_all_cores() if core.name == core_name]

    def get_all_cores(self):
        return [Core(workspace=self, core_id=core.id, name=core.name, color=CoreColor(core.color), icon=Icon(core.icon)) for core in self.client.get_all_cores(GetCoresInput(workspaceId=self.id)).result]

    def core(self, core_id: str):
        """
        Get a core based on core_id, equivalent to get_core
        :param core_id:
        :return:
        """
        return self.get_core(core_id)

    def add_core(self, core_name: str, color: CoreColor = CoreColor.blue, icon: Icon = Icon.briefcase):
        """
        Add a core with core_name, and color and icon as option
        :param core_name:
        :param color:
        :param icon:
        :return:
        """
        if '"' in core_name:
            raise ValueError('Double quotes cannot exist in core name')
        return Core(workspace=self, name=core_name, color=color, icon=icon)

    def update_core(self, core_id: str, core_name: str, color: CoreColor = CoreColor.blue, icon: Icon = Icon.book):
        if '"' in core_name:
            raise ValueError('Double quotes cannot exist in core name ', core_name)
        return Core(core_id=core_id, workspace=self, name=core_name, color=color, icon=icon, operation='update')

    # def dispose(self):
    #     """
    #     Closing the subscription streams created by grpc
    #     :return:
    #     """
    #     self.event_handler.dispose()

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        if event["eventName"].split('.')[-1] == 'CoreCreated':
            return event["coreCreatedDto"]["workspaceId"]
        elif event["eventName"].split('.')[-1] == 'CoreUpdated':
            return event["coreUpdatedDto"]["workspaceId"]
        else:
            return event["workspaceId"]

    def update_core_order(self, core_id: str, after_core_id: str):
        self.client.update_core_order(ReorderCoreInput(workspaceId=self.id, coreId=core_id, afterCoreId=after_core_id))


class Core(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'icon', 'color', '_workspace'}

    def __init__(self, name: str, core_id: str = None, workspace: Workspace = None, color: CoreColor = CoreColor.blue, icon: Icon = Icon.book, operation='add'):
        """

        :param name:
        :param core_id:
        :param workspace:
        :param color:
        :param icon:
        :param operation: this contains add update
        """
        super().__init__()
        self._name = name
        self.color = color
        self.icon = icon
        self.tables = {}
        self._workspace = workspace
        if operation == 'add':
            self._id = self._add_core(core_id, workspace)
        elif operation == 'update':
            self._id = self._update_core(core_id, workspace)
        else:
            raise ValueError(f"Unsupported operations {operation}")

    def get_name(self):
        if not self.color or not self.icon or not self.name or not self.id:
            core_projection = self.workspace.client.get_core(GetCoreInput(workspaceId=self.workspace.id, coreId=self.id))
            self._name = core_projection.name
            self.color = CoreColor(core_projection.color)
            self.icon = Icon(core_projection.icon)
        return self.name

    def get_color(self):
        self.get_name()
        return self.color

    def get_icon(self):
        self.get_name()
        return self.icon

    def close(self):
        """
        If the core no longer have a GRPC connection, call close to close the connection
        :return:
        """
        self.workspace.close()

    def _add_core(self, core_id: str, workspace: Workspace):
        if workspace:
            self._workspace = workspace
            if core_id:
                return core_id
            else:
                add_core_input = AddCoreInput(workspaceId=self.workspace.id, coreName=self.name, color=self.color.value, icon=self.icon.value)
                core_id = self.workspace.client.add_core(add_core_input).id
                self._id = core_id
            return core_id
        else:
            raise ValueError("You need to get/create the core from the workspace!")

    def _update_core(self, core_id: str, workspace: Workspace):
        self._workspace = workspace
        update_core_input = UpdateCoreInput(coreId=core_id, workspaceId=self.workspace.id, coreName=self.name,
                                            color=self.color.value,
                                            icon=self.icon.value)
        core_id = self.workspace.client.update_core(update_core_input).id
        self._id = core_id
        return core_id

    def get_table(self, table_id: str, online_update: bool = False):
        """
        Get table from table_id
        :param table_id:
        :param online_update:True is use local backup data,False is use online data
        :return:
        """
        return Table(table_id=table_id, core=self, online_update=online_update)

    def table(self, table_id: str, online_update: bool = False):
        """
        Get table from table_id, equivalent to get_table
        :param table_id:
        :param online_update:True is use local backup data,False is use online data
        :return:
        """
        return self.get_table(table_id, online_update)

    def get_tables_by_name(self, table_name: str):
        return [table for table in self.get_all_tables() if table.name == table_name]

    def get_all_tables(self, online_update: bool = False):
        """

        :param online_update:True is use local backup data,False is use online data
        :return:
        """
        get_tables_input = GetTablesInput(workspaceId=self.workspace.id, coreId=self.id)
        return [self.get_table(table.id, online_update) for table in self.workspace.client.get_all_tables(get_tables_input).result]

    def get_all_tables_dict(self):
        return MessageToDict(self.workspace.client.get_all_tables(GetTablesInput(workspaceId=self.workspace.id, coreId=self.id)))

    def add_table(self, table_name: str):

        """
        Create a table based on table_name
        not specified
        :param table_name:
        :return:
        """

        return Table(name=table_name, core=self)

    def remove_table(self, table_id: str) -> str:
        return self.workspace.client.remove_table(RemoveTableInput(workspaceId=self.workspace.id, coreId=self.id, tableId=table_id)).id

    def remove_tables(self, table_ids: List[str], mode='ids') -> List[str]:
        """
        You can delete the specified core or all of the core
        :param table_ids:
        :param mode:
            if mode == ids:
                Deletes the specified table id and returns the table id that can be deleted
            if mode == all:
                Delete all table ids and return the deleted tabke id
        :return:
        """
        get_tables_input = GetTablesInput(workspaceId=self.workspace.id, coreId=self.id)
        tables = self.workspace.client.get_all_tables(get_tables_input)
        ids = [table.id for table in tables.result]
        if mode == 'ids':
            table_ids = [table_id for table_id in table_ids if table_id in ids]
        elif mode == 'all':
            table_ids = ids
        else:
            raise ValueError(
                '{} remove_tables mode is not supported, please select mode between ids and all'.format(mode))
        return list(map(lambda table_id: self.workspace.client.remove_table(RemoveTableInput(workspaceId=self.workspace.id, coreId=self.id, tableId=table_id)).id, table_ids))

    def update_table_name(self, table_name: str, table_id: str):
        if '"' in table_name:
            raise ValueError('Double quotes cannot exist in table name {}'.format(table_name))
        return Table(name=table_name, table_id=table_id, core=self, operation='update')

    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event["coreId"]

    def snapshots(self, table_ids: list = None):
        """
        add core snapshots method
        :return:
        """
        if not table_ids:
            tables = self.get_all_tables(True)
        else:
            tables = [self.table(table_id, True) for table_id in table_ids]
        # tables = [self.table('tblb5c3da9c2e81f59e'), self.get_table('tblb5c3da9ccd86e3bc')]
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        core = self.workspace.add_core(core_name='-'.join([self.name, local_time]), color=self.color,
                                       icon=self.icon)
        column_id_table_id = {}  # {column_id:table_id}
        table_id_column_id_index = {}  # {table_id:{column_id:index}}
        table_id_index = {}  # {table_id:column_index}
        old_core_table_data_frame = {}  # {(workspace_id,core_id,table_id):data_frame}
        other_core_table_data_frame = {}  # {(workspace_id,core_id,table_id):data_frame}
        old_table_data_frame = {}  # {table_id:data_frame}
        old_table_ids = [table.id for table in tables]
        old_table_config = {}  # {table_id:[column_config]}
        old_table_views = {}  # {table_id:[views]}
        all_dict = {}  # {(old_table_ids.index(table.id), col_index): data.values}
        self._process_raw_tables_data(tables=tables, old_core_table_data_frame=old_core_table_data_frame,
                                      old_table_config=old_table_config, old_table_views=old_table_views,
                                      old_table_ids=old_table_ids, all_dict=all_dict,
                                      other_core_table_data_frame=other_core_table_data_frame,
                                      column_id_table_id=column_id_table_id,
                                      table_id_column_id_index=table_id_column_id_index,
                                      old_table_data_frame=old_table_data_frame, table_id_index=table_id_index)
        new_core_table_data_frame, new_core_tables, new_table_data_frame, add_view_list = \
            self._add_new_tables(tables=tables,
                                 core=core,
                                 old_table_config=old_table_config,
                                 old_table_data_frame=old_table_data_frame,
                                 table_id_column_id_index=table_id_column_id_index,
                                 table_id_index=table_id_index,
                                 old_table_views=old_table_views)
        self._remove_redundant_columns(old_core_table_data_frame=old_core_table_data_frame,
                                       other_core_table_data_frame=other_core_table_data_frame,
                                       new_core_table_data_frame=new_core_table_data_frame)

        # self._reset_reference(all_dict=all_dict, new_core_tables=new_core_tables,
        #                       new_table_data_frame=new_table_data_frame)
        # self._reset_lookup(tables=tables, table_id_column_id_index=table_id_column_id_index,
        #                    old_table_ids=old_table_ids, new_core_tables=new_core_tables,
        #                    new_table_data_frame=new_table_data_frame)
        self._add_view_list(add_view_list=add_view_list)
        return core

    def _process_raw_tables_data(self, tables, old_core_table_data_frame, old_table_config, old_table_views,
                                 old_table_ids, all_dict, other_core_table_data_frame, column_id_table_id,
                                 table_id_column_id_index, old_table_data_frame, table_id_index):
        """
        Process the original table data, encapsulate a variety of dict
        :param tables:
        :param old_core_table_data_frame: {(workspace_id,core_id,table_id):data_frame}
        :param old_table_config: {table_id:[column_config]}
        :param old_table_views: {table_id:[views]}
        :param old_table_ids:
        :param all_dict: {(old_table_ids.index(table.id), col_index): data.values}
        :param other_core_table_data_frame:
        :param column_id_table_id:
        :param table_id_column_id_index: {table_id:{column_id:index}}
        :param old_table_data_frame: {table_id:data_frame}
        :param table_id_index:{table_id:column_index}
        :return:
        """
        for i, table in enumerate(tables):
            if not table.data.views:
                continue
            old_core_table_data_frame[(self.workspace.id, self.id, table.id)] = table.data_frame()
            column_configs = list(table.data.columns.values())
            column_id_index = {}  # {column_id:index}
            column_index_id = {}  # {index:column_id}
            old_table_config[table.id] = column_configs
            old_table_views[table.id] = table.get_views(online_update=False)
            column_index = {index: column_config.foreign_table_id for index, column_config in enumerate(column_configs)
                            if
                            FieldType(
                                column_config.field_type) is FieldType.RECORD_REFERENCE and column_config.foreign_table_id in old_table_ids}
            df = table.data_frame()
            array = df.copy()
            for col_index, table_id in column_index.items():
                # Gets the index of the row of the current table，such as
                # {'rowb580a4b7870d4775': 0, 'rowb580a4b7c58ea840': 1}
                row_id_dict = {row_id: i for i, row_id in enumerate(self.get_table(table_id, True).data_frame().index.values)}
                data = array.iloc[:, col_index].map(
                    lambda x: {old_table_ids.index(table_id): [row_id_dict[y['id']] for y in x] if x else ''})
                # (i,col_index) Represents the index number of the current table and the index with external keys,
                # such as (0,0), data.values means Data for each row，such as [{4: [0, 1]} {4: ''}] ,4 is The index
                # number of the associated table，[0,1] means The line number of this outer key table，Each dictionary
                # represents a line
                all_dict.update({(old_table_ids.index(table.id), col_index): data.values})

            for index, column_config in enumerate(column_configs):
                if FieldType(column_config.field_type) is FieldType.RECORD_REFERENCE:
                    if column_config.foreign_table_id not in [table.id for table in tables]:
                        other_core_table_data_frame[(column_config.foreign_workspace_id, column_config.foreign_core_id,
                                                     column_config.foreign_table_id)] = Treelab(
                            token=self.workspace.token).get_workspace(
                            workspace_id=column_config.foreign_workspace_id).core(core_id=
                                                                                  column_config.foreign_core_id).table(
                            table_id=column_config.foreign_table_id, online_update=True).data_frame()
                column_id_index.update({column_config.id: index})
                column_index_id.update({index: column_config.id})
                column_id_table_id[column_config.id] = table.id
            table_id_column_id_index.update({table.id: column_id_index})
            old_table_data_frame[table.id] = table.data_frame()
            view_filter_column = []  # [column_id_index]
            for view in table.get_views(online_update=False):
                view_filter_column.append(list(map(lambda x: column_id_index[x], view.view_options.get('columns', []))))
            table_id_index.update({table.id: view_filter_column})

    def _add_new_tables(self, tables, core, old_table_config, old_table_data_frame, table_id_column_id_index, table_id_index, old_table_views):
        """
        add new tables
        :param tables: old tables
        :param core: new core
        :param old_table_config: {table_id:[column_config]}
        :param old_table_data_frame: {table_id:data_frame}
        :param table_id_column_id_index: {table_id:{column_id:index}}
        :param table_id_index: {table_id:column_index}
        :param old_table_views: {table_id:[views]}
        :return:
        """
        new_core_tables = []  # [table]
        new_table_ids = []
        new_table_data_frames = []  # [data_frame]
        new_core_table_data_frame = {}  # {(workspace_id,core_id,table_id):data_frame}
        add_view_list = []  # (new_table,view.name,ViewType(view.view_type,column_ids,start_data,end_date))
        for i, table in enumerate(tables):
            if not table.data.views:
                continue
            table_name = table.name
            new_table = core.add_table(table_name)
            new_table_ids.append(new_table.id)
            column_configs = old_table_config[table.id]
            df = old_table_data_frame[table.id]
            old_rows = df.iloc[:, 0]
            columns = []
            for column_config in column_configs:
                if column_config.field_type is FieldType.LOOKUP:
                    column_id_index = table_id_column_id_index[table.id]
                    column_config.record_reference_column_id = columns[
                        column_id_index.get(column_config.record_reference_column_id)].id
                if column_config.field_type is FieldType.UNIQUE_ID:
                    column_config.field_type = FieldType.TEXT
                column_array = new_table.add_columns(column_configs=[column_config])
                columns.append(column_array[0])
            if len(old_rows) > 0:
                rows = new_table.add_rows(n_rows=len(old_rows))
                cells = new_table.get_cells(rows, columns, mode='intersection').reshape(df.shape)
                cells.update(df.values)
            indexs = table_id_index[table.id]
            if indexs == 1:
                continue
            old_views = old_table_views[table.id]
            for column_indexs, view in zip(indexs[1:], old_views[1:]):
                column_ids = [columns[index].id for index in column_indexs] if column_indexs else [column.id for column
                                                                                                   in columns]
                old_view_column_ids = [column.id for column in view.get_columns()]
                start_data = view.view_options.get('startDate', '')
                end_date = view.view_options.get('endDate', '')
                start_data = column_ids[old_view_column_ids.index(start_data)] if start_data else ''
                end_date = column_ids[old_view_column_ids.index(end_date)] if end_date else ''
                # new_table.add_view_filter(view_name=view.name, view_type=ViewType(view.view_type),
                #                           column_ids=column_ids,
                #                           start_date=start_data,
                #                           end_date=end_date)
                add_view_list.append((new_table, view.name, ViewType(view.view_type), column_ids, start_data, end_date))
            extra_column_ids = list(
                set(column.id for column in new_table.get_columns()) - set(column.id for column in columns))
            if extra_column_ids:
                new_table.remove_columns(column_ids=extra_column_ids)
            new_table_data_frame = new_table.data_frame()
            new_core_tables.append(new_table)
            new_table_data_frames.append(new_table_data_frame)
            new_core_table_data_frame[(self.workspace.id, core.id, new_table.id)] = new_table_data_frame
        return new_core_table_data_frame, new_core_tables, new_table_data_frames, add_view_list

    def _remove_redundant_columns(self, old_core_table_data_frame, other_core_table_data_frame, new_core_table_data_frame):
        """
        Delete the redundant columns
        :param old_core_table_data_frame: # {(workspace_id,core_id,table_id):data_frame}
        :param other_core_table_data_frame: {(workspace_id,core_id,table_id):data_frame}
        :param new_core_table_data_frame: {(workspace_id,core_id,table_id):data_frame}
        :return:
        """

        def _remove_extra_columns(collect, df):
            workspace_id, core_id, table_id = collect
            table = Treelab(self.workspace.token).workspace(workspace_id=workspace_id).core(core_id=core_id).table(
                table_id=table_id, online_update=True)
            column_ids = [column.split('::')[0] for column in
                          list(set(list(table.data_frame().columns)) - set(list(df.columns)))]
            table.remove_columns(column_ids)

        for key, value in old_core_table_data_frame.items():
            _remove_extra_columns(key, value)
        for key, value in other_core_table_data_frame.items():
            _remove_extra_columns(key, value)
        for key, value in new_core_table_data_frame.items():
            _remove_extra_columns(key, value)

    @staticmethod
    def _reset_reference(all_dict, new_core_tables, new_table_data_frame):
        """
        reset reference
        :param all_dict:  {(old_table_ids.index(table.id), col_index): data.values}
        :param new_core_tables: [table]
        :param new_table_data_frame: [data_frame]
        :return:
        """
        for k, v in all_dict.items():
            old_table_index, old_column_index = k
            table_index_row_index = v
            new_core_table = new_core_tables[old_table_index]
            new_core_table = new_core_table.core.get_table(table_id=new_core_table.id, online_update=True)
            column = new_core_table.get_columns()[old_column_index]
            rows = new_core_table.get_rows()
            list_rows = []
            foreign_table_id = ''
            for indexs_ in table_index_row_index:
                for t_id, row_ids in indexs_.items():
                    foreign_table_id = new_core_tables[t_id].id
                    if row_ids:
                        ll = list(new_table_data_frame[t_id].index)
                        up_row_ids = ','.join([ll[row_id] for row_id in row_ids])
                    else:
                        up_row_ids = ''
                    list_rows.append(up_row_ids)
            column = new_core_table.update_column_recode_reference(column_id=column.id,
                                                                   field_name=column.name,
                                                                   foreign_table_id=foreign_table_id,
                                                                   foreign_core_id=new_core_table.core.id,
                                                                   foreign_workspace_id=
                                                                   new_core_table.workspace.id)
            cells = new_core_table.get_cells(rows, [column], mode='intersection')
            cells.update(np.array([list_rows]))

    @staticmethod
    def _reset_lookup(tables, table_id_column_id_index, old_table_ids, new_core_tables, new_table_data_frame):
        """
        reset lookup
        :param tables: old tables
        :param table_id_column_id_index: {table_id:column_index}
        :param old_table_ids: {table_id:column_index}
        :param new_core_tables: [table]
        :param new_table_data_frame: {(workspace_id,core_id,table_id):data_frame}
        :return:
        """
        for i, table in enumerate(tables):
            columns = table.get_columns()
            column_id_index = table_id_column_id_index[table.id]
            for j, column in enumerate(columns):
                if column.field_type is FieldType.LOOKUP:
                    c = columns[column_id_index[column.record_reference_column_id]]
                    if c.foreign_table_id in old_table_ids:
                        index_t = old_table_ids.index(c.foreign_table_id)
                        index_c = table_id_column_id_index[old_table_ids[index_t]][column.foreign_lookup_column_id]
                        new_table = new_core_tables[i]
                        new_c = new_table.get_columns()[j]
                        new_table.update_column_lookup(column_id=new_c.id, field_name=new_c.name,
                                                       record_reference_column_id=new_c.record_reference_column_id,
                                                       foreign_lookup_column_id=
                                                       new_table_data_frame[index_t].columns[index_c].split('::')[0])

    @staticmethod
    def _add_view_list(add_view_list):
        """
        Add a new view
        :param add_view_list:
        :return:
        """
        for view in add_view_list:
            new_table, name, view_type, column_ids, start_data, end_date = view
            new_table.add_view_filter(view_name=name, view_type=view_type,
                                      column_ids=column_ids,
                                      start_date=start_data,
                                      end_date=end_date)

    def update_table_order(self, table_id: str, after_table_id: str):
        """
        Modify table order
        :param table_id:
        :param after_table_id:
        :return:
        """
        self.workspace.client.update_table_order(ReorderTableInput(workspaceId=self.workspace.id, coreId=self.id, tableId=table_id, afterTableId=after_table_id))


class Table(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, name: str = None, table_id: str = None, core: Core = None, online_update: bool = True, operation='add'):
        """

        :param name:
        :param table_id:
        :param core:
        :param online_update:True is use local backup data,False is use online data
        :param operation: this contains add and update
        """
        super().__init__()
        self._name = name
        self.online_update = online_update
        self._workspace = core.workspace
        self.core = core
        if operation == 'add':
            self._id = self._add_table(table_id, core)
        elif operation == 'update':
            self._id = self._update_table_name(table_id, core)
        else:
            raise ValueError(f"Unsupported operations {operation}")

    def get_name(self):
        """
        it is for get table name
        :return:
        """
        if self.name == 'default_name' and self.id != 'default_id':
            table_projection = self.workspace.client.get_table(
                GetTableInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id))
            self._name = table_projection.name
        return self.name

    def set_online_update_false(self):
        """
        let table use online data
        :return:
        """
        self.online_update = False

    def set_online_update_true(self):
        """
        let table use backup data
        :return:
        """
        self.online_update = True

    def close(self):
        """
        If the table no longer have a GRPC connection, call close to close the connection
        :return:
        """
        self.core.workspace.close()

    @staticmethod
    def _update_data(table):
        get_table_input = GetTableInput(workspaceId=table.workspace.id,
                                        coreId=table.core.id, tableId=table.id)
        table_projection = table.core.workspace.client.get_table(get_table_input)
        table._data = json.loads(MessageToJson(table_projection))

    def _add_table(self, table_id: str, core: Core):
        if core:
            self.core = core
            self._workspace = self.core.workspace
            if table_id:
                table_projection = self.workspace.client.get_table(GetTableInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=table_id))
                self._name = table_projection.name
                return table_id
            else:
                if '"' in self.name:
                    raise ValueError('Double quotes cannot exist in table name ', self.name)
                add_table_input = AddTableInput(workspaceId=self.workspace.id, coreId=self.core.id, tableName=self.name)
                table_id = self.workspace.client.add_table(add_table_input).id
                self._id = table_id
                return table_id
        else:
            raise ValueError("You need to get/create the table from the core!")

    def _update_table_name(self, table_id: str, core: Core):
        self.core = core
        self._workspace = self.core.workspace
        _ = self.workspace.client.update_table_name(
            UpdateTableNameInput(workspaceId=self.workspace.id, coreId=core.id, tableId=table_id, tableName=self.name)).id
        self._id = table_id
        return table_id

    def data_frame(self, view_id: str = ''):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :param view_id: If empty, the default is the data of the first view
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        return view.data_frame

    def data_frames(self, view_ids: List[str] = None):
        """
        Convert the original view's data to a data_frame format，
        the index of the data_frame is the row id, and the column is the column id
        :param view_ids:
        :return: pandas.data_frame
        """
        views = self.get_views(view_ids=view_ids, online_update=self.online_update) if view_ids else self.get_views(online_update=self.online_update)
        return [view.data_frame for view in views]

    def get_row(self, row_id: str, view_id: str = ''):
        """
        Get row by row_id
        :param row_id:
        :param view_id:
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        online_update = copy.deepcopy(self.online_update)
        if not online_update:
            self.online_update = True
        row = view.get_row(row_id)
        if online_update != self.online_update:
            self.online_update = online_update
        return row

    def row(self, row_id: str, view_id: str = ''):
        """
        Get row by row_id, equivalent to get_row
        :param row_id:
        :param view_id:
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        return view.get_row(row_id=row_id)

    def add_row(self):
        """
        Add a single row to the table
        :return:
        """
        return Row(table=self)

    def add_rows(self, n_rows: int):
        """
        Add rows with number
        :param n_rows:
        :return:
        """
        if n_rows <= 0:
            raise ValueError('n_rows has to be a number larger than 0')
        return RowArray(parent_object=self, objects=[self.add_row() for _ in range(n_rows)], workspace=self.workspace)

    def get_rows(self, row_ids: List[str] = None, view_id: str = ''):
        """
        Get rows by row_ids, if row_ids are not specified, get all rows from the table,
        :param row_ids:
        :param view_id
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        online_update = copy.deepcopy(self.online_update)
        self.online_update = True if not online_update else self.online_update
        row_array = view.get_rows(row_ids)
        if online_update != self.online_update:
            self.online_update = online_update
        return row_array

    def remove_row(self, row_id: str) -> str:
        return self.workspace.client.remove_row(RemoveRowInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, rowId=row_id)).id

    def remove_rows(self, row_ids: List[str] = None, mode='ids') -> List[str]:
        """
        You can delete the specified row or all of the row
        :param row_ids:
        :param mode:
            if mode == ids:
                Deletes the specified row id and returns the row id that can be deleted
            if mode == all:
                Delete all row ids and return the deleted row id
        :return:
        """
        ids = [row.id for row in self.get_rows()]
        if mode == 'ids':
            row_ids = [row_id for row_id in row_ids if row_id in ids]
        elif mode == 'all':
            row_ids = ids
        else:
            raise ValueError('{} remove_rows mode is not supported, please select mode between ids and all'.format(mode))
        return list(map(lambda row_id: self.workspace.client.remove_row(RemoveRowInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, rowId=row_id)).id, row_ids))

    def update_row_order(self, row_id: str, after_row_id: str, view_id: str = None):
        """
        row id comes after after row id
        :param row_id:
        :param after_row_id:
        :param view_id:
        :return:
        """
        view = self.get_views()[0] if not view_id else self.get_view(view_id)
        self.workspace.client.update_row_order(ReorderRowInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view.id, rowId=row_id, afterRowId=after_row_id))

    def get_cell(self, row, column, view_id: str = ''):
        """
        Get a single cell from known row and column
        :param row:
        :param column:
        :param view_id:
        :param
        :return:
        """
        view = self.get_view(view_id) if view_id else self.get_views()[0]
        online_update = copy.deepcopy(self.online_update)
        if not online_update:
            self.online_update = True
        cell = view.get_cell(row, column)
        if online_update != self.online_update:
            self.online_update = online_update
        return cell

    def get_cells(self, rows: List = None, columns: List = None, mode: str = 'all', view_id: str = ''):
        """
        Get cells from rows and columns
        :param rows:
        :param columns:
        :param mode:
            if mode == intersection:
                returns the cells on the intersection of all rows and columns
            if mode == pair:
                returns the cells based on row/column pairs, in this case, the size
                of rows has to be equal to the size of column
            if mode == all:
                return all cells under this table, rows and columns will be ignored in this case
        :param view_id:
        :return: CellArray: CellCollection
        """
        view = self.get_view(view_id) if view_id else self.get_views()[0]
        online_update = copy.deepcopy(self.online_update)
        if not online_update:
            self.online_update = True
        cell_array = view.get_cells(rows, columns, mode)
        if online_update != self.online_update:
            self.online_update = online_update
        return cell_array

    def _add_column(self, field_type: FieldType = None, field_name: str = None,
                    foreign_table_id: str = None,
                    column_config_input: ColumnConfigInput = None, default_number: float = 0.0,
                    precision: int = 1, options: List[List[Union[OptionInput, Any]]] = None, date_format: DateFormat = None,
                    include_time: bool = True,
                    time_format: TimeFormat = None, use_gmt: bool = True, default_checked: bool = False,
                    record_reference_column_id: str = '',
                    foreign_lookup_column_id: str = '', id_prefix: str = '', foreign_core_id: str = '',
                    foreign_workspace_id: str = '', formula: str = '', rating_max: int = 1, rating_style: RatingStyleType = RatingStyleType.STAR):
        """
        Add a single column or column_config_input as as parameter which includes the four mentioned above
        :param field_type:
        :param field_name:
        :param foreign_table_id:
        :param column_config_input:
        :param default_number:
                    FieldType is NUMBER
        :param precision:
                    FieldType is NUMBER
        :param options:
                    List contains two parameters, name and color. Name is of type STR and color is of type color
                    FieldType is MULTI_SELECT or SELECT
                    example:
                        [['a',Color.lightRed],
                        ['b',Color.pink]]
        :param date_format:
                    FieldType is DATETIME
        :param include_time:
                    FieldType is DATETIME
        :param time_format:
                    FieldType is DATETIME
        :param use_gmt:
                    FieldType is DATETIME
        :param default_checked:
                    FieldType is CHECKBOX
        :param record_reference_column_id:
        :param foreign_lookup_column_id:
        :param id_prefix:
        :param foreign_core_id:
        :param foreign_workspace_id:
        :param formula:
        :param rating_max:
        :param rating_style:
        :return:
        """
        if field_name is not None and '"' in field_name:
            raise ValueError('Double quotes cannot exist in field name')
        if column_config_input:
            if column_config_input.name != '' and '"' in column_config_input.name:
                raise ValueError('Double quotes and empty cannot exist in field name')
            return Column(table=self, field_type=FieldType(column_config_input.type),
                          field_name=column_config_input.name,
                          foreign_table_id=column_config_input.foreignTableId,
                          default_number=column_config_input.defaultNumber,
                          precision=column_config_input.precision, options=column_config_input.options,
                          date_format=DateFormat(column_config_input.dateFormat) if column_config_input.dateFormat else '',
                          include_time=column_config_input.includeTime,
                          time_format=TimeFormat(column_config_input.timeFormat) if column_config_input.timeFormat else '',
                          use_gmt=column_config_input.useGMT,
                          default_checked=column_config_input.defaultChecked,
                          record_reference_column_id=column_config_input.recordReferenceColumnId,
                          foreign_lookup_column_id=column_config_input.foreignLookupColumnId,
                          id_prefix=column_config_input.idPrefix,
                          foreign_core_id=column_config_input.foreignCoreId,
                          foreign_workspace_id=column_config_input.foreignWorkspaceId, formula=column_config_input.formula,
                          rating_max=column_config_input.ratingMax,
                          rating_style=RatingStyleType(column_config_input.ratingStyle) if column_config_input.ratingStyle else '')
        else:
            if field_type is None or field_name is None:
                raise ValueError('Field type, field name  cannot be None')
            return Column(table=self, field_type=field_type, field_name=field_name,
                          foreign_table_id=foreign_table_id, default_number=default_number,
                          precision=precision, options=options, date_format=date_format,
                          include_time=include_time,
                          time_format=time_format, use_gmt=use_gmt,
                          default_checked=default_checked,
                          record_reference_column_id=record_reference_column_id,
                          foreign_lookup_column_id=foreign_lookup_column_id,
                          id_prefix=id_prefix,
                          foreign_core_id=foreign_core_id,
                          foreign_workspace_id=foreign_workspace_id, formula=formula,
                          rating_max=rating_max,
                          rating_style=rating_style)

    def add_column_text(self, field_name: str):
        return self._add_column(field_type=FieldType.TEXT, field_name=field_name)

    def add_column_datetime(self, field_name: str, include_time: bool = True,
                            use_gmt: bool = True, date_format: DateFormat = DateFormat.FRIENDLY,
                            time_format: TimeFormat = TimeFormat.TWELVE_HOUR):
        return self._add_column(field_type=FieldType.DATETIME, field_name=field_name, date_format=date_format, include_time=include_time, time_format=time_format, use_gmt=use_gmt)

    def add_column_recode_reference(self, field_name: str, foreign_table_id: str, foreign_core_id: str, foreign_workspace_id: str):
        return self._add_column(field_type=FieldType.RECORD_REFERENCE, field_name=field_name, foreign_table_id=foreign_table_id, foreign_core_id=foreign_core_id, foreign_workspace_id=foreign_workspace_id)

    def add_column_number(self, field_name: str, default_number: int = 0, precision: int = 1):
        return self._add_column(field_type=FieldType.NUMBER, field_name=field_name, default_number=default_number, precision=precision)

    def add_column_multi_select(self, field_name: str, options: List[List[Union[OptionInput, Any]]]):
        return self._add_column(field_type=FieldType.MULTI_SELECT, field_name=field_name, options=options)

    def add_column_select(self, field_name: str, options: List[List[Union[OptionInput, Any]]]):
        return self._add_column(field_type=FieldType.SELECT, field_name=field_name, options=options)

    def add_column_checkbox(self, field_name: str, default_checked: bool = False):
        return self._add_column(field_type=FieldType.CHECKBOX, field_name=field_name, default_checked=default_checked)

    def add_column_lookup(self, field_name: str, record_reference_column_id: str, foreign_lookup_column_id: str):
        return self._add_column(field_type=FieldType.LOOKUP, field_name=field_name, record_reference_column_id=record_reference_column_id, foreign_lookup_column_id=foreign_lookup_column_id)

    def add_column_rating(self, field_name: str, rating_max: int, rating_style: RatingStyleType.STAR):
        return self._add_column(field_type=FieldType.RATING, field_name=field_name, rating_max=rating_max, rating_style=rating_style)

    def add_column_unique_id(self, field_name: str, id_prefix: str):
        return self._add_column(field_type=FieldType.UNIQUE_ID, field_name=field_name, id_prefix=id_prefix)

    def add_column_formula(self, field_name: str, formula: str):
        return self._add_column(field_type=FieldType.FORMULA, field_name=field_name, formula=formula)

    def add_column_attachments(self, field_name: str):
        return self._add_column(field_type=FieldType.ATTACHMENT, field_name=field_name)

    def _update_column(self, column_id: str, field_type: FieldType = None, field_name: str = None,
                       foreign_table_id: str = None,
                       column_config_input: ColumnConfigInput = None, default_number: float = 0.0,
                       precision: int = 1, options: List[List[Union[OptionInput, Any]]] = [], date_format: DateFormat = None,
                       include_time: bool = True,
                       time_format: TimeFormat = None, use_gmt: bool = True, default_checked: bool = False,
                       record_reference_column_id: str = '',
                       foreign_lookup_column_id: str = '', id_prefix: str = '', foreign_core_id: str = '',
                       foreign_workspace_id: str = '', rating_max: int = 1, rating_style: RatingStyleType = RatingStyleType.STAR, formula: str = ''):
        """
        Add a single column or column_config_input as as parameter which includes the four mentioned above
        :param column_id
        :param field_type:
        :param field_name:
        :param foreign_table_id:
        :param column_config_input:
        :param default_number:
                    FieldType is NUMBER
        :param precision:
                    FieldType is NUMBER
        :param options:
                    List contains two parameters, name and color. Name is of type STR and color is of type color
                    FieldType is MULTI_SELECT or SELECT
                    example:
                        [['a',Color.lightRed],
                        ['b',Color.pink]]
        :param date_format:
                    FieldType is DATETIME
        :param include_time:
                    FieldType is DATETIME
        :param time_format:
                    FieldType is DATETIME
        :param use_gmt:
                    FieldType is DATETIME
        :param default_checked:
                    FieldType is CHECKBOX
        :param record_reference_column_id:
        :param foreign_lookup_column_id:
        :param id_prefix:
        :param foreign_workspace_id:
        :param foreign_core_id:
        :param rating_max:
        :param rating_style:
        :param formula:
        :return:
        """
        if field_name is not None and '"' in field_name:
            raise ValueError('Double quotes cannot exist in field name')
        if column_config_input:
            if column_config_input.name != '' and '"' in column_config_input.name:
                raise ValueError('Double quotes and empty cannot exist in field name')
            return Column(table=self, col_id=column_id, field_type=FieldType(column_config_input.type),
                          field_name=column_config_input.name,
                          foreign_table_id=column_config_input.foreignTableId,
                          default_number=column_config_input.defaultNumber,
                          precision=column_config_input.precision, options=column_config_input.options,
                          date_format=DateFormat(
                              column_config_input.dateFormat) if column_config_input.dateFormat else '',
                          include_time=column_config_input.includeTime,
                          time_format=TimeFormat(
                              column_config_input.timeFormat) if column_config_input.timeFormat else '',
                          use_gmt=column_config_input.useGMT, default_checked=column_config_input.defaultCheckbox,
                          record_reference_column_id=column_config_input.recordReferenceColumnId,
                          foreign_lookup_column_id=column_config_input.foreignLookupColumnId,
                          id_prefix=column_config_input.idPrfex, operation='update_column',
                          foreign_core_id=column_config_input.foreignCoreId,
                          foreign_workspace_id=column_config_input.foreignWorkspaceId,
                          rating_max=column_config_input.ratingMax,
                          rating_style=column_config_input.ratingStyle,
                          formula=column_config_input.formula)
        else:
            if field_type is None or field_name is None:
                raise ValueError('Field type, field name  cannot be None')
            return Column(table=self, col_id=column_id, field_type=field_type, field_name=field_name,
                          foreign_table_id=foreign_table_id, default_number=default_number,
                          precision=precision, options=options, date_format=date_format,
                          include_time=include_time,
                          time_format=time_format, use_gmt=use_gmt, default_checked=default_checked,
                          record_reference_column_id=record_reference_column_id,
                          foreign_lookup_column_id=foreign_lookup_column_id, id_prefix=id_prefix,
                          operation='update_column', foreign_core_id=foreign_core_id,
                          foreign_workspace_id=foreign_workspace_id,
                          rating_max=rating_max,
                          rating_style=rating_style,
                          formula=formula)

    def update_column_text(self, column_id: str, field_name: str):
        return self._update_column(column_id=column_id, field_type=FieldType.TEXT, field_name=field_name)

    def update_column_datetime(self, column_id: str, field_name: str, include_time: bool = True,
                               use_gmt: bool = True, date_format: DateFormat = DateFormat.FRIENDLY,
                               time_format: TimeFormat = TimeFormat.TWELVE_HOUR):
        return self._update_column(column_id=column_id, field_type=FieldType.DATETIME,
                                   field_name=field_name,
                                   date_format=date_format,
                                   include_time=include_time, time_format=time_format,
                                   use_gmt=use_gmt)

    def update_column_recode_reference(self, column_id: str, field_name: str, foreign_table_id: str, foreign_core_id: str, foreign_workspace_id: str):
        return self._update_column(column_id=column_id, field_type=FieldType.RECORD_REFERENCE,
                                   field_name=field_name,
                                   foreign_table_id=foreign_table_id,
                                   foreign_core_id=foreign_core_id,
                                   foreign_workspace_id=foreign_workspace_id)

    def update_column_number(self, column_id: str, field_name: str, default_number: int = 0, precision: int = 1):
        return self._update_column(column_id=column_id, field_type=FieldType.NUMBER, field_name=field_name, default_number=default_number, precision=precision)

    def update_column_multi_select(self, column_id: str, field_name: str, options: List[List[Union[OptionInput, Any]]]):
        return self._update_column(column_id=column_id, field_type=FieldType.MULTI_SELECT, field_name=field_name, options=options)

    def update_column_select(self, column_id: str, field_name: str, options: List[List[Union[OptionInput, Any]]]):
        return self._update_column(column_id=column_id, field_type=FieldType.SELECT, field_name=field_name, options=options)

    def update_column_checkbox(self, column_id: str, field_name: str, checkbox: bool = False):
        return self._update_column(column_id=column_id, field_type=FieldType.CHECKBOX, field_name=field_name, default_checked=checkbox)

    def update_column_lookup(self, column_id: str, field_name: str, record_reference_column_id: str, foreign_lookup_column_id: str):
        return self._update_column(column_id=column_id, field_type=FieldType.LOOKUP, field_name=field_name, record_reference_column_id=record_reference_column_id, foreign_lookup_column_id=foreign_lookup_column_id)

    def update_column_unique_id(self, column_id: str, field_name: str, id_prefix: str):
        return self._update_column(column_id=column_id, field_type=FieldType.UNIQUE_ID, field_name=field_name, id_prefix=id_prefix)

    def update_column_rating(self, column_id: str, field_name: str, rating_max: int, rating_style: RatingStyleType.STAR):
        return self._update_column(column_id=column_id, field_type=FieldType.RATING, field_name=field_name, rating_max=rating_max, rating_style=rating_style)

    def update_column_formula(self, column_id: str, field_name: str, formula: str):
        return self._update_column(column_id=column_id, field_type=FieldType.FORMULA, field_name=field_name, formula=formula)

    def update_column_width(self, column_id: str, column_width: int, view_id: str = None):
        """
        Modify the width of the column
        :param column_id:
        :param column_width:
        :param view_id:
        :return:
        """
        view = self.get_views()[0] if not view_id else self.get_view(view_id=view_id)
        self.workspace.client.update_column_width(UpdateColumnWidthInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view.id, columnId=column_id, columnWidth=column_width))

    def update_column_order(self, column_id: str, after_column_id: str, view_id: str = None):
        """
        Column id comes after after column id
        :param column_id:
        :param after_column_id:
        :param view_id:
        :return:
        """
        view = self.get_views()[0] if not view_id else self.get_view(view_id=view_id)
        self.workspace.client.update_column_order(ReorderColumnInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view.id, columnId=column_id, afterColumnId=after_column_id))

    @staticmethod
    def column_config_input_for_record_reference(column_name: str, foreign_table_id: str, foreign_core_id, foreign_workspace_id) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_record_reference
        :param column_name:
        :param foreign_table_id:
        :param foreign_core_id:
        :param foreign_workspace_id:
        :return:
        """
        return ColumnConfigInput(type=FieldType.RECORD_REFERENCE.value, name=column_name,
                                 foreignTableId=foreign_table_id, foreignCoreId=foreign_core_id,
                                 foreignWorkspaceId=foreign_workspace_id)

    @staticmethod
    def column_config_input_for_text(column_name: str) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_text
        :param column_name:
        :return:
        """
        return ColumnConfigInput(type=FieldType.TEXT.value, name=column_name)

    @staticmethod
    def column_config_input_for_datetime(column_name: str,
                                         date_format: DateFormat = DateFormat.FRIENDLY,
                                         include_time: bool = True,
                                         time_format: TimeFormat = TimeFormat.TWELVE_HOUR,
                                         use_gmt: bool = True) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_datetime
        :param column_name:
        :param date_format:
        :param include_time:
        :param time_format:
        :param use_gmt:
        :return:
        """
        return ColumnConfigInput(type=FieldType.DATETIME.value, name=column_name,
                                 dateFormat=date_format.value,
                                 includeTime=include_time, timeFormat=time_format.value,
                                 useGMT=use_gmt)

    @staticmethod
    def column_config_input_for_number(column_name: str, default_number: int = 0, precision: int = 1) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_number
        :param column_name:
        :param default_number:
        :param precision:
        :return:
        """
        return ColumnConfigInput(type=FieldType.NUMBER.value, name=column_name, defaultNumber=default_number, precision=precision)

    @staticmethod
    def column_config_input_for_multi_select(column_name: str, options: List[List[Union[OptionInput, Any]]]) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_multi_select
        :param column_name:
        :param options:
        :return:
        """
        return ColumnConfigInput(type=FieldType.MULTI_SELECT.value, name=column_name, options=options)

    @staticmethod
    def column_config_input_for_select(column_name: str, options: List[List[Union[OptionInput, Any]]]) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_select
        :param column_name:
        :param options:
        :return:
        """
        return ColumnConfigInput(type=FieldType.SELECT.value, name=column_name, options=options)

    @staticmethod
    def column_config_input_for_checkbox(column_name: str, default_checked: bool = False) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_checkbox
        :param column_name:
        :param default_checked:
        :return:
        """
        return ColumnConfigInput(type=FieldType.CHECKBOX.value, name=column_name, defaultChecked=default_checked)

    @staticmethod
    def column_config_input_for_lookup(column_name: str, record_reference_column_id: str, foreign_lookup_column_id: str) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_select
        :param column_name:
        :param record_reference_column_id:
        :param foreign_lookup_column_id:
        :return:
        """
        return ColumnConfigInput(type=FieldType.LOOKUP.value, name=column_name, recordReferenceColumnId=record_reference_column_id, foreignLookupColumnId=foreign_lookup_column_id)

    @staticmethod
    def column_config_input_for_unique_id(column_name: str, id_prefix: str) -> ColumnConfigInput:
        """
        ColumnConfigInput of add_column_select
        :param column_name:
        :param id_prefix:
        :return:
        """
        return ColumnConfigInput(type=FieldType.UNIQUE_ID.value, name=column_name, idPrefix=id_prefix)

    @staticmethod
    def column_config_input_for_formula(column_name: str, formula: str) -> ColumnConfigInput:
        """
        ColumnConfigInput of formula
        :param column_name:
        :param formula:
        :return:
        """
        return ColumnConfigInput(type=FieldType.FORMULA.value, name=column_name, formula=formula)

    @staticmethod
    def column_config_input_for_attachments(column_name: str) -> ColumnConfigInput:
        """
        ColumnConfigInput of formula
        :param column_name:
        :return:
        """
        return ColumnConfigInput(type=FieldType.ATTACHMENT.value, name=column_name)

    @staticmethod
    def column_config_input_for_ranting(column_name: str, rating_max: int, rating_style: RatingStyleType):
        return ColumnConfigInput(type=FieldType.RATING.value, name=column_name, ratingMax=rating_max, ratingStyle=rating_style)

    def add_columns(self, column_configs: List[Union[ColumnConfigInput, Any]]):
        """
        Add columns with List of column configs
        :param column_configs:
        :return:
        """
        if isinstance(column_configs[0], Column):
            return ColumnArray(self,
                               [self._add_column(field_type=column_config.field_type,
                                                 field_name=column_config.name,
                                                 foreign_table_id=column_config.foreign_table_id,
                                                 default_number=column_config.default_number,
                                                 precision=column_config.precision,
                                                 options=column_config.options,
                                                 date_format=DateFormat(column_config.date_format) if column_config.date_format else '',
                                                 include_time=column_config.include_time,
                                                 time_format=TimeFormat(column_config.time_format) if column_config.time_format else '',
                                                 use_gmt=column_config.use_gmt,
                                                 record_reference_column_id=column_config.record_reference_column_id,
                                                 foreign_lookup_column_id=column_config.foreign_lookup_column_id,
                                                 id_prefix=column_config.id_prefix,
                                                 foreign_core_id=column_config.foreign_core_id,
                                                 foreign_workspace_id=column_config.foreign_workspace_id,
                                                 formula=column_config.formula,
                                                 rating_max=column_config.ratingMax,
                                                 rating_style=RatingStyleType(column_config.ratingStyle)) if column_config.ratingStyle else ''
                                for column_config in
                                column_configs], self.workspace)
        elif isinstance(column_configs[0], ColumnConfigInput):
            return ColumnArray(self, [self._add_column(column_config_input=column_config) for column_config in column_configs], self.workspace)
        else:
            return None

    def remove_column(self, column_id: str) -> str:
        return self.workspace.client.remove_column(RemoveColumnInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, columnId=column_id)).id

    def remove_columns(self, column_ids: List[str] = None, mode='ids'):
        """
        You can delete the specified columns or all of the columns
        :param column_ids:
        :param mode:
            if mode == ids:
                Deletes the specified column id and returns the column id that can be deleted
            if mode == all:
                Delete all column ids and return the deleted column id
        :return:
        """
        ids = [column.id for column in self.get_columns()]
        if mode == 'ids':
            column_ids = [column_id for column_id in column_ids if column_id in ids]
        elif mode == 'all':
            column_ids = ids
        else:
            raise ValueError(
                '{} remove_cores mode is not supported, please select mode between ids and all'.format(mode))
        return list(map(lambda column_id: self.workspace.client.remove_column(RemoveColumnInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, columnId=column_id)).id, column_ids))

    def get_column_by_id(self, col_id: str, view_id: str = ''):
        """
        Get a single column by column id from the table

        :param col_id:
        :param view_id:To distinguish different views under the table
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        return view.get_column_by_id(col_id)

    def get_columns_by_name(self, field_name: str, view_id: str = ''):
        """
        Get a single column by field name from the table

        :param field_name:
        :param view_id:To distinguish different views under the table
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        online_update = copy.deepcopy(self.online_update)
        if not online_update:
            self.online_update = True
        columns = view.get_columns_by_name(field_name)
        if online_update != self.online_update:
            self.online_update = online_update
        return columns

    def column(self, col_id: str, view_id: str = ''):
        """
        Get a single column by column id from the table, equivalent to get_column_by_id
        :param col_id:
        :param view_id:To distinguish different views under the table
        :return:
        """
        return self.get_column_by_id(col_id=col_id, view_id=view_id)

    def get_columns(self, col_ids: List[str] = None, mode: str = 'all', view_id: str = ''):
        """
        Get either columns by either column ids or all columns under the table
        :param col_ids:
        :param mode:
            if mode == 'id':
                return columns by col_ids
            if mode == 'all':
                return all columns under this table, col_ids, if passed, will be ignored in this case
        :param view_id:To distinguish different views under the table
        :return:
        """
        view = self.get_view(view_id, online_update=self.online_update) if view_id else self.get_views(online_update=self.online_update)[0]
        online_update = copy.deepcopy(self.online_update)
        if not online_update:
            self.online_update = True
        col_array = view.get_columns(col_ids, mode)
        if online_update != self.online_update:
            self.online_update = online_update
        return col_array

    def _get_latest_view(self, view_id: str):
        self._view = View(view_id=view_id, table=self)
        return self._view

    def get_view(self, view_id: str, online_update: bool = True):
        """
        Get a view from view_id
        :param view_id:
        :param online_update: if True get the latest data
        :return:
        """
        return self._view if not online_update and hasattr(self, '_view') else self._get_latest_view(view_id)

    def _get_latest_views(self):
        """
        get latest all views
        :return:
        """
        get_views_input = GetViewsInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self._id)
        views = self.core.workspace.client.get_all_views(get_views_input)
        views_data = json.loads(MessageToJson(views))
        return {view['id']: view for view in views_data['result']}

    def get_views(self, view_ids: List[str] = None, mode: str = 'all', online_update: bool = True):
        """
        Get views by a list of view_ids
        :param view_ids:
        :param mode:
        :param online_update: if True get the latest data
        :return:
        """
        if not online_update and hasattr(self, '_views'):
            all_views = {id: View(table=self, view_id=id, name=view["name"], view_data=_TableData(table=self, table_dict=view)) for id, view in self._views.items()}
        else:
            all_views = {id: View(table=self, view_id=id, name=view["name"], view_data=_TableData(table=self, table_dict=view)) for id, view in self._get_latest_views().items()}
        if mode == 'all':
            views = list(all_views.values())
        elif mode == 'id':
            if view_ids is None:
                raise ValueError('view_ids should not be None when mode equals id')
            views = [all_views.get(view_id) for view_id in view_ids]
        else:
            raise ValueError('{} mode is not supported, please select mode between id and all'.format(mode))
        return ViewArray(parent_object=self, objects=views, workspace=self.workspace)

    def get_views_by_name(self, name: str):
        return self.get_views().select_by_name(name)

    def add_view(self, view_name, column_ids: List[str], view_type: ViewType = ViewType.GRID, start_date: str = '', end_date: str = ''):
        """
        Add a filter view to the table,TIMELINE need start_date and end_date
        :param view_name:
        :param view_type:
        :param column_ids:
        :param start_date: it is start date column id
        :param end_date: it is end date column id
        :return:
        """
        view_options_input = ViewOptionsInput(columns=column_ids, startDate=start_date, endDate=end_date)
        return View(table=self, name=view_name, view_type=view_type, view_options_input=view_options_input)

    def update_view_filter(self, view_id: str, view_name: str, column_ids: List[str] = None, start_date: str = '', end_date: str = ''):
        """
        update a filter view to the table,TIMELINE need start_date and end_date
        :param view_id:
        :param view_name:
        :param column_ids:
        :param start_date:
        :param end_date:
        :return:
        """
        view_options_input = ViewOptionsInput(columns=column_ids, startDate=start_date, endDate=end_date)
        view_update_input = ViewUpdateInput(name=view_name, viewOptions=view_options_input)
        return View(table=self, name=view_name, view_type=self.get_view(view_id).view_type, view_id=view_id, view_update_input=view_update_input, operation='update')

    def remove_view(self, view_id):
        return self.workspace.client.remove_view(RemoveViewInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view_id)).id

    def remove_views(self, view_ids: List[str], mode='ids'):
        """
        You can delete the specified views or all of the views
        :param view_ids:
        :param mode:
            if mode == ids:
                Deletes the specified view id and returns the view id that can be deleted
            if mode == all:
                Delete all view ids and return the deleted view id
        :return:
        """
        ids = [view.id for view in self.get_views(online_update=self.online_update)]
        if mode == 'ids':
            view_ids = [view_id for view_id in view_ids if view_id in ids]
        elif mode == 'all':
            view_ids = ids
        else:
            raise ValueError(
                '{} remove_views mode is not supported, please select mode between ids and all'.format(mode))
        return list(map(lambda view_id: self.workspace.client.remove_view(RemoveViewInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view_id)).id, view_ids))

    def update(self, data_matrix: Union[List[List], np.array, pd.DataFrame]):
        """
        Update table content with data_matrix
        The shape of cell_type_matrix and data_matrix must be consistent and used to verify the cell field type
        :param data_matrix:
        :return:
        """
        self.get_cells().update(data_matrix)

    @property
    def data(self):
        """
        Get the table data in _TableData
        :return:
        """
        if not self.online_update and hasattr(self, '_data'):
            return self._data
        else:
            self._update_data(self)
            return self._data

    def _get_event_id(self, event: EventPayload):
        return event["tableId"]

    def get_lookup_cell_by_column_and_row_id(self, column_id: str, row_id: str, depth: int):
        get_cell_by_column_and_row_id_input = GetCellByColumnAndRowIdInput(rowId=row_id, columnId=column_id, depth=depth)
        cell_data = self.workspace.client.get_lookup_cell(get_cell_by_column_and_row_id_input)
        return MessageToJson(cell_data)

    def update_view_order(self, view_id, after_view_id):
        self.workspace.client.update_view_order(ReorderViewInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.id, viewId=view_id, afterViewId=after_view_id))


class View(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'view_type'}

    def __init__(self, name: str = None, view_options_input: ViewOptionsInput = None, view_type: ViewType = ViewType.GRID, view_id: str = None,
                 table: Table = None, view_options: Dict = None, view_update_input: ViewUpdateInput = None, operation: str = 'add', view_data: dict = None):
        """

        :param name:
        :param view_options_input:
        :param view_type:
        :param view_id:
        :param table:
        :param view_options:
        :param operation: this contains add and update
        """
        super().__init__()
        self._name = name
        self.table = table
        self._workspace = table.core.workspace
        self._id = view_id
        self.view_type = view_type
        self.view_data = view_data
        self.view_options_input = view_options_input
        if operation == 'add':
            self._id = self._add_view(view_id=view_id, table=table)
        elif operation == 'update':
            self._id = self._update_view_filter(view_id, table, view_update_input)
        else:
            raise ValueError('Unsupported operations')
        self.table = table
        self.view_options = view_options

    def close(self):
        """
        If the view no longer have a GRPC connection, call close to close the connection
        :return:
        """
        self.workspace.close()

    def __getitem__(self, item):
        flags = [True if column.split('::')[0] in item or column.split('::')[1] in item else False for column in self.data_frame.columns]
        return self.data_frame.iloc[:, flags]

    def get_df_by_specified_column(self, item: List[str]):
        """
        Gets the data_frame for the specified column
        :param item: it's column_ids or column_names
        :return:
        """
        return self[item]

    @property
    def data(self):
        if self.view_data:
            return self.view_data
        get_view_input = GetViewInput(workspaceId=self.table.core.workspace.id, coreId=self.table.core.id, tableId=self.table.id, viewId=self.id)
        view = self.table.core.workspace.client.get_view(get_view_input)
        self._name = view.name
        return _TableData(self.table, json.loads(MessageToJson(view)))

    @property
    def columns(self):
        return self.data.columns

    @property
    def rows(self):
        return self.data.rows

    @property
    def cells(self):
        return self.data.cells

    @property
    def data_frame(self):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :return:
        """
        return self.data.view_data.get(self.id).df

    def _add_view(self, view_id: str, table: Table):
        if view_id or self.view_data:
            return view_id
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            add_view_input = AddViewInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                          tableId=self.table.id,
                                          view=ViewDefinitionInput(name=self.name, type=self.view_type.value, viewOptions=self.view_options_input, isDefault=False))
            view_id = self.workspace.client.add_view(add_view_input).id
            self._id = view_id
            return view_id
        else:
            raise ValueError("You need to get/create the view from the table!")

    def _update_view_filter(self, view_id: str, table: Table, view_update_input):
        self.table = table
        self.core = self.table.core
        self._workspace = self.core.workspace
        self.workspace.client.update_view(UpdateViewInput(workspaceId=self.workspace.id,
                                                          coreId=self.core.id, tableId=self.table.id,
                                                          viewId=view_id,
                                                          view=view_update_input))
        self._id = view_id
        return view_id

    def _get_event_id(self, event: EventPayload):
        return event['_metadata']['checkPermissionAgainst']['viewIds']

    def get_columns(self, col_ids: List[str] = None, mode: str = 'all'):
        """
        Get either columns by either column ids or all columns under the table
        :param col_ids:
        :param mode:
            if mode == 'id':
                return columns by col_ids
            if mode == 'all':
                return all columns under this table, col_ids, if passed, will be ignored in this case
        :return:
        """
        if mode == 'all':
            columns = list(self.columns.values())
        elif mode == 'id':
            if col_ids is None:
                raise ValueError('col_ids should not be None when mode equals id')
            columns = [self.column(col_id=col_id) for col_id in col_ids]
        else:
            raise ValueError('{} mode is not supported, please select mode between id and all'.format(mode))
        return ColumnArray(self, columns, self.workspace)

    def get_column_by_id(self, col_id: str):
        return self.columns.get(col_id)

    def get_columns_by_name(self, field_name: str):
        """
        Get a single column by field name from the table

        :param field_name:
        :return:columns
        """
        return self.get_columns(mode='all').select_by_name(field_name)

    def column(self, col_id: str):
        """
        Get a single column by column id from the table, equivalent to get_column_by_id
        :param col_id:
        :return:
        """
        return self.get_column_by_id(col_id=col_id)

    def get_row(self, row_id: str):
        """
        Get row by row_id
        :param row_id:
        :return:
        """
        return self.rows.get(row_id)

    def row(self, row_id: str):
        return self.get_row(row_id=row_id)

    def get_rows(self, row_ids: List[str] = None):
        """
        Get rows by row_ids, if row_ids are not specified, get all rows from the table,
        :param row_ids:
        :return:
        """

        rows = [self.get_row(row_id=row_id) for row_id in row_ids] if row_ids else list(self.rows.values())
        return RowArray(parent_object=self, objects=rows, workspace=self.workspace)

    def get_cell(self, row, column):
        """
        Get a single cell from known row and column
        :param row:
        :param column:
        :param
        :return:
        """
        return Cell(self.table, self, row, column)

    def get_cells(self, rows: List = None, columns: List = None, mode: str = 'all'):
        """
        Get cells from rows and columns
        :param rows:
        :param columns:
        :param mode:
                    if mode == intersection:
                        returns the cells on the intersection of all rows and columns
                    if mode == pair:
                        returns the cells based on row/column pairs, in this case, the size
                        of rows has to be equal to the size of column
                    if mode == all:
                        return all cells under this table, rows and columns will be ignored in this case
        :return: cells: CellCollection
        """
        if (rows is None or columns is None) and mode != 'all':
            raise ValueError('rows and columns cannot be None for mode != all')
        if mode == 'intersection':
            cells = [Cell(self.table, self, row, column) for row in rows for column in columns]
        elif mode == 'pair':
            if len(rows) != len(columns):
                raise ValueError("The size of rows has to equal to the size of columns when all_cells are set as False")
            cells = [Cell(self.table, self, row, column) for row, column in zip(rows, columns)]
        elif mode == 'all':
            cells = list(self.cells.values())
        else:
            raise ValueError('{} mode is not supported, please select mode between intersection, pair and all'.format(mode))
        return CellArray(self, cells, self.workspace)

    def remove_column_from_view(self, column_id: str):
        core = self.table.core
        workspace = core.workspace
        return workspace.client.remove_column_from_view(RemoveColumnFromViewInput(workspaceId=workspace.id, coreId=core.id, tableId=self.table.id, viewId=self.id, columnId=column_id)).id

    def remove_columns_from_view(self, column_ids: List[str] = None, mode="ids"):
        """
        remove columns by view
        :param column_ids:
        :param mode:
                    if mode == ids:
                        returns removed column_ids under this view by column_ids
                    if mode == all:
                        return all removed column_ids under this view
        :return: column_ids
        """
        if mode == "ids":
            return [self.remove_column_from_view(column_id) for column_id in column_ids]
        elif mode == "all":
            return [self.remove_column_from_view(column.id) for column in self.get_columns()]
        else:
            raise ValueError('{} mode is not supported, please select mode between ids,all'.format(mode))

    def remove_row_from_view(self, row_id: str):
        core = self.table.core
        workspace = core.workspace
        return workspace.client.remove_row_from_view(RemoveRowFromViewInput(workspaceId=workspace.id, coreId=core.id, tableId=self.table.id, viewId=self.id, rowId=row_id)).id

    def remove_rows_from_view(self, row_ids: List[str] = None, mode="ids"):
        """
        remove rows by view
        :param row_ids:
        :param mode:
                    if mode == ids:
                        returns removed row_ids under this view by row_ids
                    if mode == all:
                        return all removed row_ids under this view
        :return: row_ids
        """
        if mode == "ids":
            return [self.remove_row_from_view(row_id) for row_id in row_ids]
        elif mode == "all":
            return [self.remove_row_from_view(row.id) for row in self.get_rows()]
        else:
            raise ValueError('{} mode is not supported, please select mode between ids,all'.format(mode))


class Row(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, row_id: str = None, table: Table = None, view: View = None):
        """

        :param row_id:
        :param table:
        :param view:
        """
        super().__init__()
        self.view = view
        self.table = table
        self._workspace = self.table.core.workspace
        self._id = self._add_row(row_id, table)

    def _add_row(self, row_id: str, table: Table):
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            if row_id:
                return row_id
            else:
                add_row_input = AddRowInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.table.id)
                row_id = self.workspace.client.add_row(add_row_input).id
                self._id = row_id
                return row_id
        else:
            raise ValueError("You need to get/create the row from the table!")

    def update(self, vector: Union[List, pd.Series], columns: List = None):
        if not columns:
            columns = list(self.table.data.columns.values())
        if len(columns) != len(vector):
            raise ValueError("The size of column_ids must equals to the size of row!")
        self.table.get_cells([self], columns, mode='intersection').update([vector])

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event["rowId"]


class Column(_TreelabObject):
    __repr_fields__ = {'_id', '_name', 'foreign_table_id', 'field_type'}

    def __init__(self, col_id: str = None, field_name: str = '',
                 foreign_table_id: str = '',
                 table: Table = None, field_type: FieldType = FieldType.TEXT, default_number: float = 0.0,
                 precision: int = 1, options: List[List[Union[OptionInput, Any]]] = [], date_format: DateFormat = None,
                 include_time: bool = True,
                 time_format: TimeFormat = None, use_gmt: bool = True, view: View = None, default_checked: bool = True,
                 record_reference_column_id: str = '',
                 foreign_lookup_column_id: str = '', id_prefix: str = '', operation='add', foreign_core_id: str = '', foreign_workspace_id: str = '', formula: str = '', rating_max: int = 1,
                 rating_style: RatingStyleType = RatingStyleType.STAR):
        """
        :param col_id:
        :param field_name:
        :param foreign_table_id:
        :param table:
        :param field_type:
        :param default_number:
                    FieldType is NUMBER
        :param precision:
                    FieldType is NUMBER
        :param options:
                    List contains two parameters, name and color. Name is of type STR and color is of type color
                    FieldType is MULTI_SELECT or SELECT
                    example:
                        [['a',Color.lightRed],
                        ['b',Color.pink]]
        :param date_format:
                    FieldType is DATETIME
        :param include_time:
                    FieldType is DATETIME
        :param time_format:
                    FieldType is DATETIME
        :param default_checked:
                    FieldType is CHECKBOX
        :param use_gmt:
        :param record_reference_column_id:
        :param foreign_lookup_column_id:
        :param id_prefix:
        :param foreign_core_id:
        :param foreign_workspace_id:
        :operation: this contains add,update_column
        :param rating_max
        :param rating_style
        """
        super().__init__()
        self.field_type = field_type
        self.foreign_table_id = foreign_table_id
        self.default_number = default_number
        self.precision = precision
        self.options = self._get_options(options)
        self.date_format = date_format
        self.include_time = include_time
        self.time_format = time_format
        self.use_gmt = use_gmt
        self.default_checked = default_checked
        self.record_reference_column_id = record_reference_column_id
        self.foreign_lookup_column_id = foreign_lookup_column_id
        self.id_prefix = id_prefix
        self.foreign_core_id = foreign_core_id
        self._name = field_name
        self._workspace = table.core.workspace
        self.table = table
        self.view = view
        self.foreign_core_id = foreign_core_id
        self.foreign_workspace_id = foreign_workspace_id
        self.formula = formula
        self.rating_max = rating_max
        self.rating_style = rating_style
        if operation == 'add':
            self._id = self._add_column(col_id, table)
        elif operation == 'update_column':
            self._id = self._update_column(col_id, table)
        else:
            raise ValueError(f"not support this operation {operation}")
        self.view = view

    def close(self):
        """
        If the client no longer have a GRPC connection, call close to close the connection
        :return:
        """
        self.view.table.core.workspace.close()

    @staticmethod
    def _get_options(options):
        if not options:
            return []
        elif options and isinstance(options[0], OptionInput):
            return options
        elif options and isinstance(options[0], dict):
            return [OptionInput(id=option['id'], name=option['name'], color=option['color']) for option in options]
        else:
            return [OptionInput(name=option[0], color=option[1].value) for option in options]

    def _add_column(self, col_id: str, table: Table):
        if table:
            self.table = table
            self.core = self.table.core
            self._workspace = self.core.workspace
            if col_id:
                return col_id
            else:
                if self.field_type is FieldType.TEXT:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name)
                elif self.field_type is FieldType.DATETIME:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name,
                                                      dateFormat=self.date_format.value,
                                                      includeTime=self.include_time, timeFormat=self.time_format.value,
                                                      useGMT=self.use_gmt)
                elif self.field_type is FieldType.MULTI_SELECT or self.field_type is FieldType.SELECT:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, options=self.options)
                elif self.field_type is FieldType.NUMBER:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, defaultNumber=self.default_number, precision=self.precision)
                elif self.field_type is FieldType.RECORD_REFERENCE:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name,
                                                      foreignTableId=self.foreign_table_id,
                                                      foreignCoreId=self.foreign_core_id, foreignWorkspaceId=self.foreign_workspace_id)
                elif self.field_type is FieldType.CHECKBOX:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, defaultChecked=self.default_checked)
                elif self.field_type is FieldType.FORMULA:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, formula=self.formula)
                elif self.field_type is FieldType.LOOKUP:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name,
                                                      recordReferenceColumnId=self.record_reference_column_id,
                                                      foreignLookupColumnId=self.foreign_lookup_column_id)
                elif self.field_type is FieldType.ATTACHMENT:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name)
                elif self.field_type is FieldType.UNIQUE_ID:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, idPrefix=self.id_prefix)
                elif self.field_type is FieldType.RATING:
                    column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, ratingMax=self.rating_max, ratingStyle=self.rating_style.value)
                else:
                    raise ValueError('Not FieldType')

                add_col_input = AddColumnInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                               tableId=self.table.id,
                                               columnConfig=column_config)
                col_id = self.workspace.client.add_column(add_col_input).id
                self._id = col_id
                return col_id
        else:
            raise ValueError("You need to get/create the column from the table!")

    def _update_column(self, col_id: str, table: Table):
        self.table = table
        self.core = self.table.core
        if self.field_type is FieldType.TEXT:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name)
        elif self.field_type is FieldType.DATETIME:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name,
                                              dateFormat=self.date_format.value,
                                              includeTime=self.include_time, timeFormat=self.time_format.value,
                                              useGMT=self.use_gmt)
        elif self.field_type is FieldType.MULTI_SELECT or self.field_type is FieldType.SELECT:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, options=self.options)
        elif self.field_type is FieldType.NUMBER:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, defaultNumber=self.default_number, precision=self.precision)
        elif self.field_type is FieldType.RECORD_REFERENCE:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, foreignTableId=self.foreign_table_id, foreignCoreId=self.foreign_core_id, foreignWorkspaceId=self.foreign_workspace_id)
        elif self.field_type is FieldType.CHECKBOX:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, defaultChecked=self.default_checked)
        elif self.field_type is FieldType.FORMULA:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, formula=self.formula)
        elif self.field_type is FieldType.LOOKUP:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name,
                                              recordReferenceColumnId=self.record_reference_column_id,
                                              foreignLookupColumnId=self.foreign_lookup_column_id)
        elif self.field_type is FieldType.ATTACHMENT:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name)
        elif self.field_type is FieldType.UNIQUE_ID:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, idPrefix=self.id_prefix)
        elif self.field_type is FieldType.RATING:
            column_config = ColumnConfigInput(type=self.field_type.value, name=self.name, ratingMax=self.rating_max, ratingStyle=self.rating_style)
        else:
            raise ValueError('Not FieldType')
        update_column_input = UpdateColumnInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                                tableId=self.table.id, columnId=col_id,
                                                columnConfig=column_config)
        column_id = self.workspace.client.update_column(update_column_input).id
        self._id = column_id
        return column_id

    @property
    def data(self):
        return super().data

    def _get_event_id(self, event: EventPayload):
        return event["columnId"]


class Cell(_TreelabObject):
    __repr_fields__ = {'_id'}

    def __init__(self, table: Table, view: View, row: Row, column: Column, value=None, cell_id: str = None):
        """

        :param table:
        :param row:
        :param column:
        :param value:
        """
        super().__init__()
        self.table = table
        self.view = view
        self.core = self.table.core
        self._workspace = self.core.workspace
        self.row = row
        self.column = column
        self._value = value
        self.cell_id = cell_id
        self._id = '{}:{}'.format(column.id, row.id)

    def close(self):
        """
        If the cell no longer have a GRPC connection, call close to close the connection
        :return:
        """
        self.workspace.close()

    def get_value(self):
        if self._value is not None:
            return self._value
        else:
            if self.view.cells:
                data = self.view.cells.get((self.row.id, self.column.id))
                return data.value if data else None

    def update(self, value):
        """
        Update the value of the cell, the field_type can be inferred from self.row.field_type
        :param value:
                    column_type is FieldType.TEXT
        :return:
        """
        if self.column.field_type is FieldType.RECORD_REFERENCE:
            if not value:
                return
            if isinstance(value, list):
                value = [v['id'] for v in value]
            else:
                value = value.split(',')
            cell_value_input = CellValueInput(type=self.column.field_type.value, foreignRowIds=value)
            return self._update_cell(UpdateAction.ADD_VALUE, cell_value_input)
        else:
            if self.column.field_type is FieldType.MULTI_SELECT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, selectedOptionIds=value)
            elif self.column.field_type is FieldType.SELECT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, selectedOptionId=value)
            elif self.column.field_type is FieldType.TEXT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, text=value)
            elif self.column.field_type is FieldType.NUMBER:
                cell_value_input = CellValueInput(type=self.column.field_type.value, number=float(value))
            elif self.column.field_type is FieldType.DATETIME:
                cell_value_input = CellValueInput(type=self.column.field_type.value, dateTime=_datetime_to_utc(value))
            elif self.column.field_type is FieldType.CHECKBOX:
                if isinstance(value, np.str):
                    value = False if value == 'False' else True
                cell_value_input = CellValueInput(type=self.column.field_type.value, checked=value)
            elif self.column.field_type in [FieldType.LOOKUP, FieldType.UNIQUE_ID, FieldType.FORMULA]:
                return
            elif self.column.field_type is FieldType.RATING:
                cell_value_input = CellValueInput(type=self.column.field_type.value, rating=value)
            elif self.column.field_type is FieldType.ATTACHMENT:
                cell_value_input = CellValueInput(type=self.column.field_type.value, attachments=value)
            else:
                raise ValueError('Not Cell_Type')
            return self._update_cell(UpdateAction.SET_VALUE, cell_value_input)

    def _update_cell(self, action: UpdateAction, cell_value_input: CellValueInput):
        update_cell_input = UpdateCellInput(workspaceId=self.workspace.id, coreId=self.core.id,
                                            tableId=self.table.id, columnId=self.column.id,
                                            rowId=self.row.id,
                                            action=UpdateCellActionInput(type=action.value, value=cell_value_input))
        return self.workspace.client.update_cell(update_cell_input).id

    @property
    def data(self):
        return self.view.cells.get((self.row.id, self.column.id))

    @property
    def value(self):
        """
        Get the last updated value dict if there is any, this is not guaranteed to be the most updated value,
        for most updated data, using cell.data
        :return:
        """
        return self._value

    def _get_event_id(self, event: EventPayload):
        return '{}:{}'.format(event["columnId"], event["rowId"])

    def remove_cell(self):
        return self.workspace.client.remove_cell(RemoveCellInput(workspaceId=self.workspace.id, coreId=self.core.id, tableId=self.table.id, columnId=self.column.id, rowId=self.row.id, cellId=self.cell_id)).id


class _ViewDF:
    def __init__(self, rows=None, columns=None, cells=None, df=None):
        self.rows = rows
        self.columns = columns
        self.cells = cells
        self.df = df


class _TableData:
    def __init__(self, table: Table, table_dict: Dict):
        self.table = table
        self.table_dict = table_dict
        self._parse_dict(table_dict)
        self._parse_views()

    def _parse_views(self):
        """
        Initialize table data to form a DataFrame format and column name mapping
        :return:
        """
        self._view_data = {}
        for view_id, data in self._views_dict.items():
            if 'rows' in data and 'columns' in data:
                row_ids = data.get('rows').keys()
                column_ids = data.get('columns').keys()
                df_columns = [column.id + '::' + column.name + '::' + column.field_type.value for column in data.get('columns').values()]
                content = []
                for row_id in row_ids:
                    cells = data.get('cells')
                    row_data = [cells.get((row_id, column_id)).value if cells.get((row_id, column_id)) is not None else '' for column_id in column_ids]
                    content.append(row_data)
                df_data = pd.DataFrame(data=content, index=row_ids, columns=df_columns)
                view_df = _ViewDF(columns=data.get('columns'), rows=data.get('rows'), cells=data.get('cells'), df=df_data)
                self._view_data[view_id] = view_df

    def _parse_dict(self, table_dict: Dict):
        self._views_dict, self._views = {}, {}
        views = [table_dict]
        if not views:
            return
        self._columns_dict = {}
        index = 0
        for view_dict in views:
            self._rows, self._columns, self._cells = {}, {}, {}
            view_id = view_dict['id']
            view_type = view_dict['type']
            view_name = view_dict['name']
            view_options = view_dict['viewOptions']
            view = View(name=view_name, view_type=view_type, view_id=view_id, table=self.table, view_options=view_options)
            self.views[view_id] = view
            self._views_dict[view_id] = {}
            index = index + 1
            if 'columns' in view_dict:
                for column_dict in view_dict['columns']:
                    column_id = column_dict['id']
                    if index == 1:
                        self._columns_dict[column_id] = column_dict
                    column_type = FieldType(column_dict['type'])
                    column_name = column_dict['name']
                    foreign_table_id, default_number, precision, options, date_format, include_time, time_format, use_gmt, default_checked, record_reference_column_id, foreign_lookup_column_id, id_prefix, foreign_core_id, foreign_workspace_id, rating_max, rating_style = self._set_default_value()
                    if column_type in [FieldType.TEXT, FieldType.ATTACHMENT]:
                        pass
                    elif column_type is FieldType.RECORD_REFERENCE:
                        foreign_table_id = column_dict['foreignTableId']
                        foreign_core_id = column_dict.get('foreignCoreId', self.table.core.id)
                        foreign_workspace_id = column_dict.get('foreignWorkspaceId', self.table.workspace.id)
                    elif column_type is FieldType.NUMBER:
                        default_number = column_dict.get('defaultNumber')
                        precision = column_dict['precision']
                    elif column_type in [FieldType.SELECT, FieldType.MULTI_SELECT]:
                        options = column_dict['options']
                    elif column_type is FieldType.DATETIME:
                        date_format = DateFormat(column_dict['dateFormat'])
                        include_time = column_dict.get('includeTime')
                        time_format = TimeFormat(column_dict['timeFormat'])
                        use_gmt = column_dict.get('useGMT')
                    elif column_type is FieldType.CHECKBOX:
                        default_checked = column_dict.get('defaultChecked')
                    elif column_type is FieldType.LOOKUP:
                        record_reference_column_id = column_dict.get('recordReferenceColumnId')
                        foreign_lookup_column_id = column_dict.get('foreignLookupColumnId')
                    elif column_type is FieldType.UNIQUE_ID:
                        id_prefix = column_dict.get('idPrefix')
                    elif column_type is FieldType.RATING:
                        rating_max = column_dict.get("ratingMax")
                        rating_style = column_dict.get('ratingStyle')
                    else:
                        raise ValueError('Not FieldType')
                    column = Column(col_id=column_id, field_name=column_name,
                                    foreign_table_id=foreign_table_id,
                                    table=self.table, field_type=column_type, default_number=default_number,
                                    precision=precision, options=options, date_format=date_format,
                                    include_time=include_time,
                                    time_format=time_format, use_gmt=use_gmt, view=view,
                                    default_checked=default_checked,
                                    record_reference_column_id=record_reference_column_id,
                                    foreign_lookup_column_id=foreign_lookup_column_id, id_prefix=id_prefix,
                                    foreign_core_id=foreign_core_id, foreign_workspace_id=foreign_workspace_id, rating_max=rating_max, rating_style=rating_style)
                    self._columns[column_id] = column
            self._views_dict[view_id].update({'columns': self._columns})
            if 'rows' in view_dict:
                for row_dict in view_dict['rows']:
                    row_id = row_dict['id']
                    row = Row(row_id=row_id, table=self.table, view=view)
                    self._rows[row_id] = row
                    if 'cells' in row_dict:
                        if len(row_dict['cells']) < len(self._columns):
                            column_ids = self._columns.keys()
                            cell_column_ids = [cell_dict['columnId'] for cell_dict in row_dict['cells']]
                            additional_column_ids = list(set(column_ids).difference(set(cell_column_ids)))
                            for col_id in additional_column_ids:
                                cell = Cell(table=self.table, view=view, row=row, column=self._columns[col_id], value=None)
                                self._cells[row_id, col_id] = cell
                        for cell_dict in row_dict['cells']:
                            column_id = cell_dict['columnId']
                            column_type = FieldType(cell_dict.get('type'))
                            if column_type in [FieldType.SELECT, FieldType.MULTI_SELECT]:
                                value = json.loads(
                                    cell_dict.get(FieldTypeMap[column_type.value].value)) if cell_dict.get(
                                    FieldTypeMap[column_type.value].value) else []
                            elif column_type is FieldType.NUMBER:
                                value = cell_dict.get(FieldTypeMap[column_type.value].value, 0.0)
                            elif column_type is FieldType.CHECKBOX:
                                value = cell_dict.get(FieldTypeMap[column_type.value].value, False)
                            else:
                                value = cell_dict.get(FieldTypeMap[column_type.value].value)
                            if not self._columns.get(column_id):
                                continue
                            cell = Cell(table=self.table, view=view, row=row, column=self._columns[column_id], value=value)
                            self._cells[row_id, column_id] = cell
            self._views_dict[view_id].update({'rows': self._rows, 'cells': self._cells})
        first_view_id = list(self._views.keys())
        if len(first_view_id) > 0:
            first_view = self._views_dict.get(first_view_id[0])
            self._rows = first_view.get('rows') if 'rows' in first_view else {}
            self._columns = first_view.get('columns') if 'columns' in first_view else {}
            self._cells = first_view.get('cells') if 'cells' in first_view else {}
        else:
            self._rows = {}
            self._columns = {}
            self._cells = {}

    @staticmethod
    def _set_default_value():
        foreign_table_id = ''
        default_number = 0.0
        precision = 1
        options = []
        date_format = None
        include_time = True
        time_format = None
        use_gmt = True
        default_checked = True
        record_reference_column_id = ''
        foreign_lookup_column_id = ''
        id_prefix = ''
        foreign_core_id = ''
        foreign_workspace_id = ''
        rating_max = 1
        rating_style = RatingStyleType.STAR
        return foreign_table_id, default_number, precision, options, date_format, include_time, time_format, use_gmt, default_checked, record_reference_column_id, foreign_lookup_column_id, id_prefix, foreign_core_id, foreign_workspace_id, rating_max, rating_style

    @property
    def cells(self) -> Dict:
        return self._cells

    @property
    def rows(self) -> Dict:
        return self._rows

    @property
    def views(self) -> Dict:
        return self._views

    @property
    def columns(self) -> Dict:
        return self._columns

    @property
    def view_data(self) -> Dict:
        return self._view_data

    @property
    def views_dict(self) -> Dict:
        return self._views_dict

    @property
    def columns_dict(self) -> Dict:
        return self._columns_dict


class _TreelabObjectArray(Listenable, Generic[GenericType.PT, GenericType.T]):
    def __init__(self, parent_object: GenericType.PT, objects: List[GenericType.T], workspace):
        super().__init__(workspace)
        self._objects = objects
        self.parent_object = parent_object
        self._size = len(objects)

    def __iter__(self) -> Iterator[GenericType.T]:
        return self._objects.__iter__()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.parent_object, self._objects[item], self.workspace)
        else:
            if self.size == 0:
                raise ValueError('Cannot indexing an empty _TreelabObjectArray')
            return self._objects[item]

    def __contains__(self, obj: GenericType.T) -> bool:
        return obj in self._objects

    def __len__(self) -> int:
        return len(self._objects)

    @property
    def size(self):
        return self._size

    def select(self, filter_func: Callable[[GenericType.T], bool], max_size: int = None):
        """
        Select the objects that meet conditions specified by filter_func
        :param filter_func:
        :param max_size:
        :return:
        """
        selected_objs: List[GenericType.T] = list(filter(filter_func, self._objects))
        if max_size:
            selected_objs = selected_objs[:max_size]
        return _TreelabObjectArray(self.parent_object, selected_objs, self.workspace)

    def select_by_name(self, name):
        return self.select(filter_func=lambda obj: obj.name == name)

    def sort(self, sort_function: Callable[[GenericType.T], bool], max_size: int = None):
        """
        Sort the objects by sort_function
        :param sort_function:
        :param max_size:
        :return:
        """
        sorted_objs: List[GenericType.T] = sorted(self._objects, key=sort_function)[:max_size]
        if max_size:
            sorted_objs = sorted_objs[:max_size]
        return _TreelabObjectArray(self.parent_object, sorted_objs, self.workspace)

    def listen_to(self, listener: Union[Callable[[EventPayload], Any], Listener], name: str = None, thread_num: int = 0, user_only: bool = True):
        """
        Register the listener to every single object in the collection
        :param listener:
        :param name:
        :param thread_num:
        :param user_only:
        :return:
        """
        for i, obj in enumerate(self._objects):
            obj.listen_to(listener, '{}_{}'.format(name, i), thread_num, user_only)

    def __repr__(self):
        return self._objects.__repr__()


class CellArray(_TreelabObjectArray[Table, Cell]):
    def __init__(self, parent_object: GenericType.PT, objects: List[GenericType.T], workspace: Workspace):
        super().__init__(parent_object, objects, workspace)
        self._shape = (self.size, 1)

    @property
    def shape(self):
        return self._shape

    @property
    def matrix(self) -> np.array:
        """
        Get the text matrix representation of the cells
        :return:
        """
        return self._objects

    def update_all(self, value: str):
        """
        Update all the cells with the same value
        :param value:
        :return:
        """
        for obj in self._objects:
            obj.update(value=value)

    def reshape(self, shape: Tuple[int, int]):
        """
        Reshaping cells to certain shape as long as the size matches the product of width and length of the shape
        :param shape:
        :return:
        """
        m, n = shape
        if m * n != self.size:
            raise ValueError('The product of width and length of the shape must equals to the size of cells')
        self._shape = shape

        return self

    def flatten(self):
        """
        Flattening the cells into vector
        :return:
        """
        self._shape = (self.size, 1)
        return self

    def update(self, data_matrix: Union[List[List], np.array, pd.DataFrame], reshape: bool = True):
        """
        Update the cells with data_matrix, use reshape when you want to fit the matrix into the cells
        The shape of cell_type_matrix and data_matrix must be consistent and used to verify the cell field type
        :param data_matrix:
        :param reshape:
        :return:
        """
        data_matrix = self._convert_to_matrix(data_matrix)
        n_rows, n_cols = data_matrix.shape
        if reshape:
            self.reshape(data_matrix.shape)
        for i in range(n_rows):
            for j in range(n_cols):
                data = data_matrix.ix[i, j] if isinstance(data_matrix, pd.DataFrame) else data_matrix[i, j]
                if data != '':
                    cell_id = self._objects[i * n_cols + j].update(value=data)
                    self._objects[i * n_cols + j].cell_id = cell_id

    @staticmethod
    def _convert_to_matrix(data):
        if isinstance(data, List):
            if len(data) == 0:
                raise ValueError('The size of the data matrix must not be zero')
            data = np.array(data)
        return data

    def values_dict(self) -> Dict:
        return {obj.id: obj.value for obj in self._objects}

    def __repr__(self):
        return self.matrix.__repr__()


class CoreArray(_TreelabObjectArray[Workspace, Core]):
    pass


class TableArray(_TreelabObjectArray[Core, Table]):
    pass


class RowArray(_TreelabObjectArray[Table, Row]):
    pass


class ColumnArray(_TreelabObjectArray[Table, Column]):
    pass


class ViewArray(_TreelabObjectArray[Table, View]):
    pass


@contextmanager
def subscribe_under(workspace: Workspace, wait_time: int = 0):
    try:
        yield
    finally:
        workspace.event_handler._subscribe_all()
        print('All listeners subscribed')
        threading.Event().wait(wait_time)
        # workspace.dispose()


def subscribe(workspaces: List[Workspace], wait_time: int = 0):
    """
    Wrapper for subscribing multiple workspaces
    """

    def decorator(subscription_func):
        @wraps(subscription_func)
        def wrapper():
            for workspace in workspaces:
                subscription_func(workspace)
                workspace.event_handler._subscribe_all()
            threading.Event().wait(wait_time)
            # Disposing all workspaces
            # for workspace in workspaces:
            #     workspace.dispose()

        return wrapper

    return decorator


def get_option(options: List[List]):
    """
    Set the options for column
    :param options:
                for example :
                get_option([['a', SelectColor.blue], ['b', SelectColor.green], ['c', SelectColor.pink]])
    :return:
    """
    if not options:
        return []
    return [OptionInput(name=option[0], color=option[1].value) for option in options]


def get_options_by_names(options: List[OptionInput], names: List[str]):
    return [option for option in options if option.name in names]


def get_option_by_name(options: List[OptionInput], name: str):
    return [option for option in options if option.name == name]


def _datetime_to_utc(date: str):
    """
    convert time to utc
    :param date :
                for example :
                    yyyy-mm-dd = '%Y-%m-%d' 2019-12-25
                    yyyy-mm-dd hh-mm-ss = '%Y-%m-%d %H:%M:%S' 2019-06-05 10:19:02
                    dd-mm-yyyy = '%d-%m-%Y' 25-12-2019
                    dd-mm-yyyy hh-mm-ss = '%d-%m-%Y %H:%M:%S' 25-12-2019 10:19:02
                    mm-dd-yyyy = '%m-%d-%Y' 12-25-2019
                    mm-dd-yyyy hh-mm-ss = '%m-%d-%Y %H:%M:%S' 12-25-2019 10:19:02
    :return:
    """
    if date.find('T') > -1:
        return date

    new_date = date.replace('_', '-').replace('.', '-').replace('/', '-')
    result = _utc(new_date)
    if result:
        return result
    else:
        raise ValueError('Unsupported date format', date)


def _utc(new_date):
    for date_pattern in DatePattern:
        flag = re.match(date_pattern.value, new_date)
        if flag:
            new_date = datetime.strptime(new_date, DateFormatter[date_pattern.name].value)
            utc_time = new_date - timedelta(hours=8)
            utc_time = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            return utc_time
    return None
