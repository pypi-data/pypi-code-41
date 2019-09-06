import numbers
from enum import Enum
from ast import literal_eval
from collections import abc

# =============================================================================
# Helper Functions
# =============================================================================

def _parse_padding(val, numtokens):
    """Parse a padding attribute.

    Paddings can be in one of the forms below:
      - '15' --- pixels (can be passed as string or integer)
      - '<num><unit>' --- number followed by a unit ('c', 'i', 'm' or 'p')
      - '<padding> <padding>' --- space-separated values
      - '(<padding>, <padding>)' --- tuple
      -
    """
    val = val.strip()
    if val.startswith('('):
        no_parenthesis = val.replace('(', '').replace(')', '')
        tokens = no_parenthesis.replace(' ', '').split(',')
        if len(tokens) > numtokens:
            raise ValueError()
        return tuple(tokens)
    return val

# =============================================================================
# Basic Types
# =============================================================================

class boolean:
    @staticmethod
    def parse(value):
        if value == 'True' or value == '1':
            return True
        elif value == 'False' or value == '0':
            return False
        raise ValueError()

class uint8(int): pass

class uint16(int): pass

class int8(int): pass

class int16(int): pass

class image(str): pass #file type!

class color(str): pass

# =============================================================================
# Tk Types
# =============================================================================

class padding2:
    @staticmethod
    def parse(value):
        """Parse axis paddings (one or two dimensions)."""
        return _parse_padding(value, 2)

class padding4:
    @staticmethod
    def parse(value):
        """Parse global paddings (one, two or four dimensions)"""
        return _parse_padding(value, 4)

# =============================================================================
# Plot Widget Attributes
# =============================================================================

class plotlabels:
    @staticmethod
    def parse(value):
        value = value.strip()
        # Case 1: '/5'
        if value.startswith('/'):
            return value
        # Case 2: Multiple
        elif value.startswith('('):
            pairs = []
            value.replace(' ', '')
            for p in value.split('),'):
                pair_csv = p.replace('(', '').replace(')', '').replace(' ', '')
                pairs.append(pair_csv.split(','))
            return [ (float(fst), snd) for fst,snd in pairs ]
        # Case 3: Single value
        else:
            return float(value)


def _parse_plot_with_type(value, parser):
    value = value.strip()
    # Compound
    if value.startswith('('):
        value = value.replace('(', '').replace(')', '')
        value = value.replace(' ', '')
        return [parser(v) for v in value.split(',')]
    # Single value
    return parser(value)


class plotlimits:
    @staticmethod
    def parse(value):
        value = _parse_plot_with_type(value, float)
        if not isinstance(value, abc.Sequence):
            raise ValueError()
        return value


class plotstrconfig:
    @staticmethod
    def parse(value):
        return _parse_plot_with_type(value, str)


class plotintconfig:
    @staticmethod
    def parse(value):
        return _parse_plot_with_type(value, int)


class plotboolconfig:
    @staticmethod
    def parse(value):
        return _parse_plot_with_type(value, boolean.parse)


class plotrealconfig:
    @staticmethod
    def parse(value):
        return _parse_plot_with_type(value, float)


class dimension(str):
    @staticmethod
    def parse(val):
        pass #TODO

# =============================================================================
# Enumerations
# =============================================================================

class compound(Enum):
    none = 'none'
    top = 'top'
    bottom = 'bottom'
    left = 'left'
    right = 'right'

class justify(Enum):
    left = 'left'
    center = 'center'
    right = 'right'

class orient(Enum):
    horizontal = 'horizontal'
    vertical = 'vertical'

class anchor(Enum):
    nw = 'nw'
    n = 'n'
    ne = 'ne'
    w = 'w'
    center = 'center'
    e = 'e'
    sw = 'sw'
    s = 's'
    se = 'se'

class bitmap(Enum):
    error = 'error'
    gray75 = 'gray75'
    gray50 = 'gray50'
    gray25 = 'gray25'
    gray12 = 'gray12'
    hourglass = 'hourglass'
    info = 'info'
    questhead = 'questhead'
    question = 'question'
    warning = 'warning'

class progressmode(Enum):
    indeterminate = 'indeterminate'
    determinate = 'determinate'

class validate(Enum):
    focus = 'focus'
    focusin = 'focusin'
    focusout = 'focusout'
    key = 'key'
    all = 'all'
    none = 'none'

class activestyle(Enum):
    underline = 'underline'
    dotbox = 'dotbox'
    none = 'none'

class relief(Enum):
    flat = 'flat'
    raised = 'raised'
    sunken = 'sunken'
    groove = 'groove'
    ridge = 'ridge'

class state(Enum):
    normal = 'normal'
    disabled = 'disabled'

class selectmode(Enum):
    browse = 'browse'
    single = 'single'
    multiple = 'multiple'
    extended = 'extended'

class cursor(Enum):
    arrow = 'arrow'
    based_arrow_down = 'based_arrow_down'
    based_arrow_up = 'based_arrow_up'
    boat = 'boat'
    bogosity = 'bogosity'
    bottom_left_corner = 'bottom_left_corner'
    bottom_right_corner = 'bottom_right_corner'
    bottom_side = 'bottom_side'
    bottom_tee = 'bottom_tee'
    box_spiral = 'box_spiral'
    center_ptr = 'center_ptr'
    circle = 'circle'
    clock = 'clock'
    coffee_mug = 'coffee_mug'
    cross = 'cross'
    cross_reverse = 'cross_reverse'
    crosshair = 'crosshair'
    diamond_cross = 'diamond_cross'
    dot = 'dot'
    double_arrow = 'double_arrow'
    draft_large = 'draft_large'
    draft_small = 'draft_small'
    draped_box = 'draped_box'
    exchange = 'exchange'
    fleur = 'fleur'
    gobbler = 'gobbler'
    gumby = 'gumby'
    hand1 = 'hand1'
    hand2 = 'hand2'
    heart = 'heart'
    icon = 'icon'
    iron_cross = 'iron_cross'
    left_ptr = 'left_ptr'
    left_side = 'left_side'
    left_tee = 'left_tee'
    leftbutton = 'leftbutton'
    ll_angle = 'll_angle'
    lr_angle = 'lr_angle'
    man = 'man'
    middlebutton = 'middlebutton'
    mouse = 'mouse'
    pencil = 'pencil'
    pirate = 'pirate'
    plus = 'plus'
    question_arrow = 'question_arrow'
    right_ptr = 'right_ptr'
    right_side = 'right_side'
    right_tee = 'right_tee'
    rightbutton = 'rightbutton'
    rtl_logo = 'rtl_logo'
    sailboat = 'sailboat'
    sb_down_arrow = 'sb_down_arrow'
    sb_h_double_arrow = 'sb_h_double_arrow'
    sb_left_arrow = 'sb_left_arrow'
    sb_right_arrow = 'sb_right_arrow'
    sb_up_arrow = 'sb_up_arrow'
    sb_v_double_arrow = 'sb_v_double_arrow'
    shuttle = 'shuttle'
    sizing = 'sizing'
    spider = 'spider'
    spraycan = 'spraycan'
    star = 'star'
    target = 'target'
    tcross = 'tcross'
    top_left_arrow = 'top_left_arrow'
    top_left_corner = 'top_left_corner'
    top_right_corner = 'top_right_corner'
    top_side = 'top_side'
    top_tee = 'top_tee'
    trek = 'trek'
    ul_angle = 'ul_angle'
    umbrella = 'umbrella'
    ur_angle = 'ur_angle'
    watch = 'watch'
    xterm = 'xterm'
    X_cursor = 'X_cursor'

