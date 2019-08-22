#%%
import logging

#%%
logging.basicConfig(format='%(asctime)s - %(message)s', 
                   datefmt='%d-%b-%yT%H:%M:%SZ')
#%%
class JsonUtils(object):

    def __init__(self):
        pass

    def ErrorHandler(self, json_file, property, data_type, annotation=None):

        def errorNotFound(data_type, annotation):
            
            logging.error("{} is not found.".format(annotation))
            if data_type == "int":
                return 0
            elif data_type == "str":
                return ""

            return None

        # Nested property using "."
        if property.find(".") == -1:

            # When "." not found
            try:
                value = json_file[property]
                if data_type == "int":
                    value = int(value)
                elif data_type == "str":
                    value = str(value)
            except:
                return errorNotFound(data_type, annotation)

        else:
            # When "." is found
            property = property.split(".")
            try:
                value = json_file[property[0]][property[1]]
                if data_type == "int":
                    value = int(value)
                elif data_type == "str":
                    value = str(value)
            except:
                return errorNotFound(data_type, annotation)
        
        return value