import collections


def format_attribute(name, value):
    if name == 'damping': name = 'Damping'
    elif name == 'k': name = 'K'
    elif name == 'url': name = 'URL"'
    value = f'"{value}"' if isinstance(value, str) else str(value)
    return f'{name}={value};'


class DotObject:
    _ATTRIBUTES = tuple()

    def __init__(self, *args, **kwargs):
        self._attributes = {}
        for i in self._ATTRIBUTES:
            self._attributes[i] = kwargs.get(i, None)

    @property
    def is_containable(self):
        return False

    @property
    def is_contained(self):
        return False

    @property
    def is_container(self):
        return False

    @property
    def attributes(self):
        return self._attributes.copy()

    def render_attributes(self):
        result = []
        for i in self._ATTRIBUTES:
            if self._attributes[i] is not None:
                result.append(format_attribute(i, self._attributes[i]))
        return ' '.join(result)


class ContainerMixin(collections.abc.MutableSequence):
    def __init__(self, *args, **kwargs):
        self._items = []
        for item in args:
            try:
                if item.is_containable:
                    self.append(item)
            except AttributeError:
                pass

    @staticmethod
    def _check_item(item):
        try:
            if item.is_containable:
                return item
        except AttributeError:
            pass
        raise ValueError("Not a containable item")

    def __getitem__(self, item):
        return self._items[item]

    def __setitem__(self, key, value):
        self._items[key] = self._check_item(value)

    def __delitem__(self, key):
        del self._items[key]

    def __len__(self):
        return len(self._items)

    def insert(self, index, value):
        self._items.insert(index, self._check_item(value))

    @property
    def is_container(self):
        return True


class ContainedMixin:
    def __init__(self, *args, **kwargs):
        self._container = None

    @property
    def is_containable(self):
        return True

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container):
        if self._container is not None:
            raise Exception("Already in a container")
        if not container.is_container:
            raise Exception("Not a container")
        self._container = container


class Graph(ContainerMixin, DotObject):
    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)


class ContainableGraph(ContainedMixin, Graph):
    def __init__(self, *args, **kwargs):
        super(ContainableGraph, self).__init__(*args, **kwargs)


class SubGraph(ContainableGraph):
    _ATTRIBUTES = ("rank",)

    def __init__(self, *items, rank=None, **kwargs):
        if len(items) > 0 and isinstance(items[0], Graph):
            # if the first argument is a Graph, just do a cast
            g = items[0]
            items = g[:]
            extended_kwargs = g.attributes
        else:
            extended_kwargs = kwargs.copy()
            if rank is not None:
                extended_kwargs["rank"] = rank
        super(SubGraph, self).__init__(*items, **extended_kwargs)


