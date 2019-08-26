# -*- coding: utf-8 -*-
"""Background worker module.

contains PSWorker
"""
import importlib as imp
import multiprocessing as mp
import os
import random
import string
import sys
import traceback
from time import sleep, time
from typing import Callable

import matplotlib
import numpy as np
import psutil
from puzzlestream.backend import progressupdate, test
from puzzlestream.backend.dict import PSDict
from puzzlestream.backend.print import Printer
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.streamsection import PSStreamSection


class PSWorker:
    """Background worker class.

    Every Puzzlestream module has exactly one worker that does all the heavy
    lifting in a background process without blocking the UI.
    """

    def __init__(self, workerRegistrationFunction: Callable,
                 startTimerFunction: Callable):
        """Worker init.

        Args:
            workerRegistrationFunction (Callable): Method to enqueue the worker.
            startTimerFunction (Callable): Method to start the polling timer.
        """
        self.__process, self.__conn = None, None
        self.__finished = PSSignal()
        self.__newStdout = PSSignal()
        self.__progressUpdate = PSSignal()
        self.__name, self.__path, self.__libs = None, None, None
        self.__workerRegistration = workerRegistrationFunction
        self.__startTimer = startTimerFunction
        self.__id = None
        self.__queue = mp.Queue()

    def __getstate__(self) -> tuple:
        return (self.__name, self.__path, self.__libs)

    def __setstate__(self, state: tuple):
        self.__name, self.__path, self.__libs = state

    @property
    def finished(self) -> PSSignal:
        """Signal that is emitted when the worker has finished (PSSignal)."""
        return self.__finished

    @property
    def newStdout(self) -> PSSignal:
        """Signal that is emitted when there is new output (PSSignal)."""
        return self.__newStdout

    @property
    def progressUpdate(self) -> PSSignal:
        """Signal that is emitted when progress has changed (PSSignal)."""
        return self.__progressUpdate

    def setName(self, name: str):
        """Set the name of the worker."""
        self.__name = name

    def setPath(self, path: str):
        """Set the worker file path."""
        self.__path = path

    def setLibs(self, libs: list):
        """Pass libs to be made available inside the background process."""
        self.__libs = libs

    def enqueue(self, streamSection: PSStreamSection,
                currentID: int, lastID: int):
        """Enqueue worker to be executed whenever there is a free slot."""
        self.__streamSection = streamSection
        self.__id, self.__lastID = currentID, lastID
        self.__workerRegistration(self.__id, self)
        self.__startTimer()

    def run(self):
        """Run worker in background process."""
        self.__process = mp.Process(
            target=self._calculate,
            args=(self.__queue, self.__streamSection,
                  self.__id, self.__lastID)
        )

        self.__startTimer()
        self.__process.start()

        while not self.__process.is_alive():
            sleep(0.01)

    def __importModule(self):
        """Import and return module that holds the code to be executed."""
        for lib in self.__libs:
            if lib not in sys.path:
                sys.path.append(lib)
        sys.path.append(os.path.abspath(os.path.dirname(self.__path)))
        spec = imp.util.spec_from_file_location(self.__name, self.__path)
        mod = imp.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def poll(self):
        """Poll worker and see if there is new output or if it has finished."""
        if not self.__queue.empty():
            result = self.__queue.get()

            if isinstance(result, str):
                self.newStdout.emit(result)
            elif isinstance(result, float) or isinstance(result, int):
                self.progressUpdate.emit(result)
            else:
                self.finish(result)

    def finish(self, result: list):
        """Run some finalising procedure when the worker has finished."""
        self.__process.join()
        self.__workerRegistration(self.__id, self)
        self.__process = None
        self.finished.emit(*result)

    def _calculate(self, queue: mp.Queue, streamSec: PSStreamSection,
                   currentID: int, lastID: int):
        """Actual background task, run in seperate process.

        Args:
            queue (mp.Queue): Queue to pass data to the main process.
            streamSec (PSStreamSection): Current stream section.
            currentID, lastID (int): Current and previous module IDs.
        """
        printer = Printer(queue)
        sys.stdout, sys.stderr = printer, printer
        progressupdate.queue = queue

        np.random.seed(int.from_bytes(os.urandom(4), "big"))
        runtime, savetime, testResults = 0, 0, {}

        try:
            mod = self.__importModule()
            os.chdir(os.path.dirname(mod.__file__))

            inp = streamSec.data

            t0 = time()
            out = mod.main(inp)
            if not isinstance(out, PSDict):
                raise TypeError(
                    "The module's main function has to return the argument " +
                    "it received (usually 'return stream').")
            runtime = time() - t0
            log = out.changelog

            t0 = time()
            inp.update(out)
            streamSec.updateData(lastID, inp, log, clean=True)
            savetime = time() - t0

            success, output = True, ""

            for func in test.functions:
                result = func(out)

                if isinstance(result, bool):
                    testResults[func.__name__] = result
            del out

        except Exception:
            message = traceback.format_exc()
            success, log, output = False, [], message

        times = [runtime, savetime]

        queue.put(printer.currentStdOut)
        queue.put([success, streamSec.changelog, output, times, testResults])

    def pause(self) -> bool:
        """Pause the current process."""
        if self.__process is not None:
            p = psutil.Process(self.__process.pid)
            p.suspend()
        else:
            return False
        return True

    def resume(self) -> bool:
        """Resume the current process."""
        if self.__process is not None:
            p = psutil.Process(self.__process.pid)
            p.resume()
        else:
            return False
        return True

    def stop(self) -> bool:
        """Terminate the current process."""
        if self.__process is not None:
            self.__process.terminate()
            self.__workerRegistration(self.__id, self)
        else:
            return False
        return True
