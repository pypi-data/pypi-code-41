import threading


class _ConvertThread(threading.Thread):
    """
    class for converting each given file_name in a thread and with specified conversion function
    """
    def __init__(self, memory, file, save_to_file, function, **kwargs):
        threading.Thread.__init__(self)
        self.file = file
        self.function = function
        self.setName(file)
        self.memory = memory
        self.save_to_file = save_to_file
        self.kwargs = kwargs
        self.start()

    def run(self):
        self.function(self.file, self.memory if self.memory else False, self.save_to_file, **self.kwargs)


class _FileConversion:
    """
    class for handling the handling of converted files as well as its access without threading problems
    """
    def __init__(self, path, file_type, function, save_to_file, ignore_file_type, **kwargs):
        self.path = path
        _get_files(self, file_type, ignore_file_type)
        self.threads = dict()
        self.lock = threading.Lock()
        self.lock.acquire()
        self.__data = dict()
        for file in self.files:
            self.__data[file] = None
            self.threads[file] = _ConvertThread(memory=self.__data, save_to_file=save_to_file, file=file,
                                                function=function, **kwargs)
        for thread in self.threads:
            self.threads[thread].join()
        self.lock.release()

    @property
    def data(self):
        """
        returns the handling after conversion was finished

        Returns
        -------
        handling : dict
            converted handling as {file_name: converted_data}

        """
        self.lock.acquire()
        self.lock.release()
        if len(self.__data.keys()) == 1:
            return list(self.__data.values())[0]
        return {key[len(key) - len(self.path):]: value for key, value in self.__data.items()}

    @property
    def file_names(self):
        return self.files

    @property
    def absolute_path(self):
        return self._absolute_path


def csv_to_json(path, save_to_file=False, null_value="delete", main_key_position=0, header_line=0, ignore_file_type=False, **kwargs):
    """
    Converts files from csv to json

    Parameters
    ----------
    path : str
        path of files or file_name
    save_to_file : bool
        if handling is supposed to be saved to file_name
    null_value : any
        the value to fill the key if no value in csv file_name. If "delete", key in json not being present
    main_key_position : int
        the position in csv file_name for the main key for this row
    header_line : int
        if the header is not in the first row, select row here. WARNING: all handling above this line will not be parsed
    ignore_file_type : bool
        if the checking for the file_type shall be dismissed

    Returns
    -------
    handling : dict
        dictionary containing the jsons
    """
    from ._converting import _csv_to_json
    if kwargs:
        _register_csv_dialect(**kwargs)

    # converting
    conversion = _FileConversion(path, "csv", _csv_to_json, null_value=null_value, main_key_position=main_key_position,
                                 dialect="custom" if kwargs else None, header_line=header_line,
                                 save_to_file=save_to_file, ignore_file_type=ignore_file_type)

    return conversion.data