class Cluster(ContainableGraph):
    _ATTRIBUTES = (
        "k",
        "url",
        "area",
        "bgcolor",
        "color",
        "colorscheme",
        "fillcolor",
        "fontcolor",
        "fontname",
        "fontsize",
        "gradientangle",
        "href",
        "id",
        "label",
        "labeljust",
        "labelloc",
        "layer",
        "lheight",
        "lp",
        "lwidth",
        "margin",
        "nojustify",
        "pencolor",
        "penwidth",
        "peripheries",
        "sortv",
        "style",
        "target",
        "tooltip",
    )

    def __init__(
        self,
        *items,
        k=None,
        url=None,
        area=None,
        bgcolor=None,
        color=None,
        colorscheme=None,
        fillcolor=None,
        fontcolor=None,
        fontname=None,
        fontsize=None,
        gradientangle=None,
        href=None,
        id=None,
        label=None,
        labeljust=None,
        labelloc=None,
        layer=None,
        lheight=None,
        lp=None,
        lwidth=None,
        margin=None,
        nojustify=None,
        pencolor=None,
        penwidth=None,
        peripheries=None,
        sortv=None,
        style=None,
        target=None,
        tooltip=None,
        **kwargs
    ):
        if len(items) > 0 and isinstance(items[0], Graph):
            # if the first argument is a Graph, just do a cast
            g = items[0]
            items = g[:]
            extended_kwargs = g.attributes
        else:
            extended_kwargs = kwargs.copy()
            if k is not None:
                extended_kwargs["k"] = k
            if url is not None:
                extended_kwargs["url"] = url
            if area is not None:
                extended_kwargs["area"] = area
            if bgcolor is not None:
                extended_kwargs["bgcolor"] = bgcolor
            if color is not None:
                extended_kwargs["color"] = color
            if colorscheme is not None:
                extended_kwargs["colorscheme"] = colorscheme
            if fillcolor is not None:
                extended_kwargs["fillcolor"] = fillcolor
            if fontcolor is not None:
                extended_kwargs["fontcolor"] = fontcolor
            if fontname is not None:
                extended_kwargs["fontname"] = fontname
            if fontsize is not None:
                extended_kwargs["fontsize"] = fontsize
            if gradientangle is not None:
                extended_kwargs["gradientangle"] = gradientangle
            if href is not None:
                extended_kwargs["href"] = href
            if id is not None:
                extended_kwargs["id"] = id
            if label is not None:
                extended_kwargs["label"] = label
            if labeljust is not None:
                extended_kwargs["labeljust"] = labeljust
            if labelloc is not None:
                extended_kwargs["labelloc"] = labelloc
            if layer is not None:
                extended_kwargs["layer"] = layer
            if lheight is not None:
                extended_kwargs["lheight"] = lheight
            if lp is not None:
                extended_kwargs["lp"] = lp
            if lwidth is not None:
                extended_kwargs["lwidth"] = lwidth
            if margin is not None:
                extended_kwargs["margin"] = margin
            if nojustify is not None:
                extended_kwargs["nojustify"] = nojustify
            if pencolor is not None:
                extended_kwargs["pencolor"] = pencolor
            if penwidth is not None:
                extended_kwargs["penwidth"] = penwidth
            if peripheries is not None:
                extended_kwargs["peripheries"] = peripheries
            if sortv is not None:
                extended_kwargs["sortv"] = sortv
            if style is not None:
                extended_kwargs["style"] = style
            if target is not None:
                extended_kwargs["target"] = target
            if tooltip is not None:
                extended_kwargs["tooltip"] = tooltip
        super(Cluster, self).__init__(*items, **extended_kwargs)


