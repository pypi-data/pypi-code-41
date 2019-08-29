from escam_toolbox.ui import *
from escam_toolbox.dicom import *
from tkinter import filedialog


NAME = 'Slice Selector'

VERSION = '1.0.8'  # Should be one patch further than VERSION file

ABOUT = """
{} v{}\n\n
Application for easily selecting and exporting individual slices from many DICOM series. The tool
assumes that each DICOM series is contained in its own sub-directory. If a directory has multiple 
series, the tool will load only the 1st series.\n\n
Author: Ralph Brecheisen, Clinical Data Scientist @ Department of Surgery, Maastricht
University Medical Center, The Netherlands\n
Email: r.brecheisen@maastrichtuniversity.nl
""".format(NAME, VERSION)


class SliceSelector(MainWindow):

    def __init__(self, master):
        super(SliceSelector, self).__init__(master, 'Slice Selector v{}'.format(VERSION), 1000, 800)
        self.add_label(name='min_nr_images_label', text='Minimal nr. images per scan')
        self.add_text_field(name='min_nr_images_field', default='10')
        self.add_button(name='open_dir_button', text='Open directory...', callback=self.open_dir)
        self.add_label(name='level_slider_label', text='Window level')
        self.add_slider(name='level_slider', callback=self.level_changed)
        self.add_label(name='width_slider_label', text='Window width')
        self.add_slider(name='width_slider', callback=self.width_changed)
        self.add_button(name='reset_level_width_button', text='Reset level/width', callback=self.reset_level_width)
        self.add_label(name='select_slice_label', text='Select slice')
        self.add_slider(name='select_slice_slider', callback=self.selected_idx_changed)
        self.add_button(name='prev_slice_button', text='Previous slice (^)', callback=self.prev_slice)
        self.add_button(name='next_slice_button', text='Next slice (v)', callback=self.next_slice)
        self.add_button(name='prev_image_button', text='Previous image (<)', callback=self.prev_image)
        self.add_button(name='next_image_button', text='Next image (>)', callback=self.next_image)
        self.add_button(name='set_target_dir_button', text='Select target directory...', callback=self.open_target_dir)
        self.add_label(name='file_name_format_label', text='Select file name format')
        self.add_combobox(name='file_name_format_cbx', items=[
            'Manually specify file name',
            'Use patient ID',
            'Use patient\'s name',
        ])
        self.add_button(name='save_slice_button', text='Save slice...', callback=self.save_slice)
        self.add_quit_and_about_buttons(ABOUT)
        self.image = None
        self.image_series = None
        self.selected_idx = 0
        self.selected_image = 0
        self.target_dir = None

    def open_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            min_nr_images = int(self.get('min_nr_images_field').get())
            self.image_series = DicomSeries(min_nr_images)
            self.image_series.load_from_directory(directory)
            if self.image_series.nr_images > 0:
                self.image = self.image_series.get(self.selected_image)
                # print(self.image.info())
                self.log_area.log_text(self.image.directory)
                x = self.image.nr_slices - 1
                y = int(x / 2.0)
                self.selected_idx = y
                self.update_select_slice_slider(x, y)
                self.update_level_slider()
                self.update_width_slider()
                self.render_slice(self.selected_idx)

    def open_target_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.target_dir = directory
        else:
            self.target_dir = None

    def level_changed(self, value):
        if self.image:
            self.image.set_window_level(int(value))
            self.render_slice(self.selected_idx)

    def width_changed(self, value):
        if self.image:
            self.image.set_window_width(int(value))
            self.render_slice(self.selected_idx)

    def reset_level_width(self):
        if self.image:
            self.image.reset_window_level_and_width()
            self.update_level_slider()
            self.update_width_slider()
            self.render_slice(self.selected_idx)

    def selected_idx_changed(self, value):
        if self.image:
            self.selected_idx = int(value)
            self.render_slice(self.selected_idx)
            print('selected_idx_changed')

    def update_select_slice_slider(self, x, y):
        self.get('select_slice_slider').configure(from_=0, to=x)
        self.get('select_slice_slider').set(y)

    def update_level_slider(self):
        self.get('level_slider').configure(from_=self.image.hu_min, to=self.image.hu_max)
        self.get('level_slider').set(self.image.window_level)

    def update_width_slider(self):
        self.get('width_slider').configure(from_=self.image.hu_min, to=self.image.hu_max)
        self.get('width_slider').set(self.image.window_width)

    def prev_slice(self):
        self.selected_idx -= 1
        self.selected_idx = max(0, self.selected_idx)
        self.render_slice(self.selected_idx)

    def next_slice(self):
        self.selected_idx += 1
        self.selected_idx = min(self.selected_idx, self.image.nr_slices - 1)
        self.render_slice(self.selected_idx)

    def prev_image(self):
        if self.image:
            self.selected_image -= 1
            self.selected_image = max(0, self.selected_image)
            self.image = self.image_series.get(self.selected_image)
            self.log_area.log_text(self.image.directory)
            self.update_level_slider()
            self.update_width_slider()
            self.update_select_slice_slider_and_render_image()

    def next_image(self):
        if self.image:
            self.selected_image += 1
            self.selected_image = min(self.selected_image, self.image_series.nr_images - 1)
            self.image = self.image_series.get(self.selected_image)
            self.log_area.log_text(self.image.directory)
            self.update_level_slider()
            self.update_width_slider()
            self.update_select_slice_slider_and_render_image()

    def update_select_slice_slider_and_render_image(self):
        if self.image:
            x = self.image.nr_slices - 1
            y = int(x / 2.0)
            self.get('select_slice_slider').configure(to=x)
            self.get('select_slice_slider').set(y)
            self.selected_idx = y
            self.render_slice(self.selected_idx)

    def render_slice(self, idx):
        if self.image:
            self.get('select_slice_slider').set(idx)
            self.main_area.set_image(self.image.get_slice_as_image(idx))

    def save_slice(self):
        if not self.target_dir:
            self.show_msg('Select target directory first!')
        if not self.image:
            self.show_msg('Load and select image first!')
        file_name = None
        current_text = self.get('file_name_format_cbx').get()
        if current_text == 'Use patient ID':
            file_name = '{}.dcm'.format(self.image.patient_id)
        elif current_text == 'Use patient\'s name':
            file_name = '{}.dcm'.format(self.image.patient_name)
        else:
            pass
        if not file_name:
            file_name = filedialog.asksaveasfilename(initialdir=self.target_dir)
            if not file_name:
                self.show_msg('You must manually specify a file name or choose a different format option')
                return
            else:
                if not file_name.endswith('.dcm'):
                    file_name = file_name + '.dcm'
        file_path = os.path.join(self.target_dir, file_name)
        self.image.save_slice_as(self.selected_idx, file_path)
        self.show_msg('Saved slice {} to file {}'.format(self.selected_idx, file_path))

    # TODO: Add key events!
    def on_key_press(self, event):
        if event.keysym == 'Right':
            self.next_image()
        elif event.keysym == 'Left':
            self.prev_image()
        elif event.keysym == 'Up':
            self.prev_slice()
        elif event.keysym == 'Down':
            self.next_slice()
        else:
            pass


def main():
    root = tk.Tk()
    SliceSelector(root)
    root.mainloop()


if __name__ == '__main__':
    main()
