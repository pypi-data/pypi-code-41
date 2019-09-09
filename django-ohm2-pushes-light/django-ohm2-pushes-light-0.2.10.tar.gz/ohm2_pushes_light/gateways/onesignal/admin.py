from django.contrib import admin
from . import models as onesignal_models


@admin.register(onesignal_models.Device)
class Device(admin.ModelAdmin):
	
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