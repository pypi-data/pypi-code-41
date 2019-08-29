from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from .models import UserModel


""" start registration form here. """
# Registration form.
class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model  = User

        fields = [
            'username', 'email',
            'password1', 'password2'
        ]

        labels = {
            'username' : 'Username',
            'email' : 'Email',
            'password1': 'Password',
            'password2': 'Password confirmation'
        }

        widgets = { 
            'email': forms.EmailInput(attrs={"type":"email", "class":"form-control"}),
            'username': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control'})
        }


""" start signin form here. """
# signin form.
class SigninForm(AuthenticationForm):

    class Meta:
        model  = User

        fields = [
            'username', 'password',
        ]

        labels = {
            'username' : 'Username',
            'password': 'Password',
        }

        widgets = { 
            'username': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control'})
        }


""" start edit profile form here. """
# EditProfileForm form.
class EditProfileForm(UserChangeForm):

    class Meta:
        model  = User

        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password'
        ]

        labels = {
            'username': 'Username',
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email',
            'password': 'Password'
        }

        widgets = { 
            'username': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0'}),
            'first_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0'}),
            'last_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0'}),
            'email': forms.EmailInput(attrs={'type': 'email', 'class': 'form-control rounded-0'})
        }


""" start userform here. """
# userform.
class UserForm(ModelForm):
    
    class Meta:
        model = UserModel

        fields = ['image', 'address', 'phone', 'website']

        labels = {
            'image': 'Profile image',
            'address': 'Address',
            'phone': 'Phone',
            'website': 'Website',
        }

        widgets = { 
            'image': forms.ClearableFileInput(attrs={}),
            'address': forms.TextInput(attrs={'type': 'text', 'class': 'form-control rounded-0'}),
            'phone': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control rounded-0'}),
            'website': forms.URLInput(attrs={'type': 'url', 'class': 'form-control rounded-0'})
        }