# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Assert import *
from PyQuantum.Common.Print import *
from PyQuantum.Common.STR import *
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
class Cavity:

    # ---------------------------------------------------------------------------------------------
    def __init__(self, n, wc, wa, g):
        Assert(isinstance(n, int), "n is not integer", cf())
        Assert(isinstance(wc, (int, float)), "wc is not numeric", cf())
        Assert(isinstance(wa, list), "wa is not list", cf())
        Assert(isinstance(g, list), "g is not list", cf())

        Assert(n > 0, "n <= 0", cf())
        Assert(wc > 0, "wc <= 0", cf())

        Assert(len(wa) == n, "len(wa) != n", cf())

        for i in range(len(wa)):
            Assert(isinstance(wa[i], (int, float)),
                   "wa[" + str(i) + "] is not numeric", cf())
            Assert(wa[i] > 0, "wa[" + str(i) + "] <= 0", cf())

        Assert(len(g) == n, "len(g) != n", cf())

        for i in range(len(g)):
            Assert(isinstance(g[i], (int, float)),
                   "g[" + str(i) + "] is not numeric", cf())
            Assert(g[i] > 0, "g[" + str(i) + "] <= 0", cf())

        self.n = n

        self.wc = wc
        self.wa = wa

        self.g = g
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_n(self):
        print(" n: ", color="yellow")

        print(self.n)

        print()
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_wc(self):
        print("wc: ", color="yellow")

        print(wc_str(self.wc))

        print()
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_wa(self):
        print("wa: ", color="yellow")

        print("[" + ", ".join([wa_str(i) for i in self.wa]) + "]")

        print()
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print_g(self):
        print(" g: ", color="yellow")

        print("[" + ", ".join([g_str(i) for i in self.g]) + "]")

        print()
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def print(self):
        print("Cavity:", color="green")

        print()
        print()

        self.print_n()
        self.print_wc()
        self.print_wa()
        self.print_g()
    # ---------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
