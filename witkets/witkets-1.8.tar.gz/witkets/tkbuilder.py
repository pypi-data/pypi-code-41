#!/usr/bin/env python3

import sys
import ast
import xml.etree.ElementTree as ElementTree
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from copy import copy
import witkets as wtk
from witkets.core import wtk_types
from witkets.core.attribspec import attribspec
import witkets.plot as plt

# =========================================================================
# Module Symbols
# =========================================================================

_widget_classes = [
    # TK Base and TTK Overriden Widgets
    ttk.Button, tk.Canvas, ttk.Checkbutton, ttk.Entry, ttk.Frame, ttk.Label,
    ttk.LabelFrame, tk.Listbox, tk.Menu, tk.Message, ttk.Menubutton,
    ttk.PanedWindow, ttk.Radiobutton, ttk.Scale, ttk.Scrollbar,
    tk.scrolledtext.ScrolledText, tk.Spinbox, tk.Text,
    # TTK Exclusive
    ttk.Combobox, ttk.Notebook, ttk.Progressbar, ttk.Separator, ttk.Sizegrip,
    ttk.Treeview,
    # Witkets
    wtk.AccelLabel, wtk.CardLayout, wtk.ColorButton, wtk.ConsoleView, 
    wtk.Expander, wtk.FileChooserEntry, wtk.Gauge, wtk.ImageButton, 
    wtk.ImageMap, wtk.LED, wtk.LEDBar, wtk.LinkButton, wtk.LogicSwitch, 
    wtk.NumericLabel, plt.Plot, plt.Scope, wtk.PyText, wtk.PyScrolledText, 
    wtk.Ribbon, wtk.Spinner, wtk.Spin, wtk.Tank, wtk.ThemedLabelFrame,
    wtk.Thermometer, wtk.TimeEntry, wtk.Toolbar, wtk.ToggleButton
]

_geometry_tags = ('pack', 'grid', 'place', 'card', 'tab', 'pane')

_constructor_properties = {
    ttk.PanedWindow: ['orient']
}

# =========================================================================
# Builder
# =========================================================================

