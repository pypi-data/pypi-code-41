from rbfExcel.reader import ExcelReader
from rbfExcel.utils import BoolFormat, DateFormat, NumberFormat
from rbfExcel.writer import ExcelWriter


class ExcelLibrary(object):

    def __init__(self, date_format=DateFormat(), number_format=NumberFormat(), bool_format=BoolFormat()):
        """
        Init Excel Keyword with some default configuration.

        Excel Date Time format
        https://support.office.com/en-us/article/format-numbers-as-dates-or-times-418bd3fe-0577-47c8-8caa-b4d30c528309
        """
        self.date_format = date_format
        self.number_format = number_format
        self.bool_format = bool_format
        self.reader = None
        self.writer = None

    def open_excel(self, file_path):
        """
        *Opens the Excel file to read from the path provided in the file path parameter.*

        *Arguments*
        
        ``file_path`` : The Excel file name or path will be opened. If file name then opening file in current directory.
        
        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |

        """
        self.reader = ExcelReader(file_path, self.date_format, self.number_format, self.bool_format)

    def open_excel_to_write(self, file_path, new_path=None, override=False):
        """
        *Opens the Excel file to write from the path provided in the file name parameter.*
        
        In case `New Path` is given, new file will be created based on content of current file.

        *Arguments*
        
        ``file_path`` : The Excel file name or path will be opened. If file name then opening file in current directory.
        
        ``new_path`` : New path will be saved
        
        ``override`` : Default is False. If `True`, new file will be overriden if it exists.
        
        *Examples*

        | `Open Excel To Write`       |  ${CURDIR}/rbfExcelTest.xls  |

        """
        self.writer = ExcelWriter(file_path, new_path, override, self.date_format, self.number_format, self.bool_format)

    def get_sheet_names(self):
        """
        *Returns the names of all the worksheets in the current workbook.*

        *Examples*

        | `Open Excel`              |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Sheet Names`        |                                                    |

        """
        return self.reader.get_sheet_names()

    def get_number_of_sheets(self):
        """
        *Returns the number of worksheets in the current workbook.*

        *Examples*

        | `Open Excel`              |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Number Of Sheets`    |                                                    |

        """
        return self.reader.get_number_of_sheets()

    def get_column_count(self, sheet_name):
        """
        *Returns the specific number of columns of the sheet name specified.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the column count will be returned from
        
                
        *Examples*

        | `Open Excel`          |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Column Count`    |  Sheet1                                        |

        """
        return self.reader.get_column_count(sheet_name)

    def get_row_count(self, sheet_name):
        """
        *Returns the specific number of rows of the sheet name specified.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the column count will be returned from
        
        *Examples*

        | `Open Excel`          |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Row Count`       |  Sheet1                                        |

        """
        return self.reader.get_row_count(sheet_name)

    def get_column_values(self, sheet_name, column, include_empty_cells=True):
        """
        *Returns the specific column values of the sheet name specified.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the column count will be returned from
        
        ``column`` (int) : The column integer value is indicated to get values.
        
        ``include_empty_cells`` : Default is True. If `False` then only return cells with values. 
        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |   |
        | `Get Column Values`    |  Sheet1                                        | 0 |

        """
        return self.reader.get_column_values(sheet_name, column, include_empty_cells)

    def get_row_values(self, sheet_name, row, include_empty_cells=True):
        """
        *Returns the specific row values of the sheet name specified.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the column count will be returned from
        
        ``row`` (int) : The row integer value is indicated to get values.
        
        ``include_empty_cells`` : Default is True. If `False` then only return cells with values. 
        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |   |
        | `Get Row Values`       |  Sheet1                                        | 0 |

        """
        return self.reader.get_row_values(sheet_name, row, include_empty_cells)

    def get_sheet_values(self, sheet_name, include_empty_cells=True):
        """
        *Returns the values from the sheet name specified.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the column count will be returned from
        
        ``include_empty_cells`` : Default is True. If `False` then only return cells with values.
        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Sheet Values`     |  Sheet1 |

        """
        return self.reader.get_sheet_values(sheet_name, include_empty_cells)

    def get_workbook_values(self, include_empty_cells=True):
        """
        *Returns the values from each sheet of the current workbook.*

        *Arguments*
        
        ``include_empty_cells`` : Default is True. If `False` then only return cells with values.
        
        *Examples*
        
        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |
        | `Get Workbook Values`  |                                                    |

        """
        return self.reader.get_workbook_values(include_empty_cells)

    def read_cell_data_by_name(self, sheet_name, cell_name, data_type=None, use_format=True):
        """
        *Uses the cell name to return the data from that cell.*

        - `Data Type` indicates explicit data type to convert cell value to correct data type.
        - `Use Format` is False, then cell value will be raw data with correct data type.

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell value will be returned from.
        
        ``cell_name`` (String) : The selected cell name that the value will be returned from.
        
        ``data_type`` (String) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL
        
        ``use_format`` (boolean) : Default is True. Use format to convert data to string
        
      
        *Examples*

        | `Open Excel`                |  ${CURDIR}/rbfExcelTest.xls  |      |
        | `Read Cell Data By Name`    |  Sheet1                                        |  A2  |

        """
        return self.reader.read_cell_data_by_name(sheet_name, cell_name, data_type, use_format)

    
    def read_cell_data_by_row_and_column_header(self, sheet_name, row_header, column_header, data_type=None, use_format=True):
        """
        *Uses the row header name and column header name to return the data from the corresponding cell.*

        - `Data Type` indicates explicit data type to convert cell value to correct data type.
        - `Use Format` is False, then cell value will be raw data with correct data type.

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell value will be returned from.
        
        ``row_header`` (String) : Row Headers are usually defined in the first column of the excel sheet
		
		``column_header`` (String) : Column Headers are usually defined in the first row of the excel sheet
        
        ``data_type`` (String) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL
        
        ``use_format`` (boolean) : Default is True. Use format to convert data to string
        
      
        *Examples*

        | `Open Excel`                |  ${CURDIR}/rbfExcelTest.xls  |      |
        | ${value} | `Read Cell Data By Row And Column Header`    |  Sheet1 |  rowheadername  | columnheadername | 
        """
        return self.reader.read_cell_data_by_row_and_column_header(sheet_name, row_header, column_header, data_type, use_format)
		
    def read_cell_data(self, sheet_name, column, row, data_type=None, use_format=True):
        """
        *Uses the column and row to return the data from that cell.*

        - `Data Type` indicates explicit data type to convert cell value to correct data type.
        - `Use Format` is False, then cell value will be raw data with correct data type.
        
        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell value will be returned from.
        
        ``column`` (int) : The column integer value that the cell value will be returned from.
        
        ``row`` (int) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL
        
        ``data_type`` (String) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL
        
        ``use_format`` (boolean) : Default is True. Use format to convert data to string

        *Examples*

        | `Open Excel`        |  ${CURDIR}/rbfExcelTest.xls  |   |   |
        | `Read Cell Data`    |  Sheet1                                        | 0 | 0 |

        """
        return self.reader.read_cell_data(sheet_name, column, row, data_type, use_format)

    def check_cell_type(self, sheet_name, column, row, data_type):
        """
        *Checks the type of value that is within the cell of the sheet name selected.*

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell value will be returned from.
        
        ``column`` (int) : The column integer value that the cell value will be returned from.
        
        ``row`` (int) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL
        
        ``data_type`` (String) : Available options: DATE , TIME , DATE_TIME , TEXT , NUMBER , BOOL , EMPTY , ERROR
        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |   |   |       |
        | `Check Cell Type`      |  Sheet1                                        | 0 | 0 | DATE  |

        """
        return self.reader.check_cell_type(sheet_name, column, row, data_type)

    def write_to_cell_by_name(self, sheet_name, cell_name, value, data_type=None):
        """
        *Write data to cell by using the given sheet name and the given cell that defines by name.*

        If `Data Type` is not provided, `rbfExcel` will introspect data type from given `value` to define cell type

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell value will be returned from.
        
        ``cell_name`` (String) : The selected cell name that the value will be returned from.
        
        ``value`` String|number|datetime|boolean) : Raw value or string value then using DataType to decide data type to write
        
        ``data_type`` (String) : Available options: DATE , TIME , DATE_TIME , TEXT , NUMBER , BOOL
        
        *Examples*

        | `Open Excel`            |  ${CURDIR}/rbfExcelTest.xls  |                      |       |
        | `Write To Cell By Name` |  Sheet1                                        |  A1  |  34           |       |
        | `Write To Cell By Name` |  Sheet1                                        |  A2  |  2018-03-29   | DATE  |
        | `Write To Cell By Name` |  Sheet1                                        |  A3  |  YES          | BOOL  |

        """
        self.writer.write_to_cell_by_name(sheet_name, cell_name, value, data_type)

    def write_to_cell_by_row_and_column_header(self, sheet_name, row_header, column_header, value, data_type=None):
        """
        *Uses the row header name and column header name to write the data to the corresponding cell.*

        - `Data Type` indicates explicit data type to convert cell value to correct data type.
        - `Use Format` is False, then cell value will be raw data with correct data type.

        *Arguments*

        ``sheet_name`` (String) : The selected sheet that the cell value will be written to.

        ``row_header`` (String) : Row Headers are usually defined in the first column of the excel sheet

        ``column_header`` (String) : Column Headers are usually defined in the first row of the excel sheet

        ``value`` String|number|datetime|boolean) : Raw value or string value then using DataType to decide data type to write

        ``data_type`` (String) : Available options: TEXT , DATE , TIME , DATETIME , NUMBER , BOOL


        *Examples*

        | `Open Excel`                |  ${CURDIR}/rbfExcelTest.xls  |      |
        | ${value} | `Write To Cell By Row And Column Header`    |  Sheet1 |  rowheadername  | columnheadername | value |

        """
        print("in base class")
        self.writer.write_to_cell_by_row_and_column_header(sheet_name, row_header, column_header, value, data_type)
	
    def write_to_cell(self, sheet_name, column, row, value, data_type=None):
        """
        *Write data to cell by using the given sheet name and the given cell that defines by column and row.*

        If `Data Type` is not provided, `rbfExcel` will introspect data type from given `value` to define cell type

        *Arguments*
        
        ``sheet_name`` (String) : The selected sheet that the cell will be modified from.
        
        ``column`` (int) : The column integer value that the cell value will be returned from.
        
        ``row`` (int) : The row integer value that will be used to modify the cell.
        
        ``value`` (String|number|datetime|boolean) : Raw value or string value then using DataType to decide data type to write
        
        ``data_type`` (String) : Available options: DATE , TIME , DATE_TIME , TEXT , NUMBER , BOOL
        
        *Examples*

        | `Open Excel`            |  ${CURDIR}/rbfExcelTest.xls  |     |     |              |       |
        | `Write To Cell`         |  Sheet1                                        |  0  |  0  |  34          |       |
        | `Write To Cell`         |  Sheet1                                        |  1  |  1  |  2018-03-29  | DATE  |
        | `Write To Cell`         |  Sheet1                                        |  2  |  2  |  YES         | BOOL  |

        """
        self.writer.write_to_cell(sheet_name, column, row, value, data_type)


    def save_excel(self):
        """
        *Saves the Excel file that was opened to write before.*

        *Examples*
        
        | `Open Excel To Write`   |  ${CURDIR}/rbfExcelTest.xls  |                  |
        | `Write To Cell`         |  Sheet1                                        |  0  |  0  |  34  |
        | `Save Excel`            |                                                    |                  |

        """
        self.writer.save_excel()

    def create_sheet(self, sheet_name):
        """
        *Creates and appends new Excel worksheet using the new sheet name to the current workbook.*

        *Arguments*
        
        ``sheet_name`` (String) : The name of the new sheet added to the workbook.

        
        *Examples*

        | `Open Excel`           |  ${CURDIR}/rbfExcelTest.xls  |
        | `Create Sheet`         |  NewSheet                                          |

        """
        self.writer.create_sheet(sheet_name)
