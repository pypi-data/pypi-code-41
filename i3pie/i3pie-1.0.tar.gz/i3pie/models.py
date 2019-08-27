from collections.abc import Sequence
from itertools import islice, chain
from operator import attrgetter, __not__


class SkipItem(Exception):
    pass


def _format_items(d, keys=None, fmt="{key}={value!r}", sep=" ", prefix="", suffix=""):
    """Return a formatted string of dictionary items joined together.

    Args:
        d (dict): The source dictionary.
        keys (list): List of keys to format. If ``None`` all keys are formatted.
            An item can be a string a two-item sequence: (string, function)`` where the
            function is called to evaluate the value for the current pair. An exception
            ``SkipItem`` may be raised inside this function in order to exclude the
            current key-value pair from the autput.
        fmt (str): The format string used for each key-value pair. It should include any
            combination of the placeholders ``{key}`` and ``{value}``.
        sep (str): The string used to separate each formatted pair.
        prefix (str): The string prefixed to all formattd keys.
        suffix (str): The string suffixed to all formattd keys.

    Returns:
        A string of the formatted key-value pairs.

    Exmples:

        >>> _format_items({'a': 1, 'b': 2})
        'a=1 b=2'

        >>> _format_items({'a': 1, 'b': 2}, sep=', ', prefix='[ ', suffix=' ]')
        '[ a=1, b=2 ]'

        >>> _format_items({'a': 1, 'b': 2}, keys=('a',))
        'a=1'

        >>> def get_value(d):
        ...     if d["b"] is None:
        ...         return '?'
        ...
        >>> _format_items({'a': 1, 'b': None}, keys=['a', ('b', get_value)])
        "a=1 b='?'"

        >>> def get_value(d):
        ...     if d.has_key("a"):
        ...         raise SkipItem
        ...
        >>> _format_items({'a':1, 'b':2}, keys=['a', ('b', get_value)])
        'a=1'

    """

    if keys is None:
        keys = list(sorted(d.keys()))

    items = []
    for key in keys:
        try:
            if isinstance(key, list) or isinstance(key, tuple):
                if len(key) != 2:
                    raise TypeError(f"list field key must be a two-item long: {key}")
                if not callable(key[1]):
                    raise TypeError(
                        f"'{type(key[1])}' object is not callable: {key[1]}"
                    )
                value = key[1](d)
                key = key[0]
            else:
                value = d[key]
        except (AttributeError, KeyError):
            value = None
        except SkipItem:
            continue

        items.append(fmt.format(key=key, value=value))

    return prefix + sep.join(items) + suffix