class TkBuilder:
    def __init__(self, master):
        """Initializer
        
            :param master:
                Tk root container where interface is going to be built
        """
        self._tree = None
        self._root = None
        self._master = master
        self.nodes = {}
        self.vars = {}
        self.tkstyle = None
        self.theme = None
        self._tag2tk = {cls.__name__.lower(): cls for cls in _widget_classes}
        self._special_attribs = {}
        self._containers = ['root', 'frame', 'labelframe', 'expander',
                            'themedlabelframe', 'cardlayout', 'notebook',
                            'panedwindow'
                            ]
        self.add_tag('tkbutton', tk.Button)
        self.add_tag('tkpanedwindow', tk.PanedWindow, container=True)

    # =========================================================================
    # Widget Tags
    # =========================================================================

    def _handle_widget(self, widget_node, parent):
        """Handles individual widgets tags."""
        try:
            wid = widget_node.attrib.pop('wid')
        except KeyError:
            print('Required key "wid" not found in %s' % widget_node.tag, 
                  file=sys.stderr)
            return
        # Creating widget        
        tk_class = self._tag2tk[widget_node.tag]
        if parent == self._root:
            parent_widget = self._master
        else:
            parent_id = parent.attrib['wid']
            parent_widget = self.nodes[parent_id]
        # Expander container
        if parent.tag == 'expander':
            parent_widget = parent_widget.frame
        self.nodes[wid] = tk_class(parent_widget)
        # Mapping attributes
        kwargs = self._get_attributes_dict(self.nodes[wid], widget_node.tag,
                                           widget_node.attrib)
        self.nodes[wid].config(**kwargs)
        for child in widget_node:
            self._handle_widget_child_tag(self.nodes[wid], child)

    def _handle_widget_child_tag(self, widget, child_node):
        """Handles special widget config tags"""
        key = child_node.tag.replace('wtk-', '')
        if key in ('variable', 'textvariable'):
            if 'name' not in child_node.attrib or \
               'type' not in child_node.attrib:
               raise ValueError('Name and type are required for variables!')
            # FIXME validate type in (int, double, text)
            name = child_node.attrib['name']
            type_ = child_node.attrib['type']
            defval = None
            if 'value' in child_node.attrib:
                defval = child_node.attrib['value']
            if type_ == 'int':
                var = tk.IntVar(value=defval)
            elif type_ == 'double':
                var = tk.DoubleVar(value=defval)
            elif type_ == 'text':
                var = tk.StringVar(value=defval)
            self.vars[name] = var
            widget[key] = var

    # =========================================================================
    # Attributes
    # =========================================================================

    def _get_attributes_dict(self, widget, tagname, attribs):
        """Handles attributes, except TkBuilder related"""
        # Removing editor-specific attributes
        attribs = {key : attribs[key] for key in attribs \
                                      if not key.startswith('wtk-editor-')}
        attribs = self._get_attribs_values(widget, tagname, attribs)
        return attribs

    def _get_attribs_values(self, widget, tagname, attribs):
        widcls = widget.__class__
        handlers = {}
        # For geometry tags like <pack> and <grid>
        if tagname in attribspec:
            handlers = attribspec[tagname]
        # For Tk and Ttk widgets
        elif widcls in attribspec:
            handlers = attribspec[widcls]
        # Retrieving attributes values
        typed_attribs = {}
        for key in attribs: # this is complex, at least for now...
            if (tagname, key) in self._special_attribs:
                self._special_attribs[(tagname, key)](widget, key, attribs[key])
            # Tk and Ttk Handlers
            elif key in handlers:
                typed_attribs[key] = TkBuilder._parse_or_construct(
                    handlers[key],
                    attribs[key]
                )
            # Witkets keys
            elif hasattr(widcls, 'widget_keys') and key in widcls.widget_keys:
                typed_attribs[key] = TkBuilder._parse_or_construct(
                    widcls.widget_keys[key], attribs[key]
                )
            # Enumerations
            elif key in dir(wtk_types):
                enum = getattr(wtk_types, key)
                try:
                    typed_attribs[key] = enum(attribs[key]).value
                except ValueError as ex:
                    params = (widget, tagname, key, ex)
                    print('[warning] [%s, %s, %s] %s' % params, file=sys.stderr)
                    continue
            # Generic keys
            else:
                typed_attribs[key] = attribs[key]
        return typed_attribs

    @staticmethod
    def _parse_or_construct(obj, value):
        # Duck typing (presuming a parse staticmethod is defined)...
        try:
            return obj.parse(value)
        # If not, it's just a simple type, like int
        except:
            return obj(value)


    # =========================================================================
    # Containers and Geometry
    # =========================================================================

    def _handle_container(self, container, parent):
        """Handles containers (<root>, <frame> and user-defined containers)"""
        attribs = copy(container.attrib)
        if container.tag != 'root':
            if container.tag not in self._tag2tk:
                print('Tag not supported: %s' % container.tag, file=sys.stderr)
                return
            if 'wid' not in attribs:
                print('Required key "wid" not found in %s' % container.tag,
                      file=sys.stderr)
                return
            wid = attribs.pop('wid')
            tk_class = self._tag2tk[container.tag]
            if parent != self._root:
                parent_id = parent.attrib['wid']
                parent_widget = self.nodes[parent_id]
            else:
                parent_widget = self._master
            # Popping constructor-only properties
            kwargs = {}
            if tk_class in _constructor_properties:
                for p in _constructor_properties[tk_class]:
                    if p in attribs:
                        kwargs[p] = attribs[p]
                        attribs.pop(p)
            self.nodes[wid] = tk_class(parent_widget, **kwargs)
            kwargs = self._get_attributes_dict(self.nodes[wid], container.tag, 
                attribs)
            self.nodes[wid].config(**kwargs)
            container_widget = self.nodes[wid]
        else:
            attribs = container.attrib
            kwargs = self._get_attributes_dict(self._master, 'root', attribs)
            self._master.config(**kwargs)
            container_widget = self._master
        # Container children
        for child in container:
            if child.tag in self._containers:
                self._handle_container(child, container)
            elif child.tag == 'geometry':
                self._handle_geometry(child)
            elif child.tag == 'style':
                self._handle_stylesheet(child)
            elif child.tag == 'grid-configure':
                self._handle_grid_configure(container_widget, child)
            elif child.tag in self._tag2tk.keys():
                self._handle_widget(child, container)
            else:
                print('Invalid tag: %s!' % child.tag, sys.stderr)

    def _handle_geometry(self, geometry):
        """Handle the special <geometry> tag"""
        for child in geometry:
            if child.tag not in _geometry_tags:
                print('Invalid geometry instruction %s' % child.tag, 
                      file=sys.stderr)
                continue
            attribs = copy(child.attrib)
            # Getting widget ID
            try:
                wid = attribs.pop('for')
            except KeyError:
                print('[geom] Required key "for" not found in %s' % child.tag,
                      file=sys.stderr)
                continue
            # Calling appropriate geometry method
            attribs = self._get_attribs_values(self.nodes[wid], child.tag, attribs)
            if child.tag == 'pack':
                self.nodes[wid].pack(**attribs)
            elif child.tag == 'grid':
                self.nodes[wid].grid(**attribs)
            elif child.tag == 'place':
                self.nodes[wid].place(**attribs)
            elif child.tag == 'card':
                name = attribs['name'] if 'name' in attribs else None 
                self.nodes[wid].master.add(self.nodes[wid], name=name)
            elif child.tag in ('tab', 'pane'):
                self.nodes[wid].master.add(self.nodes[wid], **attribs)

    def _handle_grid_configure(self, parent_widget, child):
        """Handle grid configure commands.
            @FIXME: Need to be tested both in root and child frame 
        """
        for config_item in child:
            index = config_item.attrib.pop('index')
            if config_item.tag == 'row':
                parent_widget.grid_rowconfigure(int(index), **config_item.attrib)
            elif config_item.tag == 'column':
                parent_widget.grid_columnconfigure(int(index), **config_item.attrib)

    # =========================================================================
    # Styling
    # =========================================================================

    def _handle_stylesheet(self, style):
        """Handle the special <style> tag"""
        self.tkstyle = wtk.Style()
        if 'defaultfonts' in style.attrib and \
                style.attrib['defaultfonts'] != '0':
            wtk.Style.set_default_fonts()
        if 'applydefault' in style.attrib and \
                style.attrib['applydefault'] != '0':
            self.tkstyle.apply_default()
        if 'fromfile' in style.attrib:
            self.tkstyle.apply_from_file(style.attrib['fromfile'])
        else:
            self.tkstyle.apply_from_string(style.text)

    # =========================================================================
    # Visitor Entry Point
    # =========================================================================

    def _parse_tree(self):
        """Parse XML and build interface."""
        if self._root.tag != 'root':
            msg = 'Invalid root tag! Expecting "root", but found %s'
            print(msg % self._root.tag, file=sys.stderr)
            return False
        self._handle_container(self._root, self._master)
        return True

    # =========================================================================
    # Public API
    # =========================================================================

    def add_tag(self, tag: str, cls, container=False):
        """Maps a tag to a class.
        
            :param tag:
                XML tag name
            :type tag:
                str
            :param cls:
                Class to be instantiated when *tag* is found
            :type cls:
                Any widget class
            :param container:
                Whether this Tk widget is a container of other widgets
        """
        self._tag2tk[tag] = cls
        if container:
            self._containers.append(tag)

    def set_custom_attribute(self, tag: str, attribute: str, handler):
        """Set a handler for a custom (user-defined) attribute.

            :param tag:
                XML tag name.
            :type tag:
                str
            :param attribute:
                XML attribute name.
            :type attribute:
                str
            :param handler:
                Handler function with signature f(widget, key, strval).
        """
        self._special_attribs[(tag, attribute)] = handler

    def build_from_file(self, filepath):
        """Build user interface from XML file."""
        self._tree = ElementTree.parse(filepath)
        self._root = self._tree.getroot()
        self._parse_tree()

    def build_from_string(self, contents):
        """Build user interface from XML string"""
        self._root = ElementTree.fromstring(contents)
        self._parse_tree()


if __name__ == '__main__':
    import doctest
    doctest.testmod()