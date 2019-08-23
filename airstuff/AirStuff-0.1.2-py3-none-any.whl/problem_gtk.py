import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import threading
import queue
import logging
import time
logging.basicConfig(level=logging.DEBUG)


class Producer(threading.Thread):
    def __init__(self, input_queue, step, stop_event=None):
        super(Producer, self).__init__()
        self.step = step
        self.input_queue = input_queue
        self.stop_event = stop_event

    def run(self):
        i = 0
        while self.stop_event is None or not self.stop_event.is_set():
            if not self.input_queue.full():
                self.input_queue.put(i)
                i += self.step


class WorkerConsumer(threading.Thread):
    def __init__(self, input_queue, output_queue, stop_event=None):
        super(WorkerConsumer, self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_event = stop_event

    def run(self):
        while self.stop_event is not None and not self.stop_event.is_set():
            #time.sleep(0.001)
            item = self.input_queue.get()
            self.output_queue.put(item ** 0.5)
            self.input_queue.task_done()


class CallBackConsumer(threading.Thread):
    def __init__(self, input_queue, callback, stop_event=None):
        super(CallBackConsumer, self).__init__()
        self.callback = callback
        self.input_queue = input_queue
        self.stop_event = stop_event

    def run(self):
        while True:
            if not self.input_queue.empty():
                item = self.input_queue.get()
                self.callback(item)
                self.input_queue.task_done()
            if self.stop_event is not None and self.stop_event.is_set() and self.input_queue.empty():
                break


class MyWindow(Gtk.Window):

    lock = threading.Lock()

    def __init__(self):
        Gtk.Window.__init__(self, title="Air Stuff")

        main_box = Gtk.Box()
        self.add(main_box)
        self.entry = Gtk.Entry()
        main_box.pack_start(self.entry, True, True, 0)

        start_button = Gtk.Button(label='start')
        stop_button = Gtk.Button(label='stop')
        main_box.pack_start(start_button, True, True, 0)
        main_box.pack_start(stop_button, True, True, 0)

        start_button.connect('clicked', self.start)
        stop_button.connect('clicked', self.stop)

    def start(self, widget):
        logging.debug('start')

        def callback(x):
            with self.lock:
                #self.entry.set_text(str(x))
                GLib.idle_add(self.entry.set_text, str(x))

        self.input_queue = queue.Queue(10)
        self.output_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.producer = Producer(self.input_queue, 2, self.stop_event)
        self.producer.start()
        self.consumer = WorkerConsumer(self.input_queue, self.output_queue, self.stop_event)
        self.callback_worker = CallBackConsumer(self.output_queue, callback, self.stop_event)
        self.callback_worker.start()
        self.consumer.start()

    def stop(self, widget):
        logging.debug('stop')
        self.stop_event.set()
        self.producer.join()
        self.consumer.join()


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