class Container:
    """Tree of containers.

    Reference: https://i3wm.org/docs/ipc.html#_tree_reply

    Attributes:
        parent (Container): The parent container of this container. ``None`` for the root
            container.
        nodes (list): The non-floating child containers of this node.
        floating_nodes (list): The floating child containers of this node. Only
            non-empty on nodes with type workspace.
        id (int): The internal ID of the container. To be used as ``[con_id=<id>]``.
        name (str): The internal name of the container. For all containers which are
            part of the tree structure down to the workspace contents, this is set to
            a nice human-readable name of the container. For containers that have an X11
            window, the content is the title (_NET_WM_NAME property) of that window. For
            all other containers, the content is not defined.
        type (str): Type of the container. Can be one of "root", "output", "con",
            "floating_con", "workspace" or "dockarea".
        border (str): The border style of the container. Can be either "normal", "none" or "pixel".
        current_binorder_width (int): Number of pixels of the border width.
        layout (str): The layout of the contaienr. Can be either "splith", "splitv",
            "stacked", "tabbed", "dockarea" or "output".
        percent (float): The percentage which this container takes in its parent.
            A value of ``None`` means that the percent property does not make sense for
            this container, for example for the root container.
        rect (dict): The absolute display coordinates for the container. Display
            coordinates means that when you have two 1600x1200 monitors on a single X11
            Display, the coordinates of the first window on the second monitor are
            ``{"x": 1600, "y": 0, "width": 1600, "height": 1200}``.
        window_rect (dict): The coordinates of the actual client window inside its
            container. These coordinates are relative to the container and do not
            include the window decoration (which is actually rendered on the parent
            container).
        deco_rect (dict): The coordinates of the window decoration inside its container.
            These coordinates are relative to the container and do not include the
            actual client window.
        geometry (dict): The original geometry the window specified when i3 mapped it.
            Used when switching a window to floating mode, for example.
        window (int): The X11 window ID of the actual client window inside the
            container. This field is set to ``None`` for split containers or otherwise
            empty containers.
        window_properties (dict): X11 window properties title, instance, class,
            window_role and transient_for. Empty dictionary for non-window containers.
        window_id (int) Alias for ``window`` (Read only).
        window_title (str): Alias for ``window_properties["title"]``.
        window_instance (str): Alias for ``window_properties["instance"]``.
        window_class (str): Alias for ``window_properties["class"].``.
        window_role (str): Alias for ``window_properties["window_role"]``.
        urgent (bool): Whether the container has the urgency hint set, directly or
            indirectly. All parent containers up until the workspace container will be
            marked urgent if they have at least one urgent child.
        focused (bool): Whether the container is currently focused.
        focus (list): List of child node IDs in focus order. Traversing the tree by
            following the first entry in this array will result in eventually reaching
            the one node with focused set to true.
        num (int): Workspace number. ``None`` for non-workspace containers.
        marks (list): List of window marks. ``None`` for non-window contaienrs.
    """

    def __get_id(d):
        if d["window"]:
            return d["window"]
        raise SkipItem

    def __get_class(d):
        if d.get("window_properties"):
            return d["window_properties"]["class"]
        raise SkipItem

    def __get_name(d):
        if d.get("window_properties") or d["name"] is None:
            # the container is a normal window
            raise SkipItem
        return d["name"]

    _STR_FIELDS = ("type", ("class", __get_class), ("name", __get_name))
    _REPR_FIELDS = (
        ("window", __get_id),
        "type",
        ("class", __get_class),
        ("name", __get_name),
    )

    _I3_PREFIX = "__i3"
    _SCRATCHPAD_NAME = "__i3_scratch"

    def __init__(self, conn, d, parent=None):
        self._conn = conn

        self.parent = parent
        self.nodes = d.get("nodes")
        self.floating_nodes = d.get("floating_nodes")

        self.id = d.get("id")
        self.name = d.get("name")
        self.type = d.get("type")
        self.border = d.get("border")
        self.current_border_width = d.get("current_border_width")
        self.layout = d.get("layout")
        self.percent = d.get("percent")
        self.rect = d.get("rect")
        self.window_rect = d.get("window_rect")
        self.deco_rect = d.get("deco_rect")
        self.geometry = d.get("geometry")
        self.window = d.get("window")
        self.window_properties = d.get("window_properties", {})
        self.urgent = d.get("urgent")
        self.focused = d.get("focused")
        self.focus = d.get("focus")
        self.num = d.get("num")

        if self.is_window:
            self.marks = d.get("marks", [])
        else:
            self.marks = None

        # Undocumented:
        #  <field: <found on>
        # - sticky: all
        # - floating: all
        # - scratchpad_state: all
        # - workspace_layout: all
        # - last_split_layout: all
        # - fullscreen_mode: all
        # - swallows: all
        # - output: some

    @property
    def window_id(self):
        return self.window

    @property
    def window_title(self):
        return self.window_properties.get("title")

    @window_title.setter
    def window_title(self, value):
        self.window_properties["title"] = value

    @property
    def window_class(self):
        return self.window_properties.get("class")

    @window_class.setter
    def window_class(self, value):
        self.window_properties["class"] = value

    @property
    def window_instance(self):
        return self.window_properties.get("instance")

    @window_instance.setter
    def window_instance(self, value):
        self.window_properties["instance"] = value

    @property
    def window_role(self):
        return self.window_properties.get("window_role")

    @window_role.setter
    def window_role(self, value):
        self.window_properties["window_role"] = value

    @property
    def is_internal(self):
        return self.name and self.name.startswith(self._I3_PREFIX)

    @property
    def is_floating(self):
        return self.parent.type == "floating_con" if self.parent else False

    @property
    def is_window(self):
        return self.type == "con" and not list(self.children)

    @property
    def is_workspace(self):
        return self.type == "workspace"

    @property
    def is_output(self):
        return self.type == "output"

    @property
    def is_dockarea(self):
        return self.type == "dockarea"

    @property
    def is_scratchpad(self):
        return self.is_workspace and self.name == self._SCRATCHPAD_NAME

    @property
    def children(self):
        return list(reversed(self.nodes)) + self.floating_nodes

    def output(self):
        """Returns the output of the current container."""
        con = self
        while con.parent:
            if con.is_output:
                return con
            con = con.parent

    def workspace(self):
        """Returns the workspace of the current container."""
        con = self
        while con.parent:
            if con.is_workspace:
                return con
            con = con.parent

    def root(self):
        """Returns the root container."""
        con = self
        while con.parent:
            con = con.parent
        return con

    def command(self, cmd):
        """Executes a command on the current container."""
        return self._conn.command(f'[con_id="{self.id}"] {cmd}')

    def filter(
        self, fn=bool, prune=None, lazy=True, first=False, i3=False, dockarea=False
    ):
        """Returns the containers that satisfy the given tests.

        Make an iterator that filters containers from the current container tree
        returning only those for which the function ``fn`` returns ``True``.

        Args:
            fn (function): The function called for every container (passed as its
                argument) that determines whether or not the container is returned.
            prune (function): A function called for every container (passed as its
                argument). If the. function returns ``True`` the container is discarded
                along with all its descendants containers.
            lazy (bool): Discard all container descendants whenever the ``fn`` function
                returns ``True``.
            first (bool): Returns only the fisrt result.
            i3 (bool): When ``i3 == False``, all i3 internal containers and their
                descendants are discarded. dockarea (bool): When ``dockarea == False``,
                all dock areas are discarded.

        Returns:
            An iterator or a single Container when ``first == True`` (or ``None`` when
            nothing is found).

        """

        if prune is None:
            # always return False when called on an object
            prune = __not__

        # Prune the container and its subtree for which this function returns True.
        def _prune(con):
            return (
                not dockarea
                and con.is_dockarea
                or not i3
                and con.is_internal
                or prune(con)
            )

        def _filter(container):
            stack = [container]
            while stack:
                current = stack.pop()
                if _prune(current):
                    continue
                if fn(current):
                    yield current
                    if lazy:
                        # Don't visit the subtree
                        continue
                stack.extend(current.children)

        results = _filter(self)

        if first:
            try:
                return list(islice(results, 1))[0]
            except IndexError:
                return None
        else:
            return results

    def find(self, **kwargs):
        """Returns the first result from filter(..).

        Args:
            kwargs (dict): Argumets passed directly to filter(..).

        Returns:
            A ``Container``.
        """
        return self.filter(first=True, **kwargs)

    def find_workspace(self, fn=bool, **kwargs):
        """Returns the first workspace container for which the function ``fn`` returns True.

        Args:
            fn (function): The function called for every container (passed as its
                argument) that determines whether or not the container is returned.
            kwargs (dict): Arguments passed directly to filter(..).

        Returns:
            A workspace ``Container``.
        """

        def _fn(con):
            return con.is_workspace and fn(con)

        return self.filter(fn=_fn, first=True, **kwargs)

    def find_window(self, fn=bool, floating=True, **kwargs):
        """Returns the first window container for which the function ``fn`` returns True.

        Args:
            fn (function): The function called for every container (passed as its
                argument) that determines whether or not the container is returned.
            floating (bool): Whether or not floating containers are returned.
            kwargs (dict): Arguments passed directly to filter(..).

        Returns:
            An window ``Container``.
        """

        def _fn(con):
            return (
                (floating or not floating and not con.is_floating)
                and con.is_window
                and fn(con)
            )

        return self.filter(fn=_fn, first=True, **kwargs)

    def walk(self, bf=False):
        """Returns all descendants.

        Args:
            bf (bool): When ``bf=True``, the container descendants are visited in
                a breadth-first manner.

        Returs:
            An iterator of Containers.
        """
        return self._walk_bf() if bf else self._walk_df()

    def _walk_df(self, bf=False):
        """Returns all container descendants. Top-down depth-first traversal.
        """
        unvisited = [self]
        while unvisited:
            current = unvisited.pop()
            yield current
            unvisited.extend(current.children)

    def _walk_bf(self):
        """Returns all container descendants. Top-down breadth-first traversal.
        """
        unvisited = iter([self])
        while True:
            try:
                current = next(unvisited)
            except StopIteration:
                return
            yield current
            unvisited = chain(unvisited, current.children)

    def windows(self, floating=True, scratchpad=False):
        """Returns all windows in the current container.

        Args:
            floating (bool): Whether or not floating containers are returned.
            scratchpad (bool): Wheter or not scratchpad windows are returned.

        Returns:
            An iterator of window Containers.
        """

        def fn(con):
            return (floating or not floating and not con.is_floating) and con.is_window

        output = self.output()
        if not scratchpad and output and output.is_internal:
            scratchpad = True

        return self.filter(fn=fn, i3=scratchpad)

    def floating_windows(self, scratchpad=False):
        """Returns all floating windows in the current container.

        Args:
            scratchpad (bool): Wheter or not scratchpad windows are returned.

        Returns:
            An iterator of window Containers.
        """

        def fn(con):
            return con.is_window and con.is_floating

        output = self.output()
        if not scratchpad and output and output.is_internal:
            scratchpad = True

        return self.filter(fn=fn, i3=scratchpad)

    def workspaces(self, scratchpad=False):
        """Returns all workspaces.

        Makes sense only when called from the root container.

        Args:
            scratchpad (bool): Wheter or not the scratchpad container is returned.

        Returns:
            An iterator of workspace Containers.
        """
        return self.filter(fn=attrgetter("is_workspace"), i3=scratchpad)

    def outputs(self, i3=False):
        """Returns all outputs.

        Makes sense only when called from the root container.

        Args:
            i3 (bool): Wheter or not the i3 internal container is returned.

        Returns:
            An iterator of outputs Containers.
        """
        return self.filter(fn=attrgetter("is_output"), i3=i3)

    def scratchpad(self):
        """Returns the scratchpad workspace container.
        """
        return self.filter(fn=attrgetter("is_scratchpad"), i3=True, first=True)

    def focused_window(self):
        """Returns the focused window.

        Needs to be called from root/workspace containers in order to be able to
        actually retrieve the focused window.
        """
        current = self
        while True:
            if current.focused and current.is_window:
                return current
            if not current.focus:
                return
            for child in current.children:
                if current.focus and child.id == current.focus[0]:
                    current = child
                    break

    def current_workspace(self):
        """Returns the current workspace.

        Needs to be called from root/workspace containers in order to be able to
        actually retrieve the current workspace.
        """
        current = self
        while True:
            if current.is_workspace:
                return current
            if not current.focus:
                return
            for child in current.children:
                if current.focus and child.id == current.focus[0]:
                    current = child
                    break

    def _pprint(self, props=None):
        """Pretty-print the current container tree.

        The argument ``props`` must be a list of keys or key/function pairs that define
        how each contaienr should be formatted. See ``_format_items`` function. It
        defaults to ``Container._REPR_FIELDS``.

        Example:

            >>> tree = Connection().get_tree()
            >>> tree._pprint()
            type='root' name='root'
            ├─ type='output' name='__i3'
            │  └─ type='con' name='content'
            │     └─ type='workspace' name='__i3_scratch'
            └─ type='output' name='HDMI-A-0'
               ├─ type='dockarea' name='topdock'
               │  └─ window=44040194 type='con' class='Polybar'
               ├─ type='con' name='content'
               │  └─ type='workspace' name='1'
               │     └─ type='con' name=None
               │        └─ window=23068681 type='con' class='URxvt'
               └─ type='dockarea' name='bottomdock'

        """

        if props is None:
            props = self._REPR_FIELDS

        def _pprint(con, padding, last_child):

            curr_padding = ""
            next_padding = padding

            if con.parent:
                curr_padding = padding + ("└─ " if last_child else "├─ ")
                next_padding = padding + ("   " if last_child else "│  ")

            line = curr_padding + _format_items(con.__dict__, keys=props)
            print(line)

            nodes = list(con.children)
            for i, child in enumerate(nodes):
                _pprint(child, next_padding, i == len(nodes) - 1)

        _pprint(self, "", 0)

    def __iter__(self):
        return self.walk()

    def __str__(self):
        props = _format_items(self.__dict__, keys=self._STR_FIELDS)
        return f"<{self.__class__.__name__} {props}>"

    def __repr__(self):
        props = _format_items(self.__dict__, keys=self._REPR_FIELDS, sep=", ")
        return f"{self.__class__.__name__}({props})"


