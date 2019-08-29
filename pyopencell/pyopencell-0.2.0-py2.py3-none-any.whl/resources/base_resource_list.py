class BaseResourceList:
    _name = ""
    _url_path = ""
    items_resource_class = None
    items_per_page = 10

    def __init__(self, kwargs_list):
        for base_resource in kwargs_list:
            for kwarg, value in base_resource.items():
                setattr(self, kwarg, value)
