from django import forms
from .models import AbstractSolarluxUser


class UserAddWithoutPasswordForm(forms.ModelForm):
    class Meta:
        model = AbstractSolarluxUser
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user
