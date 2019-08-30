# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class ConfirmForm(forms.Form):

    def is_confirmed(self):
        return 'confirm' in self.data

    def is_cancelled(self):
        return 'cancel' in self.data

