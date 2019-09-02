"""A self-filtering Listbox with text entry for Tkinter.

tkFilterList is a combination of the Tkinter Listbox and Entry widgets
that updates to display matching items as you type.

You can customize the item display and filtering behavior by setting
its display_rule and filter_rule options, respectively, to your own
custom functions. This allows tkFilterList to process lists containing
complex datatypes, including nested lists, tuples, and even entire
classes. The functions are defined as follows:

  display_rule(item)
    Returns the display text for the specified item.

    The default is available as FilterList.default_display_rule.
    It returns the string value of item, matching the behavior of
    a standard Listbox widget.

  filter_rule(item, text)
    Returns True if the text argument matches the specified item,
    False otherwise.

    The default is available as FilterList.default_filter_rule.
    It returns True if an item starts with the specified text using
    a case-insensitive match.
"""

from .widget import FilterList

# The only thing we need to publicly export is the widget itself
__all__ = ["FilterList"]
