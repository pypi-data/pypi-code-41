from django import forms

from cuser.forms import AuthenticationForm as CUserAuthenticationForm
from cuser.forms import UserCreationForm as CUserCreationForm
from cuser.forms import UserChangeForm as CUserChangeForm

from .models import User


class EmailUserCreationForm(CUserCreationForm):

    class Meta(CUserCreationForm.Meta):
        model = User
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError("This email address is already taken")


class AuthenticationForm(CUserAuthenticationForm):
    class Meta:
        model = User
        fields = []


class UserCreationForm(CUserCreationForm):
    class Meta:
        model = User
        fields = '__all__'


class UserChangeForm(CUserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
