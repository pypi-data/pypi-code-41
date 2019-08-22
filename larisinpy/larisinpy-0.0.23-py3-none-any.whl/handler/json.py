#%%
import logging

#%%
logging.basicConfig(format='%(asctime)s - %(message)s', 
                   datefmt='%Y-%m-%dT%H:%M:%SZ')
#%%
class JsonUtils(object):

    def __init__(self):
        pass

    def ErrorHandler(self, json_file, property, data_type, annotation=None):

        def errorNotFound(data_type, annotation, property):
            
            logging.error("{} is not found.".format(str(annotation), property))
            if data_type == "int":
                return 0
            elif data_type == "str":
                return ""

            return None

        def convertValue(data_type, value):

            if data_type == "int":
                value = int(value)
            elif data_type == "str":
                value = str(value)

            return value

        # Nested property using "."
        if property.find(".") == -1:

            # When "." not found
            try:
                value = json_file[property]

                return convertValue(data_type, value)
            except:
                return errorNotFound(data_type, str(annotation), property)

        else:
            # When "." is found
            property = property.split(".")
            try:
                value = json_file[property[0]][property[1]]
                
                return convertValue(data_type, value)
            except:
                return errorNotFound(data_type, annotation, property)
        
        return value