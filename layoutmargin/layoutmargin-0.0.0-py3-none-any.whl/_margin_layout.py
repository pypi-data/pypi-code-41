from typing import NamedTuple

from kivy.properties import ObjectProperty


class AddMargin:
    margin = ObjectProperty()
    _last_X = None
    _last_Y = None
    _last_Width = None
    _last_Height = None
    _last_MarginX = None
    _last_MarginY = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.margin = (0, 0, 0, 0)


class _Sides(NamedTuple):
    primary:    str
    center:     str
    inverted: str


_X_SIDES = _Sides("left", "center_x", "right")
_Y_SIDES = _Sides("bottom", "center_y", "top")


class MarginLayout:

    def add_widget(self, widget, index=0):
        if isinstance(widget, AddMargin):
            widget.fbind("margin", self._apply_Margins)
        return super().add_widget(widget, index)

    def remove_widget(self, widget):
        if isinstance(widget, AddMargin):
            widget.funbind("margin", self._apply_Margins)
        return super().remove_widget(widget)

    def do_layout(self, *args):
        super().do_layout(*args)
        for child in [x for x in self.children if isinstance(x, AddMargin)]:
            self._apply_Margins(child, child.margin)
        self._trigger_layout.cancel()

    def _apply_Margins(self, widget, margins):

        def get_MarginValue(i, value):
            if isinstance(value, str):
                if "%" in value:
                    maxSizes = [
                        widget.width, widget.height,
                        widget.width, widget.height
                    ]
                    percentage = float(value.replace("%", "").strip()) / 100
                    value = maxSizes[i] * percentage
                else:
                    raise ValueError(
                        f"'{widget.__class__.__name__}' invalid margin value."
                    )
            return value

        def get_MarginValues(margin):
            return (get_MarginValue(i, x) for i, x in enumerate(margin))

        def get_Initial_Position(margin, position, size):
            position += margin[0]
            size -= sum(margin)
            return position, size

        def update_Widget(key, value):
            if key == "_last_X":
                widget.x = widget._last_X = value
            elif key == "_last_Y":
                widget.y = widget._last_Y = value
            elif key == "_last_Width":
                widget.width = widget._last_Width = value
            elif key == "_last_Height":
                widget.height = widget._last_Height = value
            elif key == "_last_MarginX":
                widget._last_MarginX = value
            elif key == "_last_MarginY":
                widget._last_MarginY = value

        def update_SizeHint_Widget(
                margin, position, lastPosition_Key, size, lastSize_Key):
            position, size = get_Initial_Position(margin, position, size)
            update_Widget(lastPosition_Key, position)
            update_Widget(lastSize_Key, size)

        def update_Sized_Widget(
            sides, margin, lastMargin, lastMargin_Key,
            position, position_Hint, lastPosition, lastPosition_Key,
            size, size_Hint, lastSize, lastSize_Key,
        ):
            if lastSize is None:
                position, size = get_Initial_Position(margin, position, size)
            else:
                if(margin != lastMargin) and (position_Hint == sides.primary):
                    difference = (lastMargin[0] - margin[0])
                    position -= difference
                if(size != lastSize) and (position_Hint == sides.inverted):
                    difference = size - lastSize
                    position -= (difference + (margin[1] - difference))
                elif(position_Hint == sides.inverted):
                    position -= margin[1]
            update_Widget(lastPosition_Key, position)
            update_Widget(lastSize_Key, size)
            update_Widget(lastMargin_Key, margin)

        def apply_Margins(
            sides, margin, lastMargin, lastMargin_Key,
            position, position_Hint, lastPosition, lastPosition_Key,
            size, size_Hint, lastSize, lastSize_Key,
        ):
            if(size_Hint):
                update_SizeHint_Widget(
                    margin, position, lastPosition_Key, size, lastSize_Key)
            else:
                update_Sized_Widget(
                    sides, margin, lastMargin, lastMargin_Key,
                    position, position_Hint, lastPosition, lastPosition_Key,
                    size, size_Hint, lastSize, lastSize_Key,
                )

        left, top, right, bottom = get_MarginValues(margins)
        x_Margin, y_Margin = ((left, right), (bottom, top))
        x_Hint, y_Hint = widget.pos_hint if(widget.pos_hint) else(None, None)
        w_Hint, h_Hint = widget.size_hint

        apply_Margins(
            sides=_X_SIDES, margin=x_Margin,
            lastMargin=widget._last_MarginX, lastMargin_Key="_last_MarginX",
            position=widget.x, position_Hint=x_Hint,
            lastPosition=widget._last_X, lastPosition_Key="_last_X",
            size=widget.width, size_Hint=w_Hint,
            lastSize=widget._last_Width, lastSize_Key="_last_Width",
        )

        apply_Margins(
            sides=_Y_SIDES, margin=y_Margin,
            lastMargin=widget._last_MarginY, lastMargin_Key="_last_MarginY",
            position=widget.y, position_Hint=y_Hint,
            lastPosition=widget._last_Y, lastPosition_Key="_last_Y",
            size=widget.height, size_Hint=h_Hint,
            lastSize=widget._last_Height, lastSize_Key="_last_Height",
        )
