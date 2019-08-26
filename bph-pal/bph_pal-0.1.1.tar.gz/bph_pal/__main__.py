# Copyright (c) 2019 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""packet init for BPH PAL
This exposes a main function to run the packet from CLI
"""
import argparse
import logging
try:
    from .bph_shell import BphShell as BPH
except (ImportError, SystemError):
    try:
        from bph_pal.bph_shell import BphShell as BPH
    except (ImportError, SystemError):
        from bph_shell import BphShell as BPH


def main():
    """
    Main function to allow direct exec of bph_pal package from CLI
    """
    log_levels = ('debug', 'info', 'warning', 'error', 'fatal', 'critical')
    parser = argparse.ArgumentParser(prog='python3 -m bph_pal')
    parser.add_argument('--loglevel', '-l', choices=log_levels, default='info',
                        help='Python logger log level')
    parser.add_argument('--philip_reset', '-pr', action='store_true',
                        help='Hard reset of PHiLIP', default=False)
    parser.add_argument('--load_pinmap', '-lp', default=False,
                        help='Loads and initializes pinmap')
    parser.add_argument('--set_pin', '-sp',
                        help='Sets the pin by key or name')
    parser.add_argument('--clear_pin', '-clp',
                        help='Clear the pin by key or name')
    parser.add_argument('--input_pin', '-inp',
                        help='Changes pin to input by key or name')
    parser.add_argument('--power_source', '-ps',
                        help='Sets the power source mode')
    parser.add_argument('--init_pins', '-ip', action='store_true',
                        help='Initializes pins to defaults', default=False)
    pargs = parser.parse_args()

    logging.basicConfig(level=getattr(logging, pargs.loglevel.upper()))

    if pargs.philip_reset:
        BPH().onecmd("philip_reset")
    if pargs.load_pinmap:
        BPH().onecmd("load_pinmap " + str(pargs.load_pinmap))
    if pargs.set_pin:
        BPH().onecmd("set_pin " + str(pargs.set_pin))
    if pargs.clear_pin:
        BPH().onecmd("clear_pin " + str(pargs.clear_pin))
    if pargs.input_pin:
        BPH().onecmd("input_pin " + str(pargs.input_pin))
    if pargs.power_source:
        BPH().onecmd("power_source " + str(pargs.power_source))
    if pargs.init_pins:
        BPH(init_state=True)


main()
