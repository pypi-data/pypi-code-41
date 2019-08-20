from django.db import models

class Template(models.Model):

	name = models.CharField('Name', max_length=255)
	code = models.TextField('Code')

	def __str__(self):
		return self.name