class WorkspaceReply:
    """Workspace reply.

    Reference: https://i3wm.org/docs/ipc.html#_workspaces_reply

    Attributes:
        num (int): The logical number of this workspace. Corresponds to the command to
            switch to this workspace. For named workspaces, this will be -1.
        name (str): The name of this workspace
        visible (bool): Whether this workspace is currently visible on an output
            (multiple workspaces can be visible at the same time).
        focused (bool): Whether this workspace currently has the focus (only one
            workspace can have the focus at the same time).
        urgent (bool): Whether a window on this workspace has the "urgent" flag set.
        rect (dict): The rectangle of this workspace (equals the rect of the output it
            is on), consists of x, y, width, height.
        output (str): The video output this workspace is on.
    """

    _STR_FIELDS = ("name",)
    _REPR_FIELDS = ("num", "name")

    def __init__(self, d):
        self.num = d.get("num")
        self.name = d.get("name")
        self.visible = d.get("visible")
        self.focused = d.get("focused")
        self.urgent = d.get("urgent")
        self.rect = d.get("rect")
        self.output = d.get("output")

    def __str__(self):
        info = _format_items(self.__dict__, keys=self._STR_FIELDS)
        return f"<{self.__class__.__name__} {info}>"

    def __repr__(self):
        info = _format_items(self.__dict__, keys=self._REPR_FIELDS, sep=", ")
        return f"{self.__class__.__name__}({info})"


