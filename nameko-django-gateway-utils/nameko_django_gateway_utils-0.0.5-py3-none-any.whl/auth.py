from .libs.convertions import Dict2Class


class UserObject(Dict2Class):

    def __init__(self, user_info_dict=None):
        super().__init__(user_info_dict)

        if user_info_dict:
            self.is_authenticated = True
        else:
            self.is_authenticated = False
