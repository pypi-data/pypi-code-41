from asciimatics.widgets import Frame, Layout, Button, CheckBox, Label, \
    Divider, Screen, TextBox, Text
from asciimatics.exceptions import StopApplication
from venv_clean.core.utils import find_virtualenvs, delete_folder


class VenvView(Frame):

    ASCII_TITLE = """
    venv-clean
    Select the environments that
    you want to delete, and press
    the bottom delete button when
    you're ready
    """
    ASCII_TITLE_HEIGHT = 6

    def __init__(self, screen, path):
        super(VenvView, self).__init__(screen,
                                       screen.height,
                                       screen.width,
                                       hover_focus=False,
                                       can_scroll=True,
                                       reduce_cpu=True,
                                       has_border=True)
        self.selected_size = 0
        self.size_found = 0
        self.path = path
        self.venvs = self.__find_venvs(self.path)

        self.set_visual_theme()
        # Top bar, logo & summary
        self.layout_top = Layout([1, 1])
        self.add_layout(self.layout_top)
        logo = TextBox(height=self.ASCII_TITLE_HEIGHT,
                       as_string=True, disabled=True)
        logo.value = self.ASCII_TITLE
        self.layout_top.add_widget(logo, 1)

        self.layout_top.add_widget(Label(''), 0)
        self.layout_top.add_widget(Label('SUMMARY'), 0)
        self.label_size_found = Text('Total: ', disabled=True)
        self.label_size_selected = Text('To Free: ', disabled=True)
        self.layout_top.add_widget(self.label_size_found, 0)
        self.layout_top.add_widget(self.label_size_selected, 0)
        self.__update_sizes()

        # Main list of environments
        self.layout_main = Layout([80, 20], fill_frame=True)
        self.add_layout(self.layout_main)
        self.__draw_list()

        # Bottom buttons
        self.layout_bottom = Layout([1, 1])
        self.add_layout(self.layout_bottom)

        self.layout_bottom.add_widget(Divider(), 0)
        self.layout_bottom.add_widget(Divider(), 1)
        self.layout_bottom.add_widget(Button('Delete', self._delete), 0)
        self.layout_bottom.add_widget(Button('Quit', self._quit), 1)

        self.fix()

    def __draw_list(self):
        self.layout_main.clear_widgets()
        self.layout_main.reset()

        self.layout_main.add_widget(Label('Path found'), 0)
        self.layout_main.add_widget(Label('Size MB'), 1)
        self.layout_main.add_widget(Divider(), 0)
        self.layout_main.add_widget(Divider(), 1)

        for v in self.venvs:
            self.layout_main.add_widget(v['checkbox'], 0)
            self.layout_main.add_widget(Label(str(v['size'])), 1)
        self.fix()

    def __update_sizes(self):
        self.label_size_found.value = '{:.2f}MB'.format(self.size_found)
        self.label_size_selected.value = '{:.2f}MB'.format(self.selected_size)

    def _reload_items(self):
        self.selected_size = 0
        self.size_found= 0

        self.venvs = self.__find_venvs(self.path)
        self.reset()

        self.__draw_list()
        self.__update_sizes()

    def __calculate_selected_size(self):
        self.selected_size = 0
        for v in self.venvs:
            if v['checkbox'].value:
                self.selected_size += float(v['size'])
        self.__update_sizes()

    def _delete(self):
        for v in self.venvs:
            if v['checkbox'].value:
                delete_folder(v['location'])
        self._reload_items()

    @staticmethod
    def _quit():
        raise StopApplication('Bye!')

    def set_visual_theme(self):
        self.set_theme('monochrome')
        frame_items = ('selected_focus_field',
                       'selected_focus_control',
                       'focus_button')
        for key in frame_items:
            self.palette[key] = (Screen.COLOUR_BLACK,
                                 Screen.A_BOLD,
                                 Screen.COLOUR_WHITE)

    def __find_venvs(self, path):
        self.size_found = 0
        venvs = find_virtualenvs(path)
        for v in venvs:
            v['checkbox'] = CheckBox(v['location'],
                                     on_change=self.__calculate_selected_size)
            self.size_found += float(v['size'])
        return venvs
