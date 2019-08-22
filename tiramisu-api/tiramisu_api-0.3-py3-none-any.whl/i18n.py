try:
    from tiramisu.i18n import _
except ImportError:
    # FIXME
    def _(val):
        return val
