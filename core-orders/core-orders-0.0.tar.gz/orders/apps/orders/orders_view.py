from .orders_form import OrderEditFormWidget


class Order(OrderEditFormWidget):

    UID = 'view-order'

    def __init__(self, obj=None):
        super().__init__(pk=obj)