class OutputReply:
    """Output reply.

    Reference: https://i3wm.org/docs/ipc.html#_outputs_reply

    Attributes:
        name (str): The name of this output.
        active (bool): Whether this output is currently active (has a valid mode).
        primary (bool): Whether this output is currently the primary output.
        current_workspace (str): The name of the current workspace that is visible on
            this output. ``None`` if the output is not active.
        rect (map): The rectangle of this output (equals the rect of the output it is
            on), consists of x, y, width, height.
    """

    _STR_FIELDS = ("name",)
    _REPR_FIELDS = ("name",)

    def __init__(self, d):
        self.name = d.get("name")
        self.active = d.get("active")
        self.primary = d.get("primary")
        self.current_workspace = d.get("current_workspace")
        self.rect = d.get("rect")

    def __str__(self):
        info = _format_items(self.__dict__, keys=self._STR_FIELDS)
        return f"<{self.__class__.__name__} {info}>"

    def __repr__(self):
        info = _format_items(self.__dict__, keys=self._REPR_FIELDS, sep=", ")
        return f"{self.__class__.__name__}({info})"


class CommandReply(Sequence):
    """Command reply.

    Reference: https://i3wm.org/docs/ipc.html#_command_reply

    Atributes:
        error (bool): Whether or not there are any errors in the reply.
        success (bool): Whether or not there are any errors in the reply.
    """

    def __init__(self, reply):
        self._reply = reply
        self.error = any(not i["success"] for i in reply)
        self.success = not self.error

    def errors(self, enumerate_=True):
        """Return all errors, if any.

        Args:
            enumerate_ (bool): Whether or not enumerate the errors. When ``enumerate_ ==
                True`` every error is accompained by the position of the specific command
                that failed.

        Returns:
            A list of errors.
        """
        for i, item in enumerate(self._reply):
            if not item["success"]:
                yield (i, item) if enumerate_ else item

    def __getitem__(self, index):
        return self._reply[index]

    def __len__(self):
        return len(self._reply)

    def __str__(self):
        return f"<{self.__class__.__name__} success={not(self.error)!r}>"

    def __repr__(self):
        return f"{self.__class__.__name__}(success={not(self.error)!r})"


