from allauth.account.forms import SignupForm as allauth_SignupForm
from django import forms
from django.utils.translation import ugettext_lazy as _

"""
ROLE_CHOICES = (
    (-1, 'Staff'),
    (0, 'Cityzen'),
    (1, 'Institutional'),
    (2, 'Professionist'),
    (4, 'Company'),
    (6, 'Istitutional Partition Item'),
    (7, 'App'),
)

PROFILE_FIELDS = (
                  'email',
                  'password',
                  'role',
                  'first_name', 'last_name',
                  'description', 'picture', 'birthdate',
                  'latitude', 'longitude',
                  'country',
                  'address'
                  )
"""


class SignupForm(allauth_SignupForm):
    # role = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
    #                                  choices=ROLE_CHOICES)
        
    first_name = forms.CharField(
        label=_('First name'),
        widget=forms.TextInput(
        attrs={'type': 'text',
               'placeholder': _('First name')}))

    last_name = forms.CharField(
        label=_('Last name'),
        widget=forms.TextInput(
        attrs={'type': 'text',
               'placeholder': _('Last name')}))

    description = forms.CharField(
        label=_('Description'),
        widget=forms.Textarea(
        attrs={'placeholder': _('Description')}))

    picture = forms.ImageField(
        label=_('Picture'),
    )

    birthdate = forms.DateField(
        label=_('Birthdate'),
        widget=forms.TextInput(
        attrs={ 'type': 'date',
                'placeholder': _('Birthdate')}))

    latitude = forms.CharField(
        label=_('Latitude'),
        widget=forms.TextInput(
        attrs={ 'type': 'text',
                'placeholder': _('Latitude')}))

    longitude = forms.CharField(
        label=_('Longitude'),
        widget=forms.TextInput(
        attrs={ 'type': 'text',
                'placeholder': _('Longitude')}))
        
    country = forms.CharField(
        label=_('Country'),
        widget=forms.TextInput(
        attrs={ 'type': 'text',
                'placeholder': _('Country')}))

    address = forms.CharField(
        label=_('Address'),
        widget=forms.Textarea(
        attrs={'placeholder': _('Address')}))

    language = forms.CharField(
        label=_('Language'),
        widget=forms.TextInput(
        attrs={'type': 'text',
             'placeholder': _('Language')}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.fields['birthdate'].required = False
        self.fields['picture'].required = False
        self.fields['description'].required = False
        self.fields['language'].required = False

    def get_cleaned_data(self):
        return self.clean()
