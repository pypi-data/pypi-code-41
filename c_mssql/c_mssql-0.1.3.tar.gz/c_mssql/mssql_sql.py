import binascii
from c_sql import Sql_Query



class Sql_Mssql(Sql_Query):
    # Python二进制转SQLbinary
    def binary_to_str(self,binary):
        if binary is not None and binary != 0:
            binarystr = str('0x'.encode('ascii') + binascii.hexlify(binary))
            binarystr = binarystr[2:len(binarystr)-1]
        else:
            binarystr = "0"
        return binarystr
    

    def pymssql_type_to_db_type(self,pymssql_type):
        dict_db_type={1:"string",2:"binary",3:"float",4:"datetime",9:"expression"}
        if pymssql_type in dict_db_type:
            db_type=dict_db_type[pymssql_type]
        else:
            db_type="string"
        return db_type

    def get_colums_value_str(self, column_value, column_type):
        if str(column_value).upper() == "NULL" or column_value is None:
            column_value = f"Null"
        elif column_type in ("string", "text", "datetime", "date", "time"):
            if column_type in ["string", "text"] and "'" in str(column_value):
                column_value = str(str(column_value).rstrip()
                                   ).replace("'", "''")
            elif column_type == "datetime" and len(str(column_value)) > 23:
                column_value = f"""{str(column_value)[0:23]}"""
            column_value = f"""'{column_value}'"""
        elif column_type in ("binary", "bolean", "float", "int", "expression"):
            if column_type == "binary":
                column_value = f"{self.binary_to_str(column_value)}"
            elif column_type == "bolean":
                if column_value == False or str(column_value).upper() == 'FALSE':
                    column_value = "0"
                elif column_type == True or str(column_value).upper() == "TRUE":
                    column_value = "1"
            else:
                column_value = str(column_value)
        return column_value


