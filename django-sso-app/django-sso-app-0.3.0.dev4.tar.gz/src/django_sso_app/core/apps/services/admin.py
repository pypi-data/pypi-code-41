import base64
from io import BytesIO

from PIL import Image
from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Service, Subscription, TOS


class ServiceAdminForm(forms.ModelForm):
    picture = forms.ImageField(required=False)

    def clean_picture(self):
        picture_file = self.cleaned_data['picture']

        if picture_file is not None and type(picture_file) == InMemoryUploadedFile:
            picture_bin = picture_file.file.read()
            picture_image = Image.open(BytesIO(picture_bin))
            picture_format = picture_image.format

            if picture_format not in ('PNG', 'JPEG'):
                raise forms.ValidationError('Image must be either PNG or JPEG')

            picture_image.thumbnail((100, 100), Image.ANTIALIAS)
            
            image = BytesIO()
            picture_image.save(image, format=picture_format)

            return "data:image/{};base64,".format(picture_format.lower()) + base64.b64encode(image.getvalue()).decode('utf-8')
        else:
            return None


class TOSInline(admin.TabularInline):
    model = TOS


class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    inlines = [
        TOSInline,
    ]


admin.site.register(Service, ServiceAdmin)
admin.site.register(Subscription)