class VersionReply:
    """Version reply.

    Reference: https://i3wm.org/docs/ipc.html#_version_reply

    Attributes:
        major (int): The major version of i3.
        minor (int): The minor version of i3.
        patch (int): The patch version of i3.
        human_readable (str): A human-readable version of the i3 version
            (as returned by ``i3 --version``).
        loaded_config_file_name (str): The current config path.
    """

    _STR_FIELDS = ("major", "minor", "patch")
    _REPR_FIELDS = ("major", "minor", "patch")

    def __init__(self, d):
        self.major = d.get("major")
        self.minor = d.get("minor")
        self.patch = d.get("patch")
        self.human_readable = d.get("human_readable")
        self.loaded_config_file_name = d.get("loaded_config_file_name")

    def __str__(self):
        info = _format_items(
            self.__dict__, keys=self._STR_FIELDS, sep=".", fmt="{value}"
        )
        return f"<{self.__class__.__name__} {info}>"

    def __repr__(self):
        info = _format_items(self.__dict__, keys=self._REPR_FIELDS, sep=", ")
        return f"{self.__class__.__name__}({info})"


class ConfigReply:
    """Config reply.

    Reference https://i3wm.org/docs/ipc.html#_config_reply

    Attributes:
        config (str): The config file as string.
    """

    def __init__(self, d):
        self.config = d.get("config")

    def lines(self):
        """Return the config as lines."""
        return self.config.splitlines()

    def __iter__(self):
        if self.config is None:
            return iter([])
        return iter(self.config.splitlines())

    def __str__(self):
        return "<{self.__class__.__name__}>"

    def __repr__(self):
        return "{self.__class__.__name__}()"


