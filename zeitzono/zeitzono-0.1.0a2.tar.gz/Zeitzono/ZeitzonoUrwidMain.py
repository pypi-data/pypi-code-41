import urwid
from .ZeitzonoTime import ZeitzonoTime
from .ZeitzonoCities import ZeitzonoCities
from .ZeitzonoUrwidSearch import ZeitzonoUrwidSearch
from .ZeitzonoSearch import ZeitzonoSearch


class ZeitzonoUrwidMain(urwid.WidgetWrap):
    _selectable = True

    def __init__(self, zeitzonowidgetswitcher, cache, version):

        self.zeitzonotime = ZeitzonoTime()
        self.zeitzonocities = ZeitzonoCities()

        # if we are caching, read HoronoCities from cache
        self.cache = cache
        if cache is not None:
            try:
                with open(self.cache) as cachefile:
                    self.zeitzonocities.fromJSON(cachefile)
            except Exception:
                pass

        self.baset = urwid.Text("", wrap="clip", align="left")
        basetmap = urwid.AttrMap(self.baset, "main_base_time")
        self.basezc = urwid.Text("", wrap="clip", align="right")
        basezcmap = urwid.AttrMap(self.basezc, "main_basezc")

        self.basezc_is_c = False
        self.basezc_city = None
        self.baset_update()
        self.basezc_update()

        htext = "zeitzono "
        htext_len = len(htext)
        zeitzono_ut = urwid.Text(htext, wrap="clip", align="right")
        zeitzono_ut_am = urwid.AttrMap(zeitzono_ut, "main_zeitzono")

        self.version = version
        version_len = len(version)
        version_ut = urwid.Text(version, wrap="clip", align="right")
        version_ut_am = urwid.AttrMap(version_ut, "main_version")

        blank = urwid.Text("", align="right")
        versioncols = urwid.Columns(
            [
                ("weight", 99, blank),
                (htext_len, zeitzono_ut_am),
                (version_len, version_ut_am),
            ]
        )

        self.bodypile = urwid.Pile(self.body_gen())

        self.bodyfill = urwid.Filler(self.bodypile, valign="bottom")
        self.zeitzonowidgetswitcher = zeitzonowidgetswitcher

        cols = urwid.Columns([basetmap, basezcmap])
        blankline = urwid.Text("", wrap="clip")

        helpline = "? - help,  c - add cities, Q - quit"
        helpline = urwid.Text(helpline, wrap="clip")
        helpline_attr = urwid.AttrMap(helpline, "main_helpline")

        footer = [blankline, helpline_attr, cols]
        footerpile = urwid.Pile(footer)

        frame = urwid.Frame(
            self.bodyfill, header=versioncols, footer=footerpile
        )
        super().__init__(frame)

    def _list_is_max_capacity(self, fakecap=None):
        cols, rows = urwid.raw_display.Screen().get_cols_rows()
        maxrows = rows - 4
        cap = self.zeitzonocities.numcities()

        if fakecap is not None:
            cap = cap + fakecap - 1

        if cap >= maxrows:
            return True

        return False

    def time_adjust(self, key):  # noqa

        if key in ("S"):
            self.zeitzonotime.sub_sec()
        if key in ("s"):
            self.zeitzonotime.add_sec()
        if key in ("M"):
            self.zeitzonotime.sub_min()
        if key in ("m"):
            self.zeitzonotime.add_min()
        if key in ("H"):
            self.zeitzonotime.sub_hour()
        if key in ("h"):
            self.zeitzonotime.add_hour()
        if key in ("X"):
            self.zeitzonotime.sub_qday()
        if key in ("x"):
            self.zeitzonotime.add_qday()
        if key in ("F"):
            self.zeitzonotime.sub_qhour()
        if key in ("f"):
            self.zeitzonotime.add_qhour()
        if key in ("D"):
            self.zeitzonotime.sub_day()
        if key in ("d"):
            self.zeitzonotime.add_day()
        if key in ("W"):
            self.zeitzonotime.sub_week()
        if key in ("w"):
            self.zeitzonotime.add_week()
        if key in ("O"):
            self.zeitzonotime.sub_month()
        if key in ("o"):
            self.zeitzonotime.add_month()
        if key in ("Y"):
            self.zeitzonotime.sub_year()
        if key in ("y"):
            self.zeitzonotime.add_year()
        if key in ("0"):
            self.zeitzonotime.zero_sec()
            self.zeitzonotime.zero_min()
        if key in ("N"):
            self.zeitzonotime.set_time_now()
        self.body_render()
        self.baset_update()
        return True

    def keypress(self, size, key):  # noqa
        if key.lower() in ("q"):
            # if we are caching, write HoronoCities to cache before exiting
            if self.cache is not None:
                with open(self.cache, "w") as cachefile:
                    self.zeitzonocities.toJSON(cachefile)
            raise urwid.ExitMainLoop()
        if key == ("?"):
            self.zeitzonowidgetswitcher.switch_widget_help_main()
        if key in ("C"):
            self.zeitzonocities.clear()
        if key in ("c") and not self._list_is_max_capacity():
            zeitzonourwidsearch = ZeitzonoUrwidSearch(
                self.zeitzonowidgetswitcher, self.zeitzonocities, self.version
            )
            self.zeitzonowidgetswitcher.set_widget("search", zeitzonourwidsearch)
            self.zeitzonowidgetswitcher.switch_widget_search()
        if key in ("L"):
            self.zeitzonotime.set_tz_local()
            self.basezc_is_c = False
            self.basezc_update()
            return True
        if key in ("p"):
            self.zeitzonocities.del_last()
            self.body_render()
            return True
        if key in ("P"):
            self.zeitzonocities.del_first()
            self.body_render()
            return True
        if key in ("."):
            self.zeitzonocities.rotate_left()
            self.body_render()
            return True
        if key in (","):
            self.zeitzonocities.rotate_right()
            self.body_render()
            return True
        if key in ("/"):
            self.zeitzonocities.roll_2()
            self.body_render()
            return True
        if key in ("'"):
            self.zeitzonocities.roll_3()
            self.body_render()
            return True
        if key in (";"):
            self.zeitzonocities.roll_4()
            self.body_render()
            return True
        if key in ("z"):
            if self.zeitzonocities.numcities() > 0:
                city = self.zeitzonocities.cities[-1]
                self.basezc_is_c = True
                self.basezc_city = city.name
                self.zeitzonotime.set_tz(city.tz)
                self.basezc_update()
            return True
        if key in ("Z"):
            if self.zeitzonocities.numcities() > 0:
                city = self.zeitzonocities.cities[0]
                self.basezc_is_c = True
                self.basezc_city = city.name
                self.zeitzonotime.set_tz(city.tz)
                self.basezc_update()
            return True
        if key in ("r"):
            if self._list_is_max_capacity():
                return True
            zeitzonourwidsearch = ZeitzonoSearch()
            rcities = zeitzonourwidsearch.random1()
            self.zeitzonocities.addcities(rcities)
            self.body_render()
            return True
        if key in ("R"):
            if self._list_is_max_capacity(fakecap=10):
                return True
            zeitzonourwidsearch = ZeitzonoSearch()
            rcities = zeitzonourwidsearch.random10()
            self.zeitzonocities.addcities(rcities)
            self.body_render()
            return True
        self.time_adjust(key)
        self.body_render()

    def baset_update(self):
        newstr = "base time: %s" % self.zeitzonotime.get_time_str()
        self.baset.set_text(newstr)

    def basezc_update(self):
        newstr = "base zone: %s" % str(self.zeitzonotime.get_tz())
        if self.basezc_is_c:
            newstr = "base city: %s" % self.basezc_city
        self.basezc.set_text(newstr)
        self.baset_update()

    def body_gen(self, update=False):

        bodylist = []
        for city in self.zeitzonocities.cities:
            bodytext = str(self.zeitzonotime.get_time_tz_str(city.get_tz()))
            bodytext = bodytext + " "
            bodytext = bodytext + str(city)
            rawtext = urwid.Text(bodytext, wrap="clip", align="left")
            if update:
                content = (rawtext, ("pack", None))
            else:
                content = rawtext
            bodylist.append(content)

        return bodylist

    def body_render(self):
        self.bodypile.contents = self.body_gen(update=True)
