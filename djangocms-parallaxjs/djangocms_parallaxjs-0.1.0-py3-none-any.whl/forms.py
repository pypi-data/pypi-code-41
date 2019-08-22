from django import forms
from djangocms_style.models import Style

from djangocms_parallaxjs.models import ParallaxWindow


class ParallaxWindowForm(forms.ModelForm):

    class Meta:
        model = ParallaxWindow
        fields = '__all__'