class BarConfigReply:
    """Bar config reply.

    Reference https://i3wm.org/docs/ipc.html#_bar_config_reply

    Attributes:
        id (str): The ID for this bar.
        mode (str): Either dock (the bar sets the dock window type) or hide (the bar
            does not show unless a specific key is pressed).
        position (str): Either bottom or top at the moment.
        status_command (str): Command which will be run to generate a statusline. Each
            line on stdout of this command will be displayed in the bar.
        font (str): The font to use for text on the bar.
        workspace_buttons (bool): Wheter or not workspace buttons are shown.
        binding_mode_indicator (bool): Whether or not the mode indicator is shown.
        verbose (bool): Whether or not the bar has verbose output for debugging enabled.
        colors (dict): Contains key/value pairs of colors. Each value is a color code in
            hex (#rrggbb).
    """

    _STR_FIELDS = ("id",)
    _REPR_FIELDS = ("id",)

    def __init__(self, d):
        self.id = d.get("id")
        self.mode = d.get("mode")
        self.position = d.get("position")
        self.status_command = d.get("status_command")
        self.font = d.get("font")
        self.workspace_buttons = d.get("workspace_buttons")
        self.binding_mode_indicator = d.get("binding_mode_indicator")
        self.verbose = d.get("verbose")
        self.colors = d.get("colors")

    def __str__(self):
        info = _format_items(self.__dict__, keys=self._STR_FIELDS)
        return f"<{self.__class__.__name__} {info}>"

    def __repr__(self):
        info = _format_items(self.__dict__, keys=self._REPR_FIELDS, sep=", ")
        return f"{self.__class__.__name__}({info})"


class ListReply(Sequence):
    """Basic list reply."""

    def __init__(self, reply):
        self._reply = reply

    def __getitem__(self, index):
        return self._reply[index]

    def __len__(self):
        return len(self._reply)

    def __str__(self):
        return f"<{self.__class__.__name__} {self._reply!r}>"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._reply!r})"


class BarsListReply(ListReply):
    """A list of all configured bar IDs.

    Reference https://i3wm.org/docs/ipc.html#_bar_config_reply
    """

    pass


class MarksReply(ListReply):
    """List of all defined marks.

    The order of the list is undefined.

    Reference https://i3wm.org/docs/ipc.html#_marks_reply
    """

    pass


class BindingModesReply(ListReply):
    """List of all defined binding modes.

    Reference https://i3wm.org/docs/ipc.html#_binding_modes_reply
    """

    pass


class BasicReply:
    """Basic reply type for replies with only one success field.
    """

    def __init__(self, d):
        self.success = d.get("success")

    def __str__(self):
        return f"<{self.__class__.__name__} success={self.success!r}>"

    def __repr__(self):
        return f"{self.__class__.__name__}(success={self.success!r})"


class SyncReply(BasicReply):
    """Sync reply.

    Attributes:
        success (bool): Whether or not the command succeeded.

    Reference https://i3wm.org/docs/ipc.html#_sync_reply
    """

    pass


class TickReply(BasicReply):
    """Tick reply.

    Attributes:
        success (bool): Whether or not the command succeeded.

    Reference https://i3wm.org/docs/ipc.html#_tick_reply
    """

    pass


class SubscribeReply(BasicReply):
    """Subscribe reply.

    Attributes:
        success (bool): Whether or not the command succeeded.

    Reference https://i3wm.org/docs/ipc.html#_bar_subscribe_reply
    """

    pass
