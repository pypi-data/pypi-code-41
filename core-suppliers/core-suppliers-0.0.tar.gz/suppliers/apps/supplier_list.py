#from django_pyforms.model_admin.editform_admin import EditFormAdmin
#from pyforms_web.controls.ControlQueryList import ControlQueryList
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget
from pyforms_web.widgets.django import ModelViewFormWidget
from pyforms.basewidget import segment
from pyforms.basewidget import no_columns

from django.conf import settings
from confapp            import conf                           

from suppliers.models    import Supplier
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlText

from suppliers.models    import Category

class SupplierFormAdmin(ModelFormWidget):

    MODEL = Supplier  #model to manage
    TITLE = 'Suppliers'  #title of the application

    #formset of the edit form
    FIELDSETS = [
        (
            segment(
                ('supplier_name','supplier_nif'),
                ('supplier_mail','supplier_contact'),
                ('country','supplier_phone'),
            ),
            segment(
                'supplier_keywords',
                'supplier_discounts',
                'category',
                ('_category','_addcategory_btn')
            )
        )
    ]

    AUTHORIZED_GROUPS = ['superuser', settings.APP_PROFILE_ORDERS]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._addcategory_btn = ControlButton(
            '<i class="icon plus" ></i>Category',
            css='basic mini',
            field_css='five wide',
            label_visible=False,
            default=self.__create_new_category,
        )
        self._category = ControlText(
            'New category', 
            field_css='eleven wide',
            label_visible=False,
            visible=False
        )


    def __create_new_category(self):
        
        if self._category.visible is False:
            self._category.show()
            self._addcategory_btn.label = '<i class="icon file outline" ></i>Create'
            self._addcategory_btn.css = 'blue'
        else:
            self._category.hide()
            self._addcategory_btn.label = '<i class="icon plus" ></i>Category'
            self._addcategory_btn.css = 'basic mini'
            if self._category.value:
                Category(catproduct_name=self._category.value).save()




class SupplierAdminWidget(ModelAdminWidget):
    

    UID   = 'finance-Supplier-app'.lower()
    MODEL = Supplier
    
    TITLE = 'Suppliers'

    #fields to be used in the search
    SEARCH_FIELDS  = ['supplier_name__icontains']
    EDITFORM_CLASS = SupplierFormAdmin    #edit form class
    
    ########################################################
    #### ORQUESTRA CONFIGURATION ###########################
    ########################################################
    LAYOUT_POSITION      = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU       = 'left'
    ORQUESTRA_MENU_ORDER = 0
    ORQUESTRA_MENU_ICON  = 'truck'
    #AUTHORIZED_GROUPS   = ['superuser'] #groups with authorization to visualize the app
    ########################################################
    
    
   
    
    