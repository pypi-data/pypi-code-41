from django.db import models

class Communication(models.Model):

	name 	= models.CharField(max_length=200)
	html 	= models.TextField('HTML')
	sent_on = models.DateTimeField('Date', blank=True, null=True,)
	sent_to = models.ForeignKey('MailingList', on_delete=models.CASCADE)

	messages = models.ManyToManyField('Message')

	def __str__(self):
		return self.name