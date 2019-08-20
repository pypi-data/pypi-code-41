from django.db import models

class Subject(models.Model):

	active = models.BooleanField('Active')
	name   = models.CharField(max_length=255)
	text   = models.TextField('Text', blank=True, null=True,)
	order  = models.IntegerField('Order')

	class Meta:
		ordering = ('-active', 'order', 'name')
	
	def __str__(self):
		return self.name