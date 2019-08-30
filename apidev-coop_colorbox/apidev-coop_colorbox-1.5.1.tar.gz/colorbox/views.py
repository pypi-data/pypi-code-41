# -*- coding: utf-8 -*-
"""some reusable views: inherit from them"""

from __future__ import unicode_literals

from django.views.generic.edit import FormView

from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from .decorators import popup_redirect
from .forms import ConfirmForm
from .http import HttpResponseClosePopup


class PopupRedirectView(FormView):
    """Base class for popup form : redirect if success"""
    template_name = "colorbox/popup_form_base.html"
    form_url = ""
    title = ""
    form_class = None
    success_url = ""
    staff_only = False
    
    def get_context_data(self, **kwargs):
        """update template context"""
        context = super(PopupRedirectView, self).get_context_data(**kwargs)
        context['form_url'] = self.get_form_url()
        context['title'] = self.get_title()
        return context

    def get_form_url(self):
        """get url for submitting the form"""
        return self.form_url
    
    def get_title(self):
        """get title"""
        return self.title
    
    @method_decorator(popup_redirect)
    def dispatch(self, *args, **kwargs):
        """Manage permissions and use decorator for redirection"""
        if self.staff_only:
            if not self.request.user.is_staff:
                raise PermissionDenied
        return super(PopupRedirectView, self).dispatch(*args, **kwargs)


class AdminPopupRedirectView(PopupRedirectView):
    """Popup for admin"""
    staff_only = True


class ConfirmFormView(PopupRedirectView):
    form_class = ConfirmForm

    def form_confirmed(self):
        """
        overrides this method to perform action to be confirmed
        returns None or HttpResponse : If None redirects to redirect_url
        """
        return None

    def form_cancelled(self):
        """
        overrides this method to perform action when cancelled
        returns None or HttpResponse : If None just close the popup
        """
        return None

    def form_valid(self, form):
        """on form valid"""

        if form.is_confirmed():
            response = self.form_confirmed()
            if response:
                return response
            else:
                return super(ConfirmFormView, self).form_valid(form)

        elif form.is_cancelled():
            response = self.form_cancelled()
            if response:
                return response

        return HttpResponseClosePopup()



