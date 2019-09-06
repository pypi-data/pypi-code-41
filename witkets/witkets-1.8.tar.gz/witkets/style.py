"""Provide ttk Styling by parsing INI files

This module contains the `Style` class, which overrides `ttk.Style` adding the feature of
changing widget styles according to INI-based stylesheets.

Example:
    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> from witkets import Style
    >>> root = tk.Tk()
    >>> ttk.Button(root, text='normal').pack(side=tk.LEFT, padx=10, pady=10)
    >>> b = ttk.Button(root, text='BIG One!')
    >>> b['style'] = 'BigButton.TButton'
    >>> b.pack(side=tk.RIGHT, padx=10, pady=10)
    >>> style = Style()
    >>> style.theme_use('clam')
    >>> style.set_default_fonts()
    >>> style.apply_default()  # applying default theme first
    >>> style.apply_from_string('''
    ... [BigButton.TButton]
    ... font=Helvetica 36 bold
    ... borderwidth=0
    ... relief=flat''')
    >>> root.mainloop()

"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
import configparser
import pkgutil


class Style(ttk.Style):
    """Look-and-feel management

    :param master:
        Master widget related to this `ttk` Style object or None for root
    """

    def __init__(self, master=None):
        ttk.Style.__init__(self, master)
        self._config = configparser.ConfigParser()
        self._properties = []

    @staticmethod
    def set_default_fonts():
        """Set Tk fonts to `witkets` default (Helvetica 11)"""
        default_font = tk.font.nametofont("TkDefaultFont")
        default_font.configure(size=11, family="Helvetica")
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=11, family="Helvetica")
        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(size=11, family="Helvetica")

    def _apply(self):
        """Apply styles as described by this Theme."""
        for s in self._config.sections():
            normal_values = {}
            composed_values = {}
            for key in self._config[s]:
                # Composed value
                if '.' in key:
                    parts = key.split('.')
                    # Dictionary: {'foreground': [], 'background': [], ...}
                    base_key = parts[0]
                    if base_key not in composed_values:
                        composed_values[base_key] = []
                    # Constructing list [constraint1, constraint2, ..., value]
                    # Example: ['disabled', '!pressed', '#CCC']
                    element = [x.replace('_', '!') for x in parts[1:]]
                    element.append(self._config[s][key])
                    composed_values[base_key].append(element)
                # Simple value
                else:
                    normal_values[key] = self._config[s][key]
            self.configure(s, **normal_values)
            self.map(s, **composed_values)

    def __visit_element(self, node):
        """Visitor for each layout element node"""
        name, tree = node
        properties = [x.lstrip('-') for x in self.element_options(name)]
        self._properties.extend(properties)
        if 'children' in tree:
            for child in tree['children']:
                self.__visit_element(child)

    def introspect(self, layout):
        """Returns a list of available properties for a given layout.

        Example:
            >>> import witkets as wtk
            >>> style = wtk.Style()
            >>> style.introspect('TLabel')
        """
        self._properties = []
        layout = self.layout(layout)
        for element in layout:
            self.__visit_element(element)
        return set(self._properties)

    def apply_from_file(self, filepath):
        """Read styles defined in *filepath* (INI file)"""
        self._config.read(filepath)
        self._apply()

    def apply_from_string(self, rules):
        """Read styles defined in string *rules* (INI string)"""
        self._config.read_string(rules)
        self._apply()

    def apply_default(self):
        """Read and apply the `witkets` package default theme"""
        template = pkgutil.get_data('witkets', 'data/default_theme.ini')
        self.apply_from_string(template.decode('utf-8'))


if __name__ == '__main__':
    import doctest

    doctest.testmod()