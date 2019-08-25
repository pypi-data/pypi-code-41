from maeguias import utils as maeguias_utils
from maeguias.config import config_options, Config
from maeguias.plugins import BasePlugin
from maeguias.structure.files import Files
from maeguias.structure.nav import Navigation as MaeNavigation

from .navigation import MaeHamNavigation
from .options import Options


class MaeHamPlugin(BasePlugin):

    DEFAULT_META_FILENAME = '.pages'

    config_scheme = (
        ('filename', config_options.Type(maeguias_utils.string_types, default=DEFAULT_META_FILENAME)),
        ('collapse_single_pages', config_options.Type(bool, default=False))
    )

    def on_nav(self, nav: MaeNavigation, config: Config, files: Files):
        return MaeHamNavigation(nav, Options(**self.config)).to_maeguias()
