import treelab.grpc_treelab.messages.service_pb2_grpc as treelab_service
from treelab.consts import get_env_ip
from treelab.grpc_treelab.messages.service_pb2 import *
from treelab.utils.decorator_utils import *
import grpc
import os

"""
Interfacing Treelab gRPC APIs
"""


class TreeLabClient:
    def __init__(self, token: str):
        self.metadata = [('access_token', token)]
        if not os.getenv('ip'):
            os.environ['ip'] = get_env_ip()
        self.channel = grpc.insecure_channel(os.getenv('ip'))
        self.client = treelab_service.TreeLabApiServiceStub(self.channel)

    def close(self):
        self.channel.close()

    def create_workspace(self, create_workspace_input: CreateWorkspaceInput):
        return self.client.CreateWorkspace(create_workspace_input, metadata=self.metadata)

    def update_workspace(self, update_workspace_input: UpdateWorkspaceInput):
        return self.client.UpdateWorkspace(update_workspace_input, metadata=self.metadata)

    def add_core(self, add_core_input):
        return self.client.AddCore(add_core_input, metadata=self.metadata)

    def remove_core(self, remove_core_input: RemoveCoreInput):
        return self.client.RemoveCore(remove_core_input, metadata=self.metadata)

    def update_core(self, update_core_input: UpdateCoreInput):
        return self.client.UpdateCore(update_core_input, metadata=self.metadata)

    def update_core_order(self, reorder_core_input: ReorderCoreInput):
        return self.client.ReorderCore(reorder_core_input, metadata=self.metadata)

    def add_table(self, add_table_input: AddTableInput):
        return self.client.AddTable(add_table_input, metadata=self.metadata)

    def update_table_name(self, update_table_name_input: UpdateTableNameInput):
        return self.client.UpdateTableName(update_table_name_input, metadata=self.metadata)

    def update_table_order(self, reorder_table_input: ReorderTableInput):
        return self.client.ReorderTable(reorder_table_input, metadata=self.metadata)

    def remove_table(self, remove_table_input: RemoveTableInput):
        return self.client.RemoveTable(remove_table_input, metadata=self.metadata)

    def add_view(self, add_view_input: AddViewInput):
        return self.client.AddView(add_view_input, metadata=self.metadata)

    def update_view(self, update_view_input: UpdateViewInput):
        return self.client.UpdateView(update_view_input, metadata=self.metadata)

    def update_view_order(self, reorder_view_input: ReorderViewInput):
        return self.client.ReorderView(reorder_view_input, metadata=self.metadata)

    def remove_view(self, remove_view_input: RemoveViewInput):
        return self.client.RemoveView(remove_view_input, metadata=self.metadata)

    def add_column(self, add_column_input: AddColumnInput):
        return self.client.AddColumn(add_column_input, metadata=self.metadata)

    def update_column(self, update_column_input: UpdateColumnInput):
        return self.client.UpdateColumn(update_column_input, metadata=self.metadata)

    def update_column_width(self, update_column_width_input: UpdateColumnWidthInput):
        return self.client.UpdateColumnWidth(update_column_width_input, metadata=self.metadata)

    def update_column_order(self, reorder_column_input: ReorderColumnInput):
        return self.client.ReorderColumn(reorder_column_input, metadata=self.metadata)

    def remove_column(self, remove_column_input: RemoveColumnInput):
        return self.client.RemoveColumn(remove_column_input, metadata=self.metadata)

    def remove_column_from_view(self, remove_column_from_view_input: RemoveColumnFromViewInput):
        return self.client.RemoveColumn(remove_column_from_view_input, metadata=self.metadata)

    def add_row(self, add_row_input: AddRowInput):
        return self.client.AddRow(add_row_input, metadata=self.metadata)

    def update_row_order(self, reorder_row_input: ReorderRowInput):
        return self.client.ReorderRow(reorder_row_input, metadata=self.metadata)

    def remove_row(self, remove_row_input: RemoveRowInput):
        return self.client.RemoveRow(remove_row_input, metadata=self.metadata)

    def remove_row_from_view(self, remove_row_from_view_input: RemoveRowFromViewInput):
        return self.client.RemoveRowFromView(remove_row_from_view_input, metadata=self.metadata)

    def update_cell(self, update_cell_input: UpdateCellInput):
        return self.client.UpdateCell(update_cell_input, metadata=self.metadata)

    def remove_cell(self, remove_cell_input: RemoveCellInput):
        return self.client.RemoveCell(remove_cell_input)

    def get_all_workspaces(self):
        return self.client.GetAllWorkspaces(EmptyInput(), metadata=self.metadata)

    def subscribe_to_user(self):
        return self.client.SubscribeToUser(EmptyInput(), metadata=self.metadata)

    def get_workspace(self, get_workspace_input: GetWorkspaceInput):
        return self.client.GetWorkspace(get_workspace_input, metadata=self.metadata)

    def get_table(self, get_table_input: GetTableInput):
        return self.client.GetTable(get_table_input, metadata=self.metadata)

    def get_view(self, get_view_input: GetViewInput):
        return self.client.GetView(get_view_input, metadata=self.metadata)

    def get_all_views(self, get_views_input: GetViewsInput):
        return self.client.GetAllViews(get_views_input, metadata=self.metadata)

    def get_all_tables(self, get_tables_input: GetTablesInput):
        return self.client.GetAllTables(get_tables_input, metadata=self.metadata)

    def get_core(self, get_core_input: GetCoreInput):
        return self.client.GetCore(get_core_input, metadata=self.metadata)

    def get_all_cores(self, get_cores_input: GetCoresInput):
        return self.client.GetAllCores(get_cores_input, metadata=self.metadata)

    def get_cell_by_column_and_row_id(self, get_cell_by_column_and_row_id_input: GetCellByColumnAndRowIdInput):
        return self.client.GetCellByColumnAndRowId(get_cell_by_column_and_row_id_input, metadata=self.metadata)

    def get_lookup_cell(self, get_lookup_cell_by_column_and_row_id_input:
    GetLookupCellByColumnAndRowIdInput):
        return self.client.GetLookupCellByColumnAndRowId(get_lookup_cell_by_column_and_row_id_input,
                                                         metadata=self.metadata)
