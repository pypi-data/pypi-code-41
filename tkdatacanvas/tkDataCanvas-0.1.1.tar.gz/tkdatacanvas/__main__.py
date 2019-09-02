"""A simple spreadsheet viewer to demonstrate the tkDataCanvas module.

Only comma-separated values (CSV) are currently supported.
"""

# Copyright (c) 2018 Benjamin Johnson
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import sys
import io
import csv

try:
    # Python 3
    from tkinter import *
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
except (ImportError):
    # Python 2
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkMessageBox import showerror

from . import DataCanvas


class DataCanvasDemo(Frame):
    """A demonstration of the DataCanvas widget."""

    def __init__(self, master=None, custom_colors=False):
        Frame.__init__(self, master)
        self.master = master

        if custom_colors:
            # Use a custom color palette quite distinct from the default
            canvas_colors = {
                "bg_color": "antique white",
                "fg_color": "dark goldenrod",
                "bg_header": "forest green",
                "fg_header": "white",
                "bg_shade": "light goldenrod",
                "fg_shade": "maroon",
            }
        else:
            canvas_colors = {}

        # The DataCanvas widget
        # This will be packed in display_file()
        c = self.data_canvas = DataCanvas(self,
                                          width=800,
                                          height=600,
                                          pad_x=2,
                                          **canvas_colors)
        c.bind_arrow_keys(master)
        c.bind_scroll_wheel(master)

        # Dummy widget shown until we've loaded a file
        self.dummy = Label(self,
                           text="Please select a file to display.")
        self.dummy.pack(side="top", expand=1, fill="both", padx=24, pady=24)

        # Make it easy to close this window
        for seq in "<Control-w>", "<Control-q>":
            self.master.bind(seq, self.close)

    def browse(self, event=None):
        """Browse for a file to display."""

        filetypes = ("Comma-Separated Values", "*.csv"),

        path = askopenfilename(parent=self,
                               title="Open File",
                               filetypes=filetypes)

        if path:
            self.display_file(os.path.normpath(path))

        else:
            self.after(50, self.close)

    def display_file(self, path):
        """Display the specified file."""

        # Replace our dummy widget with the DataCanvas
        self.dummy.pack_forget()
        self.data_canvas.pack(side="top", expand=1, fill="both")

        # Parse the CSV file
        try:
            with io.open(path, "r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                rows_parsed = 0

                for row in reader:
                    if rows_parsed == 0:
                        # Display the first row as a header
                        self.data_canvas.add_header("", *row)

                    else:
                        # Include the row number
                        self.data_canvas.add_cell(rows_parsed)
                        self.data_canvas.add_row(*row)

                    rows_parsed += 1

                self.data_canvas.display()

        except (Exception) as err:
            showerror("Error", err, parent=self)
            raise

        # Update the window title
        self.master.title("tkDataCanvas: " + path)

    def close(self, event=None):
        """Close the window."""

        self.master.destroy()


def demo():
    """Display a demonstration of the DataCanvas widget."""

    # Create a root window
    root = Tk()
    root.title("tkDataCanvas")

    # Use a custom color palette if a "-c" argument is present
    if "-c" in sys.argv[1:]:
        custom_colors = True
        sys.argv.remove("-c")
    else:
        custom_colors = False

    d = DataCanvasDemo(root, custom_colors)
    d.pack(side="top", expand=1, fill="both")

    # If a CSV file was named on the command line, display it
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[-1]):
        # Last command line argument is the file path
        path = sys.argv[-1]
        d.display_file(path)

    else:
        # Browse for a file to display after the main loop has started
        root.after(500, d.browse)

    root.mainloop()


if __name__ == "__main__":
    demo()
