import tkinter as tk
import tkinter.ttk as ttk
import witkets.core.wtk_types as wtk_types

attribspec = {
    ttk.Frame: {
        'takefocus': wtk_types.boolean,
        'padding': wtk_types.padding4
    },
    'pack': {
        'padx': wtk_types.padding2,
        'pady': wtk_types.padding4,
        'expand': wtk_types.boolean
    },
    'grid': {
        'padx': wtk_types.padding2,
        'pady': wtk_types.padding2
    },
    'tab': {
        'padding': wtk_types.padding4
    }
}