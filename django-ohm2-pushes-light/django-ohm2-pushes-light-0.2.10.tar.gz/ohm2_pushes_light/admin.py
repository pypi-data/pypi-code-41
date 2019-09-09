from django.contrib import admin
from . import models as ohm2_pushes_light_models


@admin.register(ohm2_pushes_light_models.Message)
class Message(admin.ModelAdmin):
	
	exclude = (
		'identity',
		'last_update',
		'code',
	)

	

	def save_model(self, request, obj, form, change):
		obj = form.instance
		if not change or len(obj.identity) == 0:
			obj.identity = h_utils.db_unique_random(type(obj))
		
		super(type(self), self).save_model(request, obj, form, change)