class RootGraph(Graph):
    _ATTRIBUTES = (
        "damping",
        "k",
        "url",
        "background",
        "bb",
        "bgcolor",
        "center",
        "charset",
        "clusterrank",
        "colorscheme",
        "comment",
        "compound",
        "concentrate",
        "defaultdist",
        "dim",
        "dimen",
        "diredgeconstraints",
        "dpi",
        "epsilon",
        "esep",
        "fontcolor",
        "fontname",
        "fontnames",
        "fontpath",
        "forcelabels",
        "gradientangle",
        "href",
        "id",
        "imagepath",
        "inputscale",
        "label",
        "label_scheme",
        "labeljust",
        "labelloc",
        "landscape",
        "layerlistsep",
        "layers",
        "layerselect",
        "layersep",
        "layout",
        "levels",
        "levelsgap",
        "lheight",
        "lp",
        "lwidth",
        "margin",
        "maxiter",
        "mclimit",
        "mindist",
        "mode",
        "model",
        "mosek",
        "newrank",
        "nodesep",
        "nojustify",
        "normalize",
        "notranslate",
        "nslimit",
        "ordering",
        "orientation",
        "outputorder",
        "overlap",
        "overlap_scaling",
        "overlap_shrink",
        "pack",
        "packmode",
        "pad",
        "page",
        "pagedir",
        "quadtree",
        "quantum",
        "rankdir",
        "ranksep",
        "ratio",
        "remincross",
        "repulsiveforce",
        "resolution",
        "root",
        "rotate",
        "rotation",
        "scale",
        "searchsize",
        "sep",
        "showboxes",
        "size",
        "smoothing",
        "sortv",
        "splines",
        "start",
        "style",
        "stylesheet",
        "target",
        "truecolor",
        "viewport",
        "voro_margin",
        "xdotversion",
    )

    def __init__(
        self,
        *items,
        damping=None,
        k=None,
        url=None,
        background=None,
        bb=None,
        bgcolor=None,
        center=None,
        charset=None,
        clusterrank=None,
        colorscheme=None,
        comment=None,
        compound=None,
        concentrate=None,
        defaultdist=None,
        dim=None,
        dimen=None,
        diredgeconstraints=None,
        dpi=None,
        epsilon=None,
        esep=None,
        fontcolor=None,
        fontname=None,
        fontnames=None,
        fontpath=None,
        forcelabels=None,
        gradientangle=None,
        href=None,
        id=None,
        imagepath=None,
        inputscale=None,
        label=None,
        label_scheme=None,
        labeljust=None,
        labelloc=None,
        landscape=None,
        layerlistsep=None,
        layers=None,
        layerselect=None,
        layersep=None,
        layout=None,
        levels=None,
        levelsgap=None,
        lheight=None,
        lp=None,
        lwidth=None,
        margin=None,
        maxiter=None,
        mclimit=None,
        mindist=None,
        mode=None,
        model=None,
        mosek=None,
        newrank=None,
        nodesep=None,
        nojustify=None,
        normalize=None,
        notranslate=None,
        nslimit=None,
        ordering=None,
        orientation=None,
        outputorder=None,
        overlap=None,
        overlap_scaling=None,
        overlap_shrink=None,
        pack=None,
        packmode=None,
        pad=None,
        page=None,
        pagedir=None,
        quadtree=None,
        quantum=None,
        rankdir=None,
        ranksep=None,
        ratio=None,
        remincross=None,
        repulsiveforce=None,
        resolution=None,
        root=None,
        rotate=None,
        rotation=None,
        scale=None,
        searchsize=None,
        sep=None,
        showboxes=None,
        size=None,
        smoothing=None,
        sortv=None,
        splines=None,
        start=None,
        style=None,
        stylesheet=None,
        target=None,
        truecolor=None,
        viewport=None,
        voro_margin=None,
        xdotversion=None,
        **kwargs
    ):
        if len(items) > 0 and isinstance(items[0], Graph):
            # if the first argument is a Graph, just do a cast
            g = items[0]
            items = g[:]
            extended_kwargs = g.attributes
        else:
            extended_kwargs = kwargs.copy()
            if damping is not None:
                extended_kwargs["damping"] = damping
            if k is not None:
                extended_kwargs["k"] = k
            if url is not None:
                extended_kwargs["url"] = url
            if background is not None:
                extended_kwargs["background"] = background
            if bb is not None:
                extended_kwargs["bb"] = bb
            if bgcolor is not None:
                extended_kwargs["bgcolor"] = bgcolor
            if center is not None:
                extended_kwargs["center"] = center
            if charset is not None:
                extended_kwargs["charset"] = charset
            if clusterrank is not None:
                extended_kwargs["clusterrank"] = clusterrank
            if colorscheme is not None:
                extended_kwargs["colorscheme"] = colorscheme
            if comment is not None:
                extended_kwargs["comment"] = comment
            if compound is not None:
                extended_kwargs["compound"] = compound
            if concentrate is not None:
                extended_kwargs["concentrate"] = concentrate
            if defaultdist is not None:
                extended_kwargs["defaultdist"] = defaultdist
            if dim is not None:
                extended_kwargs["dim"] = dim
            if dimen is not None:
                extended_kwargs["dimen"] = dimen
            if diredgeconstraints is not None:
                extended_kwargs["diredgeconstraints"] = diredgeconstraints
            if dpi is not None:
                extended_kwargs["dpi"] = dpi
            if epsilon is not None:
                extended_kwargs["epsilon"] = epsilon
            if esep is not None:
                extended_kwargs["esep"] = esep
            if fontcolor is not None:
                extended_kwargs["fontcolor"] = fontcolor
            if fontname is not None:
                extended_kwargs["fontname"] = fontname
            if fontnames is not None:
                extended_kwargs["fontnames"] = fontnames
            if fontpath is not None:
                extended_kwargs["fontpath"] = fontpath
            if forcelabels is not None:
                extended_kwargs["forcelabels"] = forcelabels
            if gradientangle is not None:
                extended_kwargs["gradientangle"] = gradientangle
            if href is not None:
                extended_kwargs["href"] = href
            if id is not None:
                extended_kwargs["id"] = id
            if imagepath is not None:
                extended_kwargs["imagepath"] = imagepath
            if inputscale is not None:
                extended_kwargs["inputscale"] = inputscale
            if label is not None:
                extended_kwargs["label"] = label
            if label_scheme is not None:
                extended_kwargs["label_scheme"] = label_scheme
            if labeljust is not None:
                extended_kwargs["labeljust"] = labeljust
            if labelloc is not None:
                extended_kwargs["labelloc"] = labelloc
            if landscape is not None:
                extended_kwargs["landscape"] = landscape
            if layerlistsep is not None:
                extended_kwargs["layerlistsep"] = layerlistsep
            if layers is not None:
                extended_kwargs["layers"] = layers
            if layerselect is not None:
                extended_kwargs["layerselect"] = layerselect
            if layersep is not None:
                extended_kwargs["layersep"] = layersep
            if layout is not None:
                extended_kwargs["layout"] = layout
            if levels is not None:
                extended_kwargs["levels"] = levels
            if levelsgap is not None:
                extended_kwargs["levelsgap"] = levelsgap
            if lheight is not None:
                extended_kwargs["lheight"] = lheight
            if lp is not None:
                extended_kwargs["lp"] = lp
            if lwidth is not None:
                extended_kwargs["lwidth"] = lwidth
            if margin is not None:
                extended_kwargs["margin"] = margin
            if maxiter is not None:
                extended_kwargs["maxiter"] = maxiter
            if mclimit is not None:
                extended_kwargs["mclimit"] = mclimit
            if mindist is not None:
                extended_kwargs["mindist"] = mindist
            if mode is not None:
                extended_kwargs["mode"] = mode
            if model is not None:
                extended_kwargs["model"] = model
            if mosek is not None:
                extended_kwargs["mosek"] = mosek
            if newrank is not None:
                extended_kwargs["newrank"] = newrank
            if nodesep is not None:
                extended_kwargs["nodesep"] = nodesep
            if nojustify is not None:
                extended_kwargs["nojustify"] = nojustify
            if normalize is not None:
                extended_kwargs["normalize"] = normalize
            if notranslate is not None:
                extended_kwargs["notranslate"] = notranslate
            if nslimit is not None:
                extended_kwargs["nslimit"] = nslimit
            if ordering is not None:
                extended_kwargs["ordering"] = ordering
            if orientation is not None:
                extended_kwargs["orientation"] = orientation
            if outputorder is not None:
                extended_kwargs["outputorder"] = outputorder
            if overlap is not None:
                extended_kwargs["overlap"] = overlap
            if overlap_scaling is not None:
                extended_kwargs["overlap_scaling"] = overlap_scaling
            if overlap_shrink is not None:
                extended_kwargs["overlap_shrink"] = overlap_shrink
            if pack is not None:
                extended_kwargs["pack"] = pack
            if packmode is not None:
                extended_kwargs["packmode"] = packmode
            if pad is not None:
                extended_kwargs["pad"] = pad
            if page is not None:
                extended_kwargs["page"] = page
            if pagedir is not None:
                extended_kwargs["pagedir"] = pagedir
            if quadtree is not None:
                extended_kwargs["quadtree"] = quadtree
            if quantum is not None:
                extended_kwargs["quantum"] = quantum
            if rankdir is not None:
                extended_kwargs["rankdir"] = rankdir
            if ranksep is not None:
                extended_kwargs["ranksep"] = ranksep
            if ratio is not None:
                extended_kwargs["ratio"] = ratio
            if remincross is not None:
                extended_kwargs["remincross"] = remincross
            if repulsiveforce is not None:
                extended_kwargs["repulsiveforce"] = repulsiveforce
            if resolution is not None:
                extended_kwargs["resolution"] = resolution
            if root is not None:
                extended_kwargs["root"] = root
            if rotate is not None:
                extended_kwargs["rotate"] = rotate
            if rotation is not None:
                extended_kwargs["rotation"] = rotation
            if scale is not None:
                extended_kwargs["scale"] = scale
            if searchsize is not None:
                extended_kwargs["searchsize"] = searchsize
            if sep is not None:
                extended_kwargs["sep"] = sep
            if showboxes is not None:
                extended_kwargs["showboxes"] = showboxes
            if size is not None:
                extended_kwargs["size"] = size
            if smoothing is not None:
                extended_kwargs["smoothing"] = smoothing
            if sortv is not None:
                extended_kwargs["sortv"] = sortv
            if splines is not None:
                extended_kwargs["splines"] = splines
            if start is not None:
                extended_kwargs["start"] = start
            if style is not None:
                extended_kwargs["style"] = style
            if stylesheet is not None:
                extended_kwargs["stylesheet"] = stylesheet
            if target is not None:
                extended_kwargs["target"] = target
            if truecolor is not None:
                extended_kwargs["truecolor"] = truecolor
            if viewport is not None:
                extended_kwargs["viewport"] = viewport
            if voro_margin is not None:
                extended_kwargs["voro_margin"] = voro_margin
            if xdotversion is not None:
                extended_kwargs["xdotversion"] = xdotversion
        super(RootGraph, self).__init__(*items, **extended_kwargs)
