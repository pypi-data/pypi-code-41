from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import EmailModel


""" Start EmailForm here. """
# start emailform here.
class EmailForm(ModelForm):

    class Meta:
        model = EmailModel

        fields = ['from_email', 'phone_number', 'full_name', 'subject', 'content' ]

        labels = {'from_email': 'Company"s email',
                  'phone_number' : 'Your phone',
                  'full_name' : 'Full Name',
                  'subject' : 'Subject',
                  'content' : 'Message' }

        widgets = {'from_email' :  forms.EmailInput(attrs={"type": "email", "class": "form-control rounded-0", "placeholder": "Email address"}),
                   'phone_number': forms.NumberInput(attrs={"type": "number", "class": "form-control rounded-0", "placeholder": "Phone number"}),
                   'full_name': forms.TextInput(attrs={"type":"text", "class": "form-control rounded-0", "placeholder": "Full name"}),
                   'subject': forms.TextInput(attrs={"type":"text", "class": "form-control rounded-0", "placeholder": "subject"}),
                   'content': forms.Textarea(attrs={"type": "text", "class": "form-control rounded-0", "placeholder": " Your message", "rows": "4"}) }

    # djangoform field level validation.
    def clean_phone_number(self, *args, **kwargs):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number == 1234567890:
            raise forms.ValidationError("Phone number is invalid.")
        else:
            return phone_number