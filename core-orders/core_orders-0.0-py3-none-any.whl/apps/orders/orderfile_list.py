from pyforms.basewidget import no_columns
from orders.models    import OrderFile
from pyforms_web.widgets.django import ModelFormWidget
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.web.middleware import PyFormsMiddleware

class OrderFileEditForm(ModelFormWidget):
    MODEL = OrderFile
    TITLE = 'Order file'
    FIELDSETS = ['file']

    
    def update_object_fields(self, obj):
        obj.createdby = PyFormsMiddleware.user()
        return super().update_object_fields(obj)
        
class OrderFileInline(ModelAdminWidget):

    MODEL = OrderFile
    TITLE = 'Order file'
    LIST_DISPLAY = ['file', 'createdon', 'createdby']

    EDITFORM_CLASS = OrderFileEditForm