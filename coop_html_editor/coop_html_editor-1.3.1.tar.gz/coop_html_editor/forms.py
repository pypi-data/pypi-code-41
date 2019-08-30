# -*- coding: utf-8 -*-
"""form base classes for integration"""

from django.utils.encoding import smart_text

import floppyforms.__future__ as forms

from .settings import get_field_prefix
from .widgets import get_inline_html_widget


class InlineHtmlForm(forms.Form):
    """Base class for form with inline html editor"""
    is_inline_editable = True

    def __init__(self, model_class, lookup, field_name, data=None, field_value=None, *args, **kwargs):
        super(InlineHtmlForm, self).__init__(data, *args, **kwargs)
        
        self._model_class = model_class
        self._lookup = lookup
        self._field_name = field_name
        
        model_name = "__".join(
            (model_class.__module__.split('.')[-2], model_class.__name__)
        )
        
        lookup_str = "__".join([key + "__" + u'{0}'.format(value).strip('"\'') for (key, value) in lookup.items()])
        
        self._form_field = "__".join(
            (get_field_prefix(), model_name, lookup_str, field_name)
        )
        
        self.fields[self._form_field] = forms.CharField(
            required=False,
            initial=field_value,
            widget=self.get_inline_html_widget()
        )

    def get_inline_html_widget(self):
        return get_inline_html_widget()

    def save(self):
        """save associated object"""
        value = smart_text(self.cleaned_data[self._form_field])
        obj = self._model_class.objects.get_or_create(**self._lookup)[0]
        setattr(obj, self._field_name, value)
        obj.save()
    
    def as_is(self):
        """return html without parent tag"""
        return self._html_output(
            normal_row=u'%(field)s',
            error_row=u'%s',
            row_ender='',
            help_text_html=u'',
            errors_on_separate_row=True
        )
