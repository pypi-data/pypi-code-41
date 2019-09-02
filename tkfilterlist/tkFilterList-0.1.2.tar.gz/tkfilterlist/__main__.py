"""Demonstration of the FilterList widget."""

try:
    # Python 3
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.messagebox import showinfo, showwarning
except (ImportError):
    # Python 2
    from Tkinter import *
    from ttk import *
    from tkMessageBox import showinfo, showwarning

from . import *


def demo():
    """Display a demonstration of the FilterList widget."""

    root = Tk()
    root.title("FilterList Demo")

    # Provide lots of ways to close the window
    for seq in "<Escape>", "<Control-w>", "<Control-q>":
        root.bind(seq, lambda event: root.destroy())

    # Sample data for the list
    entries = [
        ("John Lennon", "The Beatles"),
        ("Paul McCartney", "The Beatles"),
        ("George Harrison", "The Beatles"),
        ("Ringo Starr", "The Beatles"),
        ("Mick Jagger", "The Rolling Stones"),
        ("Keith Richards", "The Rolling Stones"),
        ("Charlie Watts", "The Rolling Stones"),
        ("Bill Wyman", "The Rolling Stones"),
        ("Bryan Jones", "The Rolling Stones"),
        ("Roger Daltrey", "The Who"),
        ("Pete Townshend", "The Who"),
        ("John Entwistle", "The Who"),
        ("Keith Moon", "The Who"),
    ]

    # The Listbox should show the name only
    display_rule = lambda item: "{0} ({1})".format(item[0], item[1])
    filter_rule = lambda item, text: text.lower() in item[0].lower()

    f = FilterList(root,
                   source=entries,
                   display_rule=display_rule,
                   filter_rule=filter_rule)
    f.pack(side="top", expand=1, fill="both", padx=8, pady=8)
    f.focus_set()

    def show_selection(event):
        """Display the selected item."""

        item = f.selection()

        if item:
            showinfo("Selected Item",
                     "You selected {0} of {1}.".format(item[0], item[1]),
                     parent=root)

        else:
            showwarning("No Selected Item",
                        "No items were found matching the entered text.",
                        parent=root)

    # Display the selected item on Return or double-click
    f.bind("<Return>", show_selection)
    f.bind("<Double-Button-1>", show_selection)

    root.mainloop()


if __name__ == "__main__":
    demo()
