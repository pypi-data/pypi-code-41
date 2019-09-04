from sorting_algorithm_visual.sorting_algorithms import InsertionSort, RandomSort

class Visualizer:
    def __init__(self, algorithm_dict, draw_factors=(.8, .8)):
        self.canvas = document.getElementById('canvas')
        self.context = self.canvas.getContext('2d')
        self.canvas.addEventListener('click', self.toggle_sorting)
        self.set_events()

        self.width = window.innerWidth
        self.height = window.innerHeight

        self.width_factor, self.height_factor = draw_factors

        self.algorithm_dict = algorithm_dict
        self.sorting_algorithm = self.algorithm_dict[document.getElementById('dropDownButton').innerHTML]
        self.sort_generator = self.sorting_algorithm.sort()

        self.is_sorting = False
        self.interval = 1
        self.swap1, self.swap2 = None, None

    def set_events(self):
        document.getElementById("drop1").addEventListener('click', self.change_text)
        document.getElementById("drop2").addEventListener('click', self.change_text)

    def change_text(self, event):
        document.getElementById('dropDownButton').innerHTML = event.target.text

        self.sorting_algorithm = self.algorithm_dict[event.target.text]
        self.sort_generator = self.sorting_algorithm.sort()

    def resizeCanvas(self):
        self.canvas.width, self.canvas.height = window.innerWidth, window.innerHeight

    def toggle_sorting(self, event):
        self.is_sorting = not self.is_sorting

    @staticmethod
    def generate_array(size):
        return [random.randrange(0, 100) for _ in range(size)]

    def draw(self):
        print(self.sorting_algorithm)
        self.resizeCanvas()

        size_slider = int(document.getElementById('sliderRangeSize').value)
        speed_slider = int(document.getElementById('sliderRangeSpeed').value)

        width, height = window.innerWidth, window.innerHeight
        element_width = (self.width * self.width_factor) / len(self.sorting_algorithm.array)

        if self.is_sorting:
            interval = 100 - speed_slider
            self.swap1, self.swap2 = next(self.sort_generator)
        else:
            interval = 1
            self.swap1, self.swap2 = None, None
            if len(self.sorting_algorithm.array) != size_slider:
                new_array = Visualizer.generate_array(size_slider)
                for key in self.algorithm_dict.keys():
                    print(key)
                    self.algorithm_dict[key].array = new_array
                self.sort_generator = self.sorting_algorithm.sort()

        for index, value in enumerate(self.sorting_algorithm.array):
            element_height = (value * self.height * self.height_factor) / max(self.sorting_algorithm.array)
            if None not in (self.swap1, self.swap2) and (index == self.swap1 or index == self.swap2):
                self.context.fillStyle = '#fc3d03'
            else:
                self.context.fillStyle = '#03bafc'
            self.context.fillRect(
                (width / 2 - (len(self.sorting_algorithm.array) / 2 * element_width)) + (element_width * index), height,
                element_width, -element_height)
            self.context.stroke()

        window.setTimeout(self.draw, interval)


initial_array = Visualizer.generate_array(100)
sorting_algorithms = {'Insertion Sort': InsertionSort(initial_array), 'Random Sort': RandomSort(initial_array)}
visualizer = Visualizer(sorting_algorithms)

window.setTimeout(visualizer.draw, 1)