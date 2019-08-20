import nanome
from nanome.api.ui import LayoutNode
from nanome.util import Logs
from nanome.util.enums import NotificationTypes
from nanome._internal._network._serialization import _ContextSerialization, _ContextDeserialization
from nanome._internal._structure._serialization import _WorkspaceSerializer, _AtomSerializer
from nanome._internal._util._serializers import _DictionarySerializer, _StringSerializer, _ByteSerializer, _TypeSerializer, _LongSerializer

import struct
import os
import zlib
import traceback
from timeit import default_timer as timer

# This plugin uses undocumented network code, in order to reuse already available serialization code

workspace_dir = os.path.join(os.path.dirname(__file__), 'Workspaces')
if not os.path.exists(workspace_dir):
    os.makedirs(workspace_dir)

workspace_serializer = _WorkspaceSerializer()
dictionary_serializer = _DictionarySerializer()
dictionary_serializer.set_types(_StringSerializer(), _ByteSerializer())
atom_dictionary_serializer = _DictionarySerializer()
atom_dictionary_serializer.set_types(_LongSerializer(), _AtomSerializer())

class WorkspaceManager(nanome.PluginInstance):

    ###################################
    ### Save + Load Logic
    ###################################

    def open_file_for_save(self, name):
        file_path = os.path.join(workspace_dir, name)
        if os.path.exists(file_path):
            self.send_notification(NotificationTypes.error, "Workspace name already exists")
            self.save.unusable = False
            self.update_content(self.save)
            return

        file = open(file_path, "wb")
        def workspace_received(workspace):
            try:
                self.save_workspace(workspace, file)
            except:
                self.send_notification(NotificationTypes.error, "Failed to save workspace, check plugin")
                Logs.error("Failed to save workspace", traceback.format_exc())
            self.save.unusable = False
            self.update_content(self.save)
            file.close()
            self.refresh_menu()
            self.__timer = timer()

        self.request_workspace(workspace_received)

    def save_workspace(self, workspace, file):
        context = _ContextSerialization(0, _TypeSerializer.get_version_table())
        context.write_uint(0) # Version
        context.write_using_serializer(dictionary_serializer, _TypeSerializer.get_version_table())
        subcontext = context.create_sub_context()
        subcontext.payload["Atom"] = {}
        subcontext.write_using_serializer(workspace_serializer, workspace)
        context.write_using_serializer(atom_dictionary_serializer, subcontext.payload["Atom"])
        context.write_bytes(subcontext.to_array())

        to_write = context.to_array()
        compressed_data = zlib.compress(to_write)
        file.write(compressed_data)

    def open_file_for_load(self, name):
        file_path = os.path.join(workspace_dir, name)
        try:
            file = open(file_path, "rb")
        except:
            self.send_notification(NotificationTypes.error, "Couldn't open workspace")
            return

        data = file.read()
        file.close()
        try:
            decompressed_data = zlib.decompress(data)
            self.load_workspace(decompressed_data)
        except:
            self.send_notification(NotificationTypes.error, "Failed to load workspace, check plugin")
            Logs.error("Failed to load workspace", traceback.format_exc())

    def load_workspace(self, data):
        context = _ContextDeserialization(data, _TypeSerializer.get_version_table())
        context.read_uint()
        file_version_table = context.read_using_serializer(dictionary_serializer)
        version_table = _TypeSerializer.get_best_version_table(file_version_table)

        context = _ContextDeserialization(data, version_table)
        context.read_uint()
        context.read_using_serializer(dictionary_serializer)
        context.payload["Atom"] = context.read_using_serializer(atom_dictionary_serializer)
        workspace = context.read_using_serializer(workspace_serializer)

        self.update_workspace(workspace)

    ###################################
    ### UI
    ###################################

    def create_menu(self):
        menu = self.menu
        menu.title = "Workspace Manager"
        menu._width = 0.8
        menu._height = 0.7
        menu.enabled = True

        ln_list = menu.root.create_child_node()
        ln_footer = menu.root.create_child_node()
        ln_name = ln_footer.create_child_node()
        ln_save = ln_footer.create_child_node()

        ln_list.forward_dist = 0.01
        ln_list.sizing_type = LayoutNode.SizingTypes.ratio
        ln_footer.sizing_type = LayoutNode.SizingTypes.ratio
        ln_list.sizing_value = 0.85
        ln_footer.sizing_value = 0.15
        ln_footer.layout_orientation = LayoutNode.LayoutTypes.horizontal
        ln_name.forward_dist = 0.01
        ln_name.sizing_type = LayoutNode.SizingTypes.ratio
        ln_save.sizing_type = LayoutNode.SizingTypes.ratio
        ln_name.sizing_value = 0.7
        ln_save.sizing_value = 0.3

        self.list = ln_list.add_new_list()
        self.field = ln_name.add_new_text_input()
        self.field.placeholder_text = "Workspace name"
        self.save = ln_save.add_new_button(text="Save")
        self.save.register_pressed_callback(self.save_pressed_callback)

        item = LayoutNode()
        ln_label = item.create_child_node(name="file_name")
        ln_load = item.create_child_node(name="file_load")
        ln_delete = item.create_child_node(name="file_delete")
        label = ln_label.add_new_label()
        load = ln_load.add_new_button(text="Load")
        delete = ln_delete.add_new_button(text="Delete")
        item.layout_orientation = LayoutNode.LayoutTypes.horizontal
        ln_label.sizing_type = LayoutNode.SizingTypes.ratio
        ln_load.sizing_type = LayoutNode.SizingTypes.ratio
        ln_delete.sizing_type = LayoutNode.SizingTypes.ratio
        ln_label.sizing_value = 0.6
        ln_load.sizing_value = 0.2
        ln_delete.sizing_value = 0.2
        self.item = item

        self.update_menu(menu)

    def refresh_menu(self):
        files = [filename for filename in os.listdir(workspace_dir)]
        file_names = set(map(lambda item: item.name, self.list.items))
        add_set = set(files)
        remove_files = file_names - add_set
        changed = False

        for file_name in remove_files:
            item_to_delete = None
            for item in self.list.items:
                if item.name == file_name:
                    item_to_delete = item
                    break
            if item_to_delete != None:
                self.list.items.remove(item_to_delete)
            changed = True

        add_files = add_set - file_names
        for file_name in add_files:
            new_item = self.item.clone()
            new_item.name = file_name
            label = new_item.find_node("file_name").get_content()
            load = new_item.find_node("file_load").get_content()
            delete = new_item.find_node("file_delete").get_content()
            label.text_value = file_name
            changed = True

            load.workspace = file_name
            delete.workspace = file_name
            load.register_pressed_callback(self.load_pressed_callback)
            delete.register_pressed_callback(self.delete_pressed_callback)

            self.list.items.append(new_item)

        if changed:
            self.update_content(self.list)

    def display_menu(self):
        self.menu.enabled = True
        self.update_menu(self.menu)

    ###################################
    ### Base Logic
    ###################################

    def start(self):
        self.create_menu()
        self.refresh_menu()
        self.__timer = timer()

    def on_run(self):
        self.display_menu()

    def update(self):
        if timer() - self.__timer >= 5.0:
            self.refresh_menu()
            self.__timer = timer()

    def save_pressed_callback(self, button):
        name = self.field.input_text.strip()
        if name == '':
            self.send_notification(NotificationTypes.error, "Workspace name cannot be empty")
            return
        self.save.unusable = True
        self.update_content(self.save)
        self.open_file_for_save(name)

    def load_pressed_callback(self, button):
        self.open_file_for_load(button.workspace)

    def delete_pressed_callback(self, button):
        try:
            os.remove(os.path.join(workspace_dir, button.workspace))
        except:
            pass
        self.refresh_menu()
        self.__timer = timer()

def main():
    # Plugin
    plugin = nanome.Plugin("Workspace Manager", "Allows standalone VR headset to save and load workspaces", "Loading", False)
    plugin.set_plugin_class(WorkspaceManager)
    plugin.run('127.0.0.1', 8888)

if __name__ == "__main__":
    main()
