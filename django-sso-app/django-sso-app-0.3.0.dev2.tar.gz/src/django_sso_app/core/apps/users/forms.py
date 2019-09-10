import logging
from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.forms import EmailField

from allauth.utils import email_address_exists
from allauth.account.models import EmailAddress

logger = logging.getLogger('users')
User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    email = EmailField(required=True, label='Email')

    class Meta(forms.UserCreationForm.Meta):
        model = User
        fields = ("username", "email",)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email_address_exists(email):
            raise ValidationError(self.error_messages["duplicate_email"])
        else:
            return email

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        if settings.DJANGO_SSO_BACKEND_ENABLED:
            # removing unnecessary password fields
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            # If one field gets autocompleted but not the other, our 'neither
            # password or both password' validation will be triggered.
            self.fields['password1'].widget.attrs['autocomplete'] = 'off'
            self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit)

        if not commit:
            new_email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=True,
                primary=True
            )
            logger.info('NEW USER EMAIL CREATED FROM ADMIN: {}'.format(new_email_address))

        return user
