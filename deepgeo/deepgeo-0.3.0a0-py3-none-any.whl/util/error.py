class SupportFormatError(Exception):
    def _init_(self, format_):
        self.value = "SupportFormatError: Format '"+format_+"' is not supported."
    
    def _str_(self):
        return self.value

class ImageLoadError(Exception):
    def _init_(self, image_name):
        self.value = "ImageLoadError: Unable to retrieve '"+image_name+"' file."
    
    def _str_(self):
        return self.value

class FontLoadError(Exception):
    def _init_(self, font_name):
        self.value = "FontLoadError: The font file does not exist. (/fonts/"+font_name+".ttf)"
    
    def _str_(self):
        return self.value

class FontUnitError(Exception):
    def _init_(self, font_size):
        self.value = "FontUnitError: Unit of font size not supported. ("+font_size+")"
    
    def _str_(self):
        return self.value

class KeyNotNoneError(Exception):
    def _init_(self):
        self.value = "KeyError: Key value must not be None."

    def _str_(self):
        return self.value

class KeyNotEmptyError(Exception):
    def _init_(self):
        self.value = "KeyError: Key value must not be empty."

    def _str_(self):
        return self.value

class KeyNoDataError(Exception):
    def _init_(self):
        self.value = "KeyError: No data corresponding to the key value."

    def _str_(self):
        return self.value

class NoSuchClassInContribError(Exception):
    def _init_(self):
        self.value = "NoSuchClassInContribError: No data corresponding to the key value."

    def _str_(self):
        return self.value