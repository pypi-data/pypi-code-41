from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import EmailUser


class EmailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = EmailUser
        fields = ('email', 'name')


class EmailUserChangeForm(UserChangeForm):
    class Meta:
        model = EmailUser
        fields = ('email', 'name